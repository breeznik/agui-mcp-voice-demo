"""
FastAPI application entrypoint.

Routes
------
POST /agent/{demo}              AG-UI SSE streaming endpoint
GET  /agent/{demo}/tools        MCP tool catalog (for frontend sidebar)
POST /api/voice/tts/stream      Streaming PCM TTS
POST /api/voice/tts             Buffered MP3 TTS
POST /api/voice/stt             Whisper speech-to-text
POST /api/voice/realtime/session  WebRTC ephemeral token
GET  /health                    Liveness check
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

load_dotenv()

from src.agents.registry import AgentRegistry
from src.voice.tts_service import synthesize_speech, synthesize_speech_stream
from src.voice.stt_service import transcribe_audio
from src.voice.realtime_service import create_realtime_session

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

DEMO_NAMES = Literal["travel", "trivia", "shopping", "chef", "support"]

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start MCP servers and init LangGraph agents on startup."""
    logger.info("Starting agui-mcp-voice-demo backend...")
    registry = AgentRegistry()
    await registry.start_all()
    app.state.registry = registry
    logger.info("All agents ready.")
    yield
    logger.info("Shutting down...")
    await registry.stop_all()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="agui-mcp-voice-demo", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Agent endpoints ───────────────────────────────────────────────────────────

@app.post("/agent/{demo}")
async def agent_endpoint(demo: DEMO_NAMES, request: Request):
    """
    AG-UI SSE streaming endpoint for each demo agent.

    The frontend sends a JSON body with `threadId` and `messages`
    (standard AG-UI HttpAgent format). We stream back SSE events.
    """
    registry: AgentRegistry = request.app.state.registry
    agent = registry.get(demo)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Demo '{demo}' not found.")

    body = await request.json()
    accept = request.headers.get("accept")

    from src.agents.runner import stream_agent

    return StreamingResponse(
        stream_agent(agent, body, demo_name=demo, accept=accept),
        media_type="text/event-stream",
    )


@app.get("/agent/{demo}/tools")
async def list_tools(demo: DEMO_NAMES, request: Request):
    """
    Return all MCP tools available for a demo (name + description).
    Used by the frontend's MCP Tool Catalog sidebar.
    """
    registry: AgentRegistry = request.app.state.registry
    tools = registry.get_tools(demo)
    if tools is None:
        raise HTTPException(status_code=404, detail=f"Demo '{demo}' not found.")
    return JSONResponse({"demo": demo, "tools": tools})


# ── Voice endpoints ───────────────────────────────────────────────────────────

@app.post("/api/voice/tts/stream")
async def tts_stream(request: Request):
    """Streaming PCM TTS. Returns audio/pcm with sample-rate headers."""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="'text' is required.")

    async def pcm_stream():
        async for chunk in synthesize_speech_stream(text):
            yield chunk

    return StreamingResponse(
        pcm_stream(),
        media_type="audio/pcm",
        headers={
            "X-Voice-Sample-Rate": "24000",
            "X-Voice-Channels": "1",
            "X-Voice-Bit-Depth": "16",
        },
    )


@app.post("/api/voice/tts")
async def tts_buffered(request: Request):
    """Buffered MP3 TTS fallback."""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="'text' is required.")

    audio_bytes = await synthesize_speech(text)
    return StreamingResponse(iter([audio_bytes]), media_type="audio/mpeg")


@app.post("/api/voice/stt")
async def stt(file: UploadFile, language_hint: str | None = None):
    """Whisper STT. Accepts multipart audio file, returns transcript."""
    audio_bytes = await file.read()
    transcript = await transcribe_audio(audio_bytes, language_hint=language_hint)
    return JSONResponse({"transcript": transcript})


@app.post("/api/voice/realtime/session")
async def realtime_session(request: Request):
    """Create an ephemeral WebRTC token for OpenAI Realtime API."""
    body = await request.json()
    thread_id = body.get("thread_id", "")
    session_data = await create_realtime_session(thread_id=thread_id)
    return JSONResponse(session_data)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}
