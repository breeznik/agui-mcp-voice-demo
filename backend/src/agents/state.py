"""
Shared state schema for all demo agents.

Every demo uses the same DemoState. The `canvas` dict is the agent's
working memory — it can write anything it needs to track progress.
The `client_events` list is replaced each turn and carries typed events
for the frontend's generative UI system.
"""

from __future__ import annotations

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import add_messages
from langgraph.managed.is_last_step import RemainingStepsManager


def _replace(_, b):
    """Reducer: always use the new value (replace, not merge)."""
    return b


def _merge(a, b):
    """Reducer: shallow-merge dicts."""
    return {**a, **b}


class DemoState(TypedDict):
    # Conversation history — append-only via add_messages reducer
    messages: Annotated[list, add_messages]

    # Agent working memory — merged on every update
    # The agent writes notes, results, and progress here.
    canvas: Annotated[dict, _merge]

    # Frontend events emitted this turn — replaced each turn to prevent
    # stale events from leaking into the next turn.
    client_events: Annotated[list, _replace]

    # LangGraph managed value — tracks remaining agent steps
    remaining_steps: Annotated[int, RemainingStepsManager]
