"""
Trivia Host MCP Server.

Uses the Open Trivia Database (https://opentdb.com) — free, no API key.

Tools
-----
get_categories   List available trivia categories
get_question     Fetch a question (category + difficulty)
check_answer     Validate the user's answer
update_score     Update session score
end_game         Wrap up with final summary

Resources
---------
trivia://leaderboard   Session leaderboard
"""

from __future__ import annotations

import html
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("trivia-host")

# ── In-memory session state ───────────────────────────────────────────────────

_sessions: dict[str, dict] = {}
# {thread_id: {score, questions_asked, correct, current_question}}

_OPENTDB_BASE = "https://opentdb.com"


def _get_session(thread_id: str) -> dict:
    if thread_id not in _sessions:
        _sessions[thread_id] = {
            "score": 0,
            "questions_asked": 0,
            "correct": 0,
            "current_question": None,
        }
    return _sessions[thread_id]


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_categories() -> dict:
    """
    Get the list of available trivia categories from Open Trivia DB.
    Present these to the user so they can pick a topic.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{_OPENTDB_BASE}/api_category.php")
            resp.raise_for_status()
            data = resp.json()
            categories = [
                {"id": c["id"], "name": c["name"]}
                for c in data.get("trivia_categories", [])
            ]
    except Exception:
        # Fallback list if API is unreachable
        categories = [
            {"id": 9, "name": "General Knowledge"},
            {"id": 17, "name": "Science & Nature"},
            {"id": 21, "name": "Sports"},
            {"id": 23, "name": "History"},
            {"id": 11, "name": "Film"},
            {"id": 12, "name": "Music"},
            {"id": 15, "name": "Video Games"},
            {"id": 22, "name": "Geography"},
        ]

    return {"categories": categories}


@mcp.tool()
async def get_question(
    category_id: int = 9,
    difficulty: str = "medium",
    thread_id: str = "default",
) -> dict:
    """
    Fetch a trivia question from Open Trivia DB.

    Parameters
    ----------
    category_id : Category ID from get_categories() (default 9 = General Knowledge)
    difficulty  : "easy" | "medium" | "hard"
    thread_id   : Session identifier
    """
    session = _get_session(thread_id)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_OPENTDB_BASE}/api.php",
                params={
                    "amount": 1,
                    "category": category_id,
                    "difficulty": difficulty,
                    "type": "multiple",
                    "encode": "url3986",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if data["response_code"] != 0 or not data["results"]:
            return {"error": "Could not fetch a question. Try a different category."}

        raw = data["results"][0]
        # Decode percent-encoded strings from the API
        from urllib.parse import unquote
        question = {
            "question_id": f"q_{session['questions_asked'] + 1}",
            "question": unquote(raw["question"]),
            "category": unquote(raw["category"]),
            "difficulty": raw["difficulty"],
            "correct_answer": unquote(raw["correct_answer"]),
            "all_answers": sorted(
                [unquote(a) for a in raw["incorrect_answers"]] + [unquote(raw["correct_answer"])]
            ),
        }
    except Exception as exc:
        # Fallback question if API is down
        question = {
            "question_id": "q_fallback",
            "question": "What is the capital of France?",
            "category": "Geography",
            "difficulty": "easy",
            "correct_answer": "Paris",
            "all_answers": ["Berlin", "Madrid", "Paris", "Rome"],
        }

    session["current_question"] = question
    session["questions_asked"] += 1

    # Return WITHOUT the correct_answer — the frontend shows it only after check_answer
    return {k: v for k, v in question.items() if k != "correct_answer"}


@mcp.tool()
async def check_answer(
    user_answer: str,
    thread_id: str = "default",
) -> dict:
    """
    Check the user's answer against the current question.

    Parameters
    ----------
    user_answer : The answer the user gave
    thread_id   : Session identifier
    """
    session = _get_session(thread_id)

    if not session.get("current_question"):
        return {"error": "No active question. Call get_question first."}

    q = session["current_question"]
    correct = q["correct_answer"]
    is_correct = user_answer.strip().lower() == correct.strip().lower()

    points = {"easy": 1, "medium": 2, "hard": 3}.get(q.get("difficulty", "medium"), 2)
    if is_correct:
        session["score"] += points
        session["correct"] += 1

    result = {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct,
        "points_earned": points if is_correct else 0,
        "current_score": session["score"],
        "questions_asked": session["questions_asked"],
        "correct_count": session["correct"],
    }

    session["current_question"] = None
    return result


@mcp.tool()
async def update_score(points: int, thread_id: str = "default") -> dict:
    """
    Manually adjust the session score (e.g. for bonus points or penalties).

    Parameters
    ----------
    points    : Points to add (positive) or subtract (negative)
    thread_id : Session identifier
    """
    session = _get_session(thread_id)
    session["score"] = max(0, session["score"] + points)
    return {"score": session["score"]}


@mcp.tool()
async def end_game(thread_id: str = "default") -> dict:
    """
    End the trivia game and return the final score with a performance tier.

    Parameters
    ----------
    thread_id : Session identifier
    """
    session = _get_session(thread_id)

    total = session["questions_asked"]
    correct = session["correct"]
    score = session["score"]
    pct = (correct / total * 100) if total > 0 else 0

    tier = (
        "Trivia Legend" if pct >= 90 else
        "Expert" if pct >= 70 else
        "Intermediate" if pct >= 50 else
        "Beginner"
    )

    result = {
        "final_score": score,
        "questions_asked": total,
        "correct_answers": correct,
        "accuracy_pct": round(pct, 1),
        "performance_tier": tier,
    }

    # Reset session
    _sessions[thread_id] = {
        "score": 0, "questions_asked": 0, "correct": 0, "current_question": None
    }

    return result


# ── Resources ─────────────────────────────────────────────────────────────────

@mcp.resource("trivia://leaderboard")
def leaderboard() -> str:
    """Current session leaderboard."""
    if not _sessions:
        return "No games played yet."
    rows = []
    for tid, s in _sessions.items():
        rows.append(f"- {tid}: {s['score']} pts ({s['correct']}/{s['questions_asked']})")
    return "# Leaderboard\n\n" + "\n".join(rows)


if __name__ == "__main__":
    mcp.run(transport="stdio")
