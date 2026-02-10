# app/summarizer.py
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Optional, Tuple, Dict, Any
import threading

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path


load_dotenv()

def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _cap_words(text: str, max_words: int) -> str:
    words = _sanitize(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).strip()


@dataclass(frozen=True)
class SummaryResult:
    summary: str
    used_llm: bool
    error: Optional[str] = None


def _client() -> OpenAI:
    return OpenAI()


def summarize_answer(
    transcript: str,
    *,
    speaker: str = "",
    theme: str = "",
    word_of_day: str = "",
    model: str = "gpt-4o-mini",
) -> SummaryResult:
    """
    Converts a raw transcript into a bounded, panel-friendly summary.

    Output requirements:
    - 2–3 bullets max
    - neutral tone
    - no praise, no critique, no advice
    - short enough to be used as "memory" for the next question
    """
    transcript = _sanitize(transcript)
    if not transcript:
        return SummaryResult(summary="", used_llm=False, error="No transcript provided.")

    speaker = _sanitize(speaker)
    theme = _sanitize(theme)
    word_of_day = _sanitize(word_of_day)

    transcript_for_prompt = _cap_words(transcript, 220)

    system = load_prompt("app/prompts/summarize_prompt.txt")

    user = {
        "speaker": speaker or "the speaker",
        "theme": theme or None,
        "word_of_day": word_of_day or None,
        "transcript": transcript_for_prompt,
        "goal": "Create memory the next question can build on.",
    }

    try:
        resp = _client().chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=140,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
        )
        text = resp.choices[0].message.content or ""
        data = json.loads(text)

        bullets = data.get("bullets") or []
        if not isinstance(bullets, list):
            bullets = []

        clean = []
        for b in bullets[:3]:
            b = _sanitize(str(b))
            if not b:
                continue
            b = _cap_words(b, 15)
            clean.append(b)

        if not clean:
            gist = _cap_words(transcript, 18)
            return SummaryResult(summary=f"- {gist}", used_llm=False)

        summary = "\n".join([f"- {b}" for b in clean]).strip()
        return SummaryResult(summary=summary, used_llm=True)

    except Exception as e:
        gist = _cap_words(transcript, 18)
        return SummaryResult(summary=f"- {gist}", used_llm=False, error=str(e))


# =============================
# Async wrapper (Streamlit-safe)
# =============================

_sum_lock = threading.Lock()
_sum_inflight = False
_sum_done = False
_sum_error: Optional[str] = None
_sum_result: Optional[Dict[str, Any]] = None


def is_summarize_inflight() -> bool:
    with _sum_lock:
        return bool(_sum_inflight)


def _summarize_worker(
    *,
    transcript: str,
    speaker: str,
    theme: str,
    word_of_day: str,
    model: str,
) -> None:
    global _sum_inflight, _sum_done, _sum_error, _sum_result
    try:
        res = summarize_answer(
            transcript=transcript,
            speaker=speaker,
            theme=theme,
            word_of_day=word_of_day,
            model=model,
        )

        with _sum_lock:
            _sum_result = {
                "summary": res.summary,
                "used_llm": bool(res.used_llm),
            }
            _sum_error = res.error
            _sum_done = True
            _sum_inflight = False

    except Exception as e:
        with _sum_lock:
            _sum_result = None
            _sum_error = str(e)
            _sum_done = True
            _sum_inflight = False


def start_summarize_async(
    *,
    transcript: str,
    speaker: str = "",
    theme: str,
    word_of_day: str,
    model: str = "gpt-4o-mini",
) -> None:
    global _sum_inflight, _sum_done, _sum_error, _sum_result

    with _sum_lock:
        if _sum_inflight:
            return
        _sum_inflight = True
        _sum_done = False
        _sum_error = None
        _sum_result = None

    t = threading.Thread(
        target=_summarize_worker,
        kwargs={
            "transcript": transcript,
            "speaker": speaker,
            "theme": theme,
            "word_of_day": word_of_day,
            "model": model,
        },
        daemon=True,
    )
    t.start()


def pop_summarize_result() -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    global _sum_done, _sum_error, _sum_result

    with _sum_lock:
        if not _sum_done:
            return False, None, None

        done = _sum_done
        res = _sum_result
        err = _sum_error

        _sum_done = False
        _sum_result = None
        _sum_error = None

        return done, res, err
