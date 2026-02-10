# app/tts.py
import os
import re
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _client() -> OpenAI:
    return OpenAI()


def _sanitize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def tts_preprocess(
    text: str,
    *,
    pace: str = "tight",              # "tight" | "normal" | "dramatic"
    emphasize: Optional[str] = None,  # e.g., Word of the Day
) -> str:
    """
    Text shaping to control pacing + emphasis for TTS.

    pace="tight"   -> shorter pauses, sharper delivery
    pace="normal"  -> reasonable pauses
    pace="dramatic"-> more pauses for stage delivery
    """
    t = _sanitize_spaces(text)

    # Emphasis: make the emphasis word pop (subtle + reliable)
    if emphasize:
        w = emphasize.strip()
        if w:
            t = re.sub(rf"\b{re.escape(w)}\b", w.upper(), t, flags=re.I)

    # Pacing controls (punctuation shaping)
    if pace == "tight":
        t = t.replace("...", ".")
        t = t.replace("—", ",")
        t = t.replace(";", ",")

        t = re.sub(r",\s*,+", ", ", t)
        t = re.sub(r"\s*,\s*", ", ", t)
        t = re.sub(r"\s*\.\s*", ". ", t)
        t = re.sub(r"\s*\?\s*", "? ", t)
        t = re.sub(r"\s*!\s*", "! ", t)

        # Keep it punchy: cap to 1–2 sentences max
        parts = re.split(r"(?<=[.!?])\s+", t)
        parts = [p for p in parts if p.strip()]
        t = " ".join(parts[:2]).strip()

    elif pace == "dramatic":
        t = t.replace("—", " — ")
        t = t.replace(";", "; ")
        t = re.sub(r"\s+(but|so|and)\s+", r", \1 ", t, flags=re.I)

    t = _sanitize_spaces(t)
    return t


def generate_tts_mp3(
    text: str,
    *,
    model: str = "tts-1",
    voice: str = "alloy",
) -> bytes:
    """
    Returns MP3 bytes for Streamlit st.audio().
    """
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. "
            "Local: add to .env file. "
            "Streamlit Cloud: add in app Settings → Secrets."
        )

    text = _sanitize_spaces(text)
    if not text:
        raise ValueError("No text provided for TTS.")

    client = _client()

    # NOTE: Do NOT pass format=. The SDK returns audio bytes via .content by default.
    resp = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )

    audio_bytes = getattr(resp, "content", None)
    if not audio_bytes:
        # Fallback: some SDK variants expose bytes differently
        try:
            audio_bytes = resp.read()
        except Exception:
            audio_bytes = None

    if not audio_bytes:
        raise RuntimeError("TTS returned no audio bytes.")

    return audio_bytes
