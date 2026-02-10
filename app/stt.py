# app/stt.py
import os
import json
import re
import threading
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

from paths import TRANSCRIPTS_DIR

load_dotenv()


# -----------------------------
# Helpers
# -----------------------------
def _safe_filename(name: str) -> str:
    name = (name or "").strip() or "Unknown"
    name = name.replace(" ", "_")
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    return name[:40] if name else "Unknown"


def _utc_timestamps() -> tuple[str, str]:
    dt = datetime.now(timezone.utc)
    iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    compact = dt.strftime("%Y%m%d_%H%M%S")
    return iso, compact


def _audio_exists_ok(path: str) -> bool:
    try:
        return bool(path) and os.path.exists(path) and os.path.getsize(path) > 1024
    except Exception:
        return False


# -----------------------------
# Async transcription state (module-level, like audio_io.py)
# -----------------------------
_tx_lock = threading.Lock()
_tx_inflight = False
_tx_done = False
_tx_error: Optional[str] = None
_tx_result: Optional[Dict[str, Any]] = None


def is_transcribe_inflight() -> bool:
    with _tx_lock:
        return bool(_tx_inflight)


def _transcribe_worker(
    *,
    wav_path: str,
    model: str,
    prompt: str,
    speaker: str,
    context: str,
) -> None:
    global _tx_inflight, _tx_done, _tx_error, _tx_result
    try:
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. "
                "Local: add to .env file. "
                "Streamlit Cloud: add in app Settings → Secrets."
            )

        if not _audio_exists_ok(wav_path):
            raise RuntimeError(
                "No recent WAV found to transcribe. Record again (Listen → Stop Listening) and try once more."
            )

        client = OpenAI()

        with open(wav_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model=model,
                file=f,
                prompt=prompt,
            )

        text = (getattr(transcription, "text", "") or "").strip()

        # Persist JSON
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        iso_ts, compact_ts = _utc_timestamps()
        record = {
            "speaker": speaker,
            "timestamp_utc": iso_ts,
            "context": context,
            "audio_path": wav_path,
            "stt_model": model,
            "transcript": text,
        }

        fname = f"{_safe_filename(speaker)}_{compact_ts}.json"
        out_path = os.path.join(TRANSCRIPTS_DIR, fname)
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump(record, fp, ensure_ascii=False, indent=2)

        with _tx_lock:
            _tx_result = {"text": text, "out_path": out_path, "fname": fname}
            _tx_error = None
            _tx_done = True
            _tx_inflight = False

    except Exception as e:
        with _tx_lock:
            _tx_result = None
            _tx_error = str(e)
            _tx_done = True
            _tx_inflight = False


def start_transcribe_async(
    *,
    wav_path: str,
    model: str,
    prompt: str,
    speaker: str,
    context: str,
) -> None:
    """
    Kicks off transcription in a background thread.
    Does NOT touch Streamlit session_state (thread-safe).
    """
    global _tx_inflight, _tx_done, _tx_error, _tx_result

    with _tx_lock:
        if _tx_inflight:
            return
        _tx_inflight = True
        _tx_done = False
        _tx_error = None
        _tx_result = None

    t = threading.Thread(
        target=_transcribe_worker,
        kwargs={
            "wav_path": wav_path,
            "model": model,
            "prompt": prompt,
            "speaker": speaker,
            "context": context,
        },
        daemon=True,
    )
    t.start()


def pop_transcribe_result() -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Returns (done, result, error).
    result = {"text": ..., "out_path": ..., "fname": ...}
    """
    global _tx_done, _tx_error, _tx_result
    with _tx_lock:
        if not _tx_done:
            return False, None, None

        done = _tx_done
        res = _tx_result
        err = _tx_error

        _tx_done = False
        _tx_result = None
        _tx_error = None

        return done, res, err
