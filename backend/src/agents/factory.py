"""
Shared factory for creating LangGraph ReAct agents.

Each demo calls create_demo_agent() with its own tools and prompt.
The agent is a standard LangGraph ReAct agent — no custom middleware,
no complex state machines. The system prompt is the control surface.
"""

from __future__ import annotations

import os
from typing import Any, Type

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent


def create_demo_agent(
    *,
    demo_name: str,
    tools: list,
    state_schema: Type,
    prompt: str,
    checkpointer: AsyncSqliteSaver,
) -> Any:
    """
    Create a LangGraph ReAct agent for a demo.

    Parameters
    ----------
    demo_name   : Human-readable name (used in LangSmith traces)
    tools       : LangChain tool list (from MCP adapter)
    state_schema: TypedDict subclass with at least `messages` and `canvas`
    prompt      : System prompt string
    checkpointer: Shared async SQLite checkpointer (one per app)

    Returns
    -------
    CompiledGraph — the runnable LangGraph agent
    """
    model = ChatOpenAI(
        model=os.getenv("AGENT_MODEL", "gpt-4o"),
        streaming=True,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=state_schema,
        checkpointer=checkpointer,
        name=f"{demo_name}_agent",
        # System prompt injected on every turn
        prompt=prompt,
    )

    return agent
