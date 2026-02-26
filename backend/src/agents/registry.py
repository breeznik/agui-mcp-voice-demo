"""
AgentRegistry — starts all 5 MCP servers as subprocesses and
initializes a LangGraph agent for each demo.

Event emission fix
------------------
MCP tools run in stdio subprocesses. adispatch_custom_event() requires an
active LangChain callback context, which only exists in the *parent* FastAPI
process. Calling it inside the subprocess always fails silently.

The fix: _wrap_tool() wraps each LangChain tool object (which DOES run in the
parent process) to emit `agent_activity` before the MCP call and `render_card`
after the result returns. MCP server tool functions are kept as pure data
functions — no emit calls.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import aiosqlite
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.runnables.config import var_child_runnable_config
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.agents.factory import create_demo_agent

logger = logging.getLogger(__name__)

_MCP_SERVERS_DIR = Path(__file__).parent.parent / "mcp_servers"

_DEMO_SERVERS = {
    "travel":   _MCP_SERVERS_DIR / "travel_server.py",
    "trivia":   _MCP_SERVERS_DIR / "trivia_server.py",
    "shopping": _MCP_SERVERS_DIR / "shopping_server.py",
    "chef":     _MCP_SERVERS_DIR / "chef_server.py",
    "support":  _MCP_SERVERS_DIR / "support_server.py",
}

# ── Tool → card_type mapping ──────────────────────────────────────────────────
# None means the tool result doesn't need a dedicated card (text only).

_TOOL_CARDS: dict[str, str | None] = {
    # Travel
    "search_flights":         "flight_card",
    "get_weather":            "weather_card",
    "search_hotels":          "hotel_card",
    "get_place_info":         None,
    "save_to_itinerary":      "itinerary_card",
    # Trivia
    "get_categories":         "category_card",
    "get_question":           "question_card",
    "check_answer":           "answer_card",
    "update_score":           None,
    "end_game":               "scoreboard_card",
    # Shopping
    "search_products":        "product_card",
    "get_product_details":    "product_card",
    "add_to_cart":            "cart_card",
    "remove_from_cart":       "cart_card",
    "view_cart":              "cart_card",
    "checkout":               "checkout_card",
    # Chef
    "search_recipes":         "recipe_card",
    "create_recipe":          "recipe_card",
    "get_nutritional_info":   "nutrition_card",
    "plan_meals":             "meal_plan_card",
    "generate_shopping_list": "shopping_list_card",
    "save_recipe":            None,
    # Support
    "lookup_order":           "order_card",
    "get_tracking_status":    "order_card",
    "initiate_refund":        "order_card",
    "search_knowledge_base":  "kb_article_card",
    "create_ticket":          "ticket_card",
    "escalate_to_human":      "escalation_card",
}

# ── Tool → activity label ─────────────────────────────────────────────────────

_TOOL_ACTIVITIES: dict[str, tuple[str, str]] = {
    # (title, phase)
    "search_flights":         ("Searching flights",        "search"),
    "get_weather":            ("Checking weather",         "search"),
    "search_hotels":          ("Finding hotels",           "search"),
    "get_place_info":         ("Looking up destination",   "search"),
    "save_to_itinerary":      ("Saving itinerary",         "done"),
    "get_categories":         ("Loading categories",       "search"),
    "get_question":           ("Fetching question",        "search"),
    "check_answer":           ("Checking answer",          "compute"),
    "update_score":           ("Updating score",           "done"),
    "end_game":               ("Tallying final score",     "done"),
    "search_products":        ("Searching products",       "search"),
    "get_product_details":    ("Getting product details",  "search"),
    "add_to_cart":            ("Adding to cart",           "done"),
    "remove_from_cart":       ("Updating cart",            "done"),
    "view_cart":              ("Checking cart",            "search"),
    "checkout":               ("Processing order",         "done"),
    "search_recipes":         ("Searching recipes",        "search"),
    "create_recipe":          ("Composing recipe",         "compute"),
    "get_nutritional_info":   ("Getting nutrition info",   "compute"),
    "plan_meals":             ("Building meal plan",       "compute"),
    "generate_shopping_list": ("Building shopping list",   "compute"),
    "save_recipe":            ("Saving recipe",            "done"),
    "lookup_order":           ("Looking up order",         "search"),
    "get_tracking_status":    ("Getting tracking info",    "search"),
    "initiate_refund":        ("Processing refund",        "compute"),
    "search_knowledge_base":  ("Searching help articles",  "search"),
    "create_ticket":          ("Creating support ticket",  "done"),
    "escalate_to_human":      ("Escalating to human agent","done"),
}


def _extract_tool_data(result: Any) -> dict | None:
    """
    Extract a JSON dict from an MCP tool result.

    MCP tools via langchain-mcp-adapters return:
      - tuple: (content_blocks, artifacts) — content_blocks is a list of
        dicts with {"type": "text", "text": "...json..."}
      - str: raw JSON string
      - dict: already a dict (direct invocation in tests)

    Returns the parsed dict, or None if extraction fails.
    """
    try:
        if isinstance(result, dict):
            return result
        if isinstance(result, str):
            return json.loads(result)
        if isinstance(result, (tuple, list)):
            # (content_blocks, ...) — look for the first text block
            blocks = result[0] if result else []
            if isinstance(blocks, list):
                for block in blocks:
                    if isinstance(block, dict) and block.get("type") == "text":
                        return json.loads(block["text"])
            # Single text block outside a list
            if isinstance(blocks, dict) and blocks.get("type") == "text":
                return json.loads(blocks["text"])
    except (json.JSONDecodeError, IndexError, KeyError, TypeError):
        pass
    return None


def _wrap_tool(tool: Any) -> Any:
    """
    Wrap a LangChain tool to emit AG-UI events from the parent process.

    MCP tools run in stdio subprocesses where adispatch_custom_event() has no
    callback context and silently fails. This wrapper runs in the FastAPI
    process where LangGraph's callback context IS active, so events reach the
    frontend via the AG-UI SSE stream.

    Emits:
      - agent_activity  before the MCP call  (phase + label from _TOOL_ACTIVITIES)
      - render_card     after the result      (card_type from _TOOL_CARDS)
    """
    original_coroutine = tool.coroutine
    tool_name = tool.name

    async def _wrapped(**kwargs: Any) -> Any:
        # ── 0. Inject LangGraph thread_id so MCP servers isolate sessions ─────
        # Without this the agent omits thread_id and all sessions collide on
        # the "default" key, causing check_answer / add_to_cart etc. to fail
        # with "no active session" errors across turns.
        if kwargs.get("thread_id", "default") == "default":
            try:
                config = var_child_runnable_config.get(None)
                if config:
                    lg_tid = config.get("configurable", {}).get("thread_id")
                    if lg_tid:
                        kwargs["thread_id"] = lg_tid
            except Exception:
                pass

        # ── 1. Pre-call activity event ────────────────────────────────────────
        activity = _TOOL_ACTIVITIES.get(tool_name)
        if activity:
            title, phase = activity
            # Build a concise detail string from kwargs (skip thread_id, None values)
            detail_parts = [
                str(v) for k, v in kwargs.items()
                if k != "thread_id" and v is not None and v != "" and v != []
            ]
            detail = " · ".join(detail_parts[:3])[:80]
            try:
                await adispatch_custom_event(
                    "agent_activity",
                    {"title": title, "detail": detail, "phase": phase},
                )
            except Exception:
                pass  # Only fails outside LangGraph context (e.g. direct unit tests)

        # ── 2. Execute tool (MCP subprocess call) ─────────────────────────────
        result = await original_coroutine(**kwargs)

        # ── 3. Post-call card event ───────────────────────────────────────────
        # MCP tools return (content_blocks, artifacts) tuple — extract the
        # JSON text from the first text content block for card rendering.
        card_type = _TOOL_CARDS.get(tool_name)
        if card_type:
            card_data = _extract_tool_data(result)
            if card_data and "error" not in card_data:
                try:
                    await adispatch_custom_event(
                        "render_card",
                        {"card_type": card_type, "data": card_data},
                    )
                except Exception:
                    pass

        return result

    tool.coroutine = _wrapped
    return tool


# ── Registry ──────────────────────────────────────────────────────────────────

class AgentRegistry:
    """Holds all running demo agents and their tool metadata."""

    def __init__(self):
        self._agents: dict[str, object] = {}
        self._tools_meta: dict[str, list[dict]] = {}
        self._mcp_clients: dict[str, MultiServerMCPClient] = {}
        self._db_conn = None
        self._checkpointer = None

    async def start_all(self) -> None:
        """Start MCP servers and create agents for all demos."""
        db_path = os.getenv("DB_PATH", "data/checkpoints.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._db_conn = await aiosqlite.connect(db_path)
        self._checkpointer = AsyncSqliteSaver(self._db_conn)
        await self._checkpointer.setup()

        for demo_name, server_script in _DEMO_SERVERS.items():
            await self._start_demo(demo_name, server_script)

    async def _start_demo(self, demo_name: str, server_script: Path) -> None:
        """Start a single MCP server and create its agent (with retry)."""
        logger.info("Starting MCP server for demo: %s", demo_name)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                client = MultiServerMCPClient({
                    demo_name: {
                        "command": "python",
                        "args": [str(server_script)],
                        "transport": "stdio",
                        "env": dict(os.environ),
                    }
                })
                raw_tools = await client.get_tools()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning("MCP server %s failed (attempt %d/%d): %s", demo_name, attempt + 1, max_retries, e)
                    await asyncio.sleep(1)
                else:
                    raise

        # Wrap each tool to emit AG-UI events from the parent process.
        tools = [_wrap_tool(t) for t in raw_tools]

        self._mcp_clients[demo_name] = client

        # Store tool metadata for the /agent/{demo}/tools endpoint
        self._tools_meta[demo_name] = [
            {"name": t.name, "description": t.description or ""}
            for t in tools
        ]

        state_schema, prompt = _load_demo_config(demo_name)

        agent = create_demo_agent(
            demo_name=demo_name,
            tools=tools,
            state_schema=state_schema,
            prompt=prompt,
            checkpointer=self._checkpointer,
        )

        self._agents[demo_name] = agent
        logger.info("Agent ready: %s (%d tools)", demo_name, len(tools))

    async def stop_all(self) -> None:
        """Clean up database connections."""
        if self._db_conn:
            await self._db_conn.close()

    def get(self, demo_name: str):
        """Return the compiled agent for a demo, or None if not found."""
        return self._agents.get(demo_name)

    def get_tools(self, demo_name: str) -> list[dict] | None:
        """Return tool metadata list for a demo, or None if not found."""
        return self._tools_meta.get(demo_name)


def _load_demo_config(demo_name: str) -> tuple:
    """
    Dynamically import state_schema and prompt for a demo.
    Each demo module exports: STATE_SCHEMA and SYSTEM_PROMPT.
    """
    import importlib
    module = importlib.import_module(f"src.agents.{demo_name}.prompts")
    return module.STATE_SCHEMA, module.SYSTEM_PROMPT
