# agui-mcp-voice-demo — Claude Context

Open-source demo template: **LangGraph + MCP + Voice + Generative UI (AG-UI)**
Five fully functional demo agents on a single FastAPI backend.

## Memory Files
Detailed context lives in `.claude/memory/`:
- [`MEMORY.md`](.claude/memory/MEMORY.md) — project overview, tech stack, key files
- [`architecture.md`](.claude/memory/architecture.md) — backend data flow, state, voice pipeline
- [`frontend.md`](.claude/memory/frontend.md) — component hierarchy, design system, AG-UI hook

## Quick Reference

### Run
```bash
# Backend
cd backend && poetry install && poetry run uvicorn src.app:app --reload --port 8000
# Frontend
cd frontend && npm install && npm run dev
# Tests
cd backend && poetry run pytest
```

### Key Files
| File | Purpose |
|------|---------|
| `backend/src/app.py` | FastAPI entrypoint, all routes, lifespan |
| `backend/src/agents/registry.py` | AgentRegistry — MCP lifecycle, tool wrapping, event emission |
| `backend/src/agents/factory.py` | `create_demo_agent()` wrapper around `create_react_agent()` |
| `backend/src/agents/runner.py` | `stream_agent()` — AG-UI SSE adapter |
| `backend/src/agents/state.py` | `DemoState` TypedDict (messages, canvas, client_events) |
| `backend/src/mcp_servers/base.py` | `emit_card()` / `emit_activity()` helpers |
| `backend/src/voice/tts_service.py` | Streaming PCM TTS + buffered MP3 fallback |
| `backend/src/voice/realtime_service.py` | WebRTC ephemeral token (bridge mode) |
| `frontend/src/hooks/useCustomAgent.js` | AG-UI HttpAgent hook — all event handlers |
| `frontend/src/components/DemoView.jsx` | Main demo UI container |
| `frontend/src/components/ComponentRegistry.jsx` | card_type → React component map |

### Architecture Rules
- **System prompt is the only control surface** — no custom graph middleware
- **MCP servers are pure data functions** — wrapping + event emission happens in parent process
- **One `create_react_agent()` per demo** — not one agent with tool switching
- **`canvas` = agent working memory** — agents write progress/results; frontend mirrors in HUD
- **`client_events` is replaced each turn** — never accumulates, prevents stale events
- **Voice bridge mode** — Realtime API does STT only; backend handles response + TTS

### Environment Variables
| Variable | Required | Default |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | — |
| `AGENT_MODEL` | No | `gpt-4o` |
| `VOICE_TTS_MODEL` | No | `gpt-4o-mini-tts` |
| `VOICE_TTS_VOICE` | No | `ash` |
| `VOICE_REALTIME_MODEL` | No | `gpt-4o-realtime-preview-2024-12-17` |
| `OPENWEATHER_API_KEY` | No | — (travel demo, falls back to mock) |
| `DB_PATH` | No | `data/checkpoints.db` |
