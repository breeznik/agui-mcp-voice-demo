"""
AG-UI event helpers for parent-process use.

These functions emit AG-UI custom events via LangChain's callback system.
They require an active LangGraph callback context to work — i.e. they must
be called from within a running LangGraph graph execution.

Usage
-----
These are called from registry.py's _wrap_tool() wrapper, which runs in the
FastAPI parent process where the LangGraph callback context IS active.

Do NOT call these from inside MCP server tool functions — those run in stdio
subprocesses and have no access to the callback context.
"""

from __future__ import annotations


async def emit_card(card_type: str, data: dict) -> None:
    """
    Emit a render_card custom event to the AG-UI stream.

    Parameters
    ----------
    card_type : Key in the frontend ComponentRegistry (e.g. "flight_card")
    data      : Card data dict — matches the card component's expected props
    """
    try:
        from langchain_core.callbacks.manager import adispatch_custom_event
        await adispatch_custom_event(
            "render_card",
            {"card_type": card_type, "data": data},
        )
    except Exception:
        pass  # No-op outside LangGraph context (e.g. unit tests)


async def emit_activity(title: str, detail: str = "", phase: str = "tool") -> None:
    """
    Emit an agent_activity custom event — shown as a reasoning step in the UI.

    Parameters
    ----------
    title  : Short label (e.g. "Searching flights")
    detail : Longer description (e.g. "London → Tokyo")
    phase  : "search" | "compute" | "done" | "tool"
    """
    try:
        from langchain_core.callbacks.manager import adispatch_custom_event
        await adispatch_custom_event(
            "agent_activity",
            {"title": title, "detail": detail, "phase": phase},
        )
    except Exception:
        pass
