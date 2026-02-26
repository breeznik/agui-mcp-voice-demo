"""
End-to-end test: verify each agent can receive messages and call tools.
Run from backend dir: poetry run python test_e2e.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Load .env from project root
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.agents.registry import AgentRegistry
from src.agents.runner import stream_agent


async def test_agent(registry, demo_name, user_message, expect_tool=None):
    """Send a message to an agent and verify tool calls + text response."""
    agent = registry.get(demo_name)
    assert agent is not None, f"Agent {demo_name} not found"

    thread_id = f"test-{demo_name}-{os.urandom(4).hex()}"
    run_id = f"run-{os.urandom(4).hex()}"

    body = {
        "threadId": thread_id,
        "runId": run_id,
        "messages": [
            {"id": f"msg-{os.urandom(4).hex()}", "role": "user", "content": user_message}
        ],
        "state": {},
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }

    events = []
    tool_calls = []
    text_content = ""
    run_started = False
    run_finished = False
    custom_events = []

    async for chunk in stream_agent(agent, body, demo_name=demo_name, accept="text/event-stream"):
        # Parse SSE events from chunk
        for line in chunk.split("\n"):
            if line.startswith("data: "):
                try:
                    event = json.loads(line[6:])
                    events.append(event)
                    etype = event.get("type")

                    if etype == "RUN_STARTED":
                        run_started = True
                    elif etype == "RUN_FINISHED":
                        run_finished = True
                    elif etype == "TEXT_MESSAGE_CONTENT":
                        text_content += event.get("delta", "")
                    elif etype == "TOOL_CALL_START":
                        tool_calls.append(event.get("toolCallName", ""))
                    elif etype == "CUSTOM":
                        custom_events.append(event.get("name", ""))
                    elif etype == "RUN_ERROR":
                        print(f"  ERROR: {event}")
                except json.JSONDecodeError:
                    pass

    print(f"\n{'='*60}")
    print(f"DEMO: {demo_name}")
    print(f"INPUT: {user_message}")
    print(f"{'='*60}")
    print(f"  Run started: {run_started}")
    print(f"  Run finished: {run_finished}")
    print(f"  Events: {len(events)}")
    print(f"  Tool calls: {tool_calls}")
    print(f"  Custom events: {custom_events}")
    # Safely print text (Windows console may choke on emoji)
    safe_text = text_content[:200].encode("ascii", errors="replace").decode("ascii")
    print(f"  Text response: {safe_text}...")

    assert run_started, f"{demo_name}: RUN_STARTED not received"
    assert run_finished, f"{demo_name}: RUN_FINISHED not received"
    assert text_content, f"{demo_name}: No text response received"

    if expect_tool:
        # expect_tool can be a single name or pipe-separated alternatives
        expected = expect_tool.split("|")
        matched = [e for e in expected if e in tool_calls]
        assert matched, \
            f"{demo_name}: Expected one of {expected} in {tool_calls}"
        print(f"  TOOL CHECK PASSED: '{matched[0]}' was called")

    print(f"  PASSED")
    return True


async def main():
    print("Starting all agents...")
    registry = AgentRegistry()
    await registry.start_all()
    print("All agents ready.\n")

    results = {}

    # Test each agent with a message that should trigger tool use
    test_cases = [
        ("shopping", "I am looking for a shaver under $50", "search_products"),
        ("travel", "Search for flights from New York to London on 2026-03-15 for 2 passengers", "search_flights"),
        ("trivia", "What categories are available for trivia?", "get_categories"),
        ("chef", "Find me vegan Italian recipes", "search_recipes"),
        ("support", "Check the status of order ORD-A1B2C3", "lookup_order|get_tracking_status"),
    ]

    for demo, message, expected_tool in test_cases:
        try:
            ok = await test_agent(registry, demo, message, expect_tool=expected_tool)
            results[demo] = "PASS" if ok else "FAIL"
        except Exception as e:
            print(f"\n  FAILED: {demo}: {e}")
            results[demo] = f"FAIL: {e}"

    await registry.stop_all()

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for demo, result in results.items():
        print(f"  {demo}: {result}")

    all_pass = all(r == "PASS" for r in results.values())
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    asyncio.run(main())
