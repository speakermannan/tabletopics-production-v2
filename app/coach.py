# app/coach.py
import json
import re
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# -----------------------------
# Helpers
# -----------------------------
def _sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _one_sentence(text: str, max_len: int = 180) -> str:
    """
    Ensure output is exactly one short, clean sentence.
    """
    t = _sanitize(text)
    if not t:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", t)
    t = parts[0] if parts else t
    return t[:max_len]


def _contains_word(text: str, word: str) -> bool:
    if not text or not word:
        return False
    return re.search(
        rf"\b{re.escape(word)}\b",
        text,
        flags=re.IGNORECASE,
    ) is not None


# -----------------------------
# Prompt loading
# -----------------------------
@lru_cache(maxsize=4)
def load_prompt(rel_path: str) -> str:
    """
    Load a prompt file relative to this module's folder (…/app),
    so it works regardless of the current working directory.
    """
    base = Path(__file__).parent  # …/app
    path = base / rel_path

    if not path.exists():
        # Safe fallback prompt if file is missing
        return (
            "You generate a private, one-sentence observation about the speaker’s response "
            "in a Toastmasters Table Topics session. Be neutral, descriptive, and supportive. "
            "Do not give instructions or advice."
        )

    return path.read_text(encoding="utf-8")


# -----------------------------
# Deterministic speaker feedback (NO instructions)
# -----------------------------
def _deterministic_hint(transcript: str, summary: str, wod: str) -> str:
    """
    Deterministic, speaker-focused observations only.
    No instructions. No advice. No procedural language.
    """

    # Word of the Day not used
    if wod and not _contains_word(transcript, wod):
        return _one_sentence(
            f"The speaker did not use the Word of the Day (“{wod}”) in their response."
        )

    # Very short response
    if len((transcript or "").split()) < 25:
        return _one_sentence(
            "The response was brief and focused on a single idea."
        )

    # Clear takeaway present
    if summary:
        return _one_sentence(
            "The speaker communicated a clear main takeaway."
        )

    return ""


# -----------------------------
# Public API
# -----------------------------
def generate_coach_hint(
    *,
    transcript: str,
    summary: str,
    word_of_day: str = "",
    model: str = "gpt-4o-mini",
    timeout_sec: float = 6.0,
) -> str:
    """
    Generate a private, one-sentence observation about the speaker's response.
    This is speaker feedback only — not moderator instruction.
    """

    transcript = _sanitize(transcript)
    summary = _sanitize(summary)
    wod = _sanitize(word_of_day)

    # Guard against polluted WOD values (e.g., "1", True)
    if wod.isdigit():
        wod = ""

    if not (transcript or summary):
        return "Clear response with a relatable example."

    # ✅ Deterministic first (fast, safe, predictable)
    cheap = _deterministic_hint(transcript, summary, wod)
    if cheap:
        return cheap

    # ✅ LLM fallback (still speaker-feedback only)
    system = load_prompt("prompts/coach_hint_prompt.txt")

    user = {
        "word_of_day": wod or "",
        "summary": summary,
        "transcript": transcript[:1200],
        "format": "Return EXACTLY 1 sentence, plain text.",
    }

    client = OpenAI(timeout=timeout_sec)

    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=60,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    )

    text = (resp.choices[0].message.content or "").strip()

    # Absolute safety net
    return _one_sentence(text) or "Clear response with a relatable example."
