"""
WebRTC voice session bootstrap — OpenAI Realtime API.

Creates an ephemeral token for the browser to connect directly to
OpenAI's Realtime API via WebRTC. The browser uses this token to
establish a peer connection; audio never routes through our server.

Configuration via environment variables:
  OPENAI_API_KEY         Required
  VOICE_REALTIME_MODEL   Default: gpt-4o-realtime-preview-2024-12-17
"""

from __future__ import annotations

import os

import httpx

_OPENAI_API_BASE = "https://api.openai.com/v1"


async def create_realtime_session(thread_id: str = "") -> dict:
    """
    Create an ephemeral WebRTC session token.

    The token is short-lived (60s) and scoped to one connection.
    The browser exchanges it for a WebRTC offer/answer with OpenAI directly.

    Parameters
    ----------
    thread_id : Session/thread identifier (used as the session label)

    Returns
    -------
    dict with `client_secret.value` (the ephemeral token) and session config
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    model = os.getenv("VOICE_REALTIME_MODEL", "gpt-4o-realtime-preview-2024-12-17")

    session_config = {
        "model": model,
        # Bridge mode: the realtime model handles STT only.
        # The browser forwards transcripts to our /agent/{demo} endpoint
        # and plays TTS from our /api/voice/tts/stream.
        "modalities": ["audio", "text"],
        "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
        "turn_detection": {
            "type": "semantic_vad",
            "create_response": False,   # Don't generate responses — bridge mode
            "interrupt_response": False,
        },
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{_OPENAI_API_BASE}/realtime/sessions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=session_config,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "session_id": data.get("id", ""),
        "client_secret": data.get("client_secret", {}),
        "model": model,
        "thread_id": thread_id,
        # Tell the browser this is bridge mode — it should forward
        # transcripts to /agent/{demo} and play TTS locally.
        "bridge_mode": True,
    }
