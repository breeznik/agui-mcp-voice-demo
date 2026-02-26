# agui-mcp-voice-demo

An open-source template demonstrating the full modern agentic stack:

**AG-UI · LangGraph ReAct · MCP · Voice (WebRTC + Streaming TTS) · Generative UI**

Five fully functional demo agents, one MCP server each, all running on a single FastAPI backend. Fork this to build your own agentic application.

---

## What's Inside

| Demo | Agent | MCP Server | Free APIs Used |
|------|-------|------------|----------------|
| **Travel Concierge** | Trip planning assistant | `travel_server` | OpenWeatherMap (optional), Wikipedia |
| **Trivia Host** | Interactive quiz game | `trivia_server` | Open Trivia DB |
| **Shopping Assistant** | Product search + cart | `shopping_server` | Mock catalog |
| **Personal Chef** | Recipe + meal planning | `chef_server` | Mock recipe DB |
| **Customer Support** | Order lookup + tickets | `support_server` | Mock order DB |

All demos work with only `OPENAI_API_KEY` set. No paid third-party APIs required.

---

## Architecture

```
Browser (AG-UI client)
    │  SSE (AG-UI events)
    ▼
FastAPI  ──── LangGraph ReAct agent (one per demo)
                │  LangChain tool calls
                ▼
            MultiServerMCPClient
                │  stdio transport
                ├── travel_server.py   (FastMCP)
                ├── trivia_server.py   (FastMCP)
                ├── shopping_server.py (FastMCP)
                ├── chef_server.py     (FastMCP)
                └── support_server.py  (FastMCP)
```

### Key design choices

- **One `create_react_agent` per demo** — no custom graph, no middleware. System prompt is the only control surface.
- **MCP as the tool layer** — each demo's tools live in a dedicated FastMCP server. The agent connects via stdio subprocess at startup.
- **Generative UI via AG-UI custom events** — tools emit `render_card`, `agent_activity`, and `canvas_update` events that the frontend renders as rich components.
- **State canvas** — each agent writes a `canvas` dict (progress, results, session state) that the frontend mirrors in a live state panel.
- **Voice** — streaming PCM TTS (~400ms TTFA), Whisper STT, WebRTC ephemeral token for OpenAI Realtime API.

---

## Quickstart

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- An OpenAI API key

### 1. Clone and configure

```bash
git clone https://github.com/your-org/agui-mcp-voice-demo
cd agui-mcp-voice-demo

cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 2. Install and run

```bash
cd backend
poetry install
poetry run uvicorn src.app:app --reload --port 8000
```

### 3. Verify

```bash
# Health check
curl http://localhost:8000/health
# → {"status": "ok"}

# List tools for the travel demo
curl http://localhost:8000/agent/travel/tools
# → {"demo": "travel", "tools": [...]}
```

### 4. Run with Docker

```bash
# From the repo root
docker compose up --build
```

---

## API Reference

### Agent endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/agent/{demo}` | AG-UI SSE stream. Body: `RunAgentInput` (threadId + messages). |
| `GET` | `/agent/{demo}/tools` | MCP tool catalog for the frontend sidebar. |

`{demo}` is one of: `travel` · `trivia` · `shopping` · `chef` · `support`

### Voice endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/voice/tts/stream` | Streaming PCM TTS. Body: `{"text": "..."}`. Returns `audio/pcm` at 24kHz 16-bit mono. Headers: `X-Voice-Sample-Rate`, `X-Voice-Channels`, `X-Voice-Bit-Depth`. |
| `POST` | `/api/voice/tts` | Buffered MP3 TTS fallback. Body: `{"text": "..."}`. |
| `POST` | `/api/voice/stt` | Whisper STT. Multipart file upload. Returns `{"transcript": "..."}`. |
| `POST` | `/api/voice/realtime/session` | WebRTC ephemeral token. Body: `{"thread_id": "..."}`. Returns session config for OpenAI Realtime API. |

### Utility

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe. |

---

## AG-UI Events

The backend emits these event types over the SSE stream:

### Standard AG-UI events

```
TEXT_MESSAGE_START / CONTENT / END   — streaming text response
TOOL_CALL_START / ARGS / END         — tool call lifecycle (args streamed as they arrive)
STATE_SNAPSHOT                       — full DemoState snapshot after each turn
```

### Custom events (generative UI)

All custom events arrive as `CUSTOM` events with a `name` field and a `value` payload.

**`render_card`** — display a rich UI card in the chat thread
```json
{
  "type": "render_card",
  "data": {
    "card_type": "flight_card",
    "message_id": "msg_abc123",
    "data": { ... }
  }
}
```

**`agent_activity`** — show a reasoning / progress step
```json
{
  "type": "agent_activity",
  "data": {
    "title": "Searching flights",
    "detail": "London → Tokyo · 2 passengers",
    "phase": "mcp"
  }
}
```

**`canvas_update`** — live update to the state canvas panel
```json
{
  "type": "canvas_update",
  "data": {
    "canvas": { "destination": "Tokyo", "budget": 3000 }
  }
}
```

**`navigate`** — signal the frontend to change route/view
```json
{
  "type": "navigate",
  "data": { "route": "checkout" }
}
```

### Card types per demo

| Demo | card_types |
|------|-----------|
| travel | `flight_card`, `weather_card`, `hotel_card`, `itinerary_card` |
| trivia | `question_card`, `answer_card`, `scoreboard_card`, `category_card` |
| shopping | `product_card`, `cart_card`, `checkout_card` |
| chef | `recipe_card`, `nutrition_card`, `meal_plan_card`, `shopping_list_card` |
| support | `order_card`, `ticket_card`, `kb_article_card`, `escalation_card` |

See [`FRONTEND_BRIEF.md`](FRONTEND_BRIEF.md) for the complete TypeScript interface for every card type.

---

## MCP Servers

Each demo's tools live in a standalone FastMCP server under `backend/src/mcp_servers/`. The servers run as stdio subprocesses started at app startup via `langchain-mcp-adapters`.

### Calling pattern

Tools emit AG-UI events directly via `adispatch_custom_event()` from inside each tool function. This means tool execution automatically drives the frontend UI — no extra coordination needed in the agent logic.

```python
# Pattern used in every MCP server tool
from src.mcp_servers.base import emit_card, emit_activity

async def search_flights(origin: str, destination: str, date: str, passengers: int = 1) -> dict:
    await emit_activity("Searching flights", f"{origin} → {destination}", phase="search")
    results = _mock_flights(origin, destination, date, passengers)
    await emit_card("flight_card", results)
    return results
```

### Adding your own MCP server

1. Copy any server in `backend/src/mcp_servers/` as a starting point.
2. Add it to `AgentRegistry` in `backend/src/agents/registry.py`.
3. Create a `prompts.py` in `backend/src/agents/{your_demo}/`.
4. Add the demo name to `DEMO_NAMES` in `app.py`.

---

## Project Structure

```
agui-mcp-voice-demo/
├── .env.example
├── docker-compose.yml
├── FRONTEND_BRIEF.md          ← Complete spec for a frontend AI
└── backend/
    ├── pyproject.toml
    ├── Dockerfile
    ├── src/
    │   ├── app.py             ← FastAPI entrypoint + all routes
    │   ├── agents/
    │   │   ├── factory.py     ← create_react_agent() wrapper
    │   │   ├── runner.py      ← AG-UI stream adapter
    │   │   ├── registry.py    ← MCP lifecycle + agent registry
    │   │   ├── state.py       ← Shared DemoState TypedDict
    │   │   └── {demo}/
    │   │       └── prompts.py ← System prompt + state schema per demo
    │   ├── mcp_servers/
    │   │   ├── base.py        ← emit_card / emit_activity helpers
    │   │   ├── travel_server.py
    │   │   ├── trivia_server.py
    │   │   ├── shopping_server.py
    │   │   ├── chef_server.py
    │   │   └── support_server.py
    │   └── voice/
    │       ├── tts_service.py      ← Streaming PCM + buffered MP3
    │       ├── stt_service.py      ← Whisper transcription
    │       └── realtime_service.py ← WebRTC ephemeral token
    └── tests/
        └── test_mcp_servers.py    ← Unit tests for all 5 servers
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key (agent + voice) |
| `AGENT_MODEL` | No | `gpt-4o` | LangGraph agent model |
| `DB_PATH` | No | `data/checkpoints.db` | SQLite checkpoint path |
| `VOICE_TTS_MODEL` | No | `gpt-4o-mini-tts` | TTS model |
| `VOICE_TTS_VOICE` | No | `ash` | TTS voice name |
| `VOICE_REALTIME_MODEL` | No | `gpt-4o-realtime-preview-2024-12-17` | WebRTC model |
| `OPENWEATHER_API_KEY` | No | — | Travel demo weather (falls back to mock) |

---

## Testing

```bash
cd backend
poetry run pytest
```

Tests call MCP server tool functions directly (no subprocess needed) — they run fast.

```
tests/test_mcp_servers.py  — 35+ tests covering all 5 MCP servers
```

---

## Building a Frontend

See [`FRONTEND_BRIEF.md`](FRONTEND_BRIEF.md) for the complete specification including:

- AG-UI `HttpAgent` setup with all event handlers
- TypeScript interfaces for all 20 generative UI card types
- 3-panel layout: MCP Tool Catalog | Chat | State Canvas
- Voice call integration (REST pipeline + WebRTC bridge mode)
- Demo selector landing page
- Environment variable setup

The frontend can be any framework — the backend speaks standard HTTP + SSE.

---

## License

MIT
