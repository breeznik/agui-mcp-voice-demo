"""
Text-to-speech service — OpenAI Audio API.

Provides two functions:
  synthesize_speech()        → bytes (buffered MP3)
  synthesize_speech_stream() → async generator of PCM chunks (24kHz int16 mono)

Configuration via environment variables:
  OPENAI_API_KEY     Required
  VOICE_TTS_MODEL    Default: gpt-4o-mini-tts
  VOICE_TTS_VOICE    Default: ash
"""

from __future__ import annotations

import os
import re
from typing import AsyncIterator

import httpx

_OPENAI_API_BASE = "https://api.openai.com/v1"

_FILLER_RE = re.compile(
    r"^(Certainly!?\s*|Of course!?\s*|Sure!?\s*|Absolutely!?\s*"
    r"|I(?:'d| would) be happy to help(?: you(?: with)?)?\.\s*"
    r"|Great(?: question)?!?\s*|No problem!?\s*)",
    re.IGNORECASE,
)


def _format_for_speech(text: str) -> str:
    """Strip markdown and filler phrases so TTS reads naturally."""
    t = str(text or "").strip()
    t = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", t)          # bold/italic
    t = re.sub(r"^#{1,6}\s+", "", t, flags=re.MULTILINE)     # headers
    t = re.sub(r"^\s*[-*]\s+", "", t, flags=re.MULTILINE)    # bullet points
    t = re.sub(r"[✅✓✔→←↑↓📋🎫🧳✈️💳🔹🔸▶►🎯🛍️👨‍🍳🎧🌍]", "", t)  # emoji
    t = _FILLER_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 500:
        t = t[:497] + "..."
    return t


def _headers() -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


async def synthesize_speech(text: str) -> bytes:
    """
    Synthesize speech and return buffered MP3 bytes.

    Parameters
    ----------
    text : Text to synthesise (markdown will be stripped automatically)
    """
    clean = _format_for_speech(text)
    if not clean:
        return b""

    payload = {
        "model": os.getenv("VOICE_TTS_MODEL", "gpt-4o-mini-tts"),
        "voice": os.getenv("VOICE_TTS_VOICE", "ash"),
        "input": clean,
        "response_format": "mp3",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            f"{_OPENAI_API_BASE}/audio/speech",
            headers=_headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.content


async def synthesize_speech_stream(text: str) -> AsyncIterator[bytes]:
    """
    Yield raw PCM audio chunks from OpenAI TTS as they arrive.

    PCM format: 24000 Hz · 16-bit signed int · mono
    Chunks are raw bytes with no container framing.

    Parameters
    ----------
    text : Text to synthesise (markdown will be stripped automatically)
    """
    clean = _format_for_speech(text)
    if not clean:
        return

    payload = {
        "model": os.getenv("VOICE_TTS_MODEL", "gpt-4o-mini-tts"),
        "voice": os.getenv("VOICE_TTS_VOICE", "ash"),
        "input": clean,
        "response_format": "pcm",
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        async with client.stream(
            "POST",
            f"{_OPENAI_API_BASE}/audio/speech",
            headers=_headers(),
            json=payload,
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes(4096):
                yield chunk
