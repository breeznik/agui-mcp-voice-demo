"""
Speech-to-text service — OpenAI Whisper API.

Configuration via environment variables:
  OPENAI_API_KEY     Required
  VOICE_STT_MODEL    Default: gpt-4o-mini-transcribe
"""

from __future__ import annotations

import os

import httpx

_OPENAI_API_BASE = "https://api.openai.com/v1"


def _headers() -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return {"Authorization": f"Bearer {api_key}"}


async def transcribe_audio(
    audio_bytes: bytes,
    language_hint: str | None = None,
    filename: str = "audio.webm",
) -> str:
    """
    Transcribe audio bytes to text using OpenAI Whisper.

    Parameters
    ----------
    audio_bytes   : Raw audio bytes (WebM, WAV, MP3, OGG, MP4)
    language_hint : BCP-47 language code hint (e.g. "en", "es") — optional
    filename      : Filename hint for content-type detection

    Returns
    -------
    Transcribed text string (empty string if no speech detected)
    """
    if not audio_bytes:
        return ""

    model = os.getenv("VOICE_STT_MODEL", "gpt-4o-mini-transcribe")

    files = {"file": (filename, audio_bytes, "audio/webm")}
    data: dict = {"model": model}
    if language_hint:
        data["language"] = language_hint

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            f"{_OPENAI_API_BASE}/audio/transcriptions",
            headers=_headers(),
            files=files,
            data=data,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("text") or "").strip()
