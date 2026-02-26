"""
Converts an incoming AG-UI HTTP request body into LangGraph input
and streams AG-UI events back to the caller.

The ag_ui_langgraph library handles the heavy lifting — this module
is a thin bridge between FastAPI and LangGraph.
"""

from __future__ import annotations

from typing import AsyncIterator, Any

from ag_ui.core import RunAgentInput
from ag_ui_langgraph import LangGraphAgent
from ag_ui_langgraph.endpoint import EventEncoder


def _patch_agent(lg_agent: LangGraphAgent) -> None:
    """
    Monkey-patch a bug in ag_ui_langgraph 0.0.25 where
    set_message_in_progress crashes when messages_in_process[run_id]
    is None (set during message-end cleanup) instead of missing.
    """
    original = lg_agent.set_message_in_progress

    def patched(run_id, data):
        current = lg_agent.messages_in_process.get(run_id)
        if current is None:
            lg_agent.messages_in_process[run_id] = dict(data)
        else:
            original(run_id, data)

    lg_agent.set_message_in_progress = patched


async def stream_agent(
    agent: Any,
    body: dict,
    demo_name: str = "agent",
    accept: str | None = None,
) -> AsyncIterator[str]:
    """
    Parse the AG-UI request body and yield SSE-encoded events from the agent.

    Parameters
    ----------
    agent : Compiled LangGraph graph
    body  : Raw JSON body from the AG-UI HttpAgent POST request
    demo_name : Name for the LangGraphAgent wrapper
    accept : Accept header from request (for EventEncoder)
    """
    run_input = RunAgentInput(**body)

    lg_agent = LangGraphAgent(
        name=f"{demo_name}_agent",
        graph=agent,
    )
    _patch_agent(lg_agent)

    encoder = EventEncoder(accept=accept)

    async for event in lg_agent.run(run_input):
        yield encoder.encode(event)
