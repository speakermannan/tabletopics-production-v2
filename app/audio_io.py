# app/audio_io.py
import os
import threading
from datetime import datetime
from typing import Optional, Tuple

import streamlit as st
from recorder import AudioRecorder, RecorderConfig

AUDIO_DIR = "audio"
RECORDINGS_DIR = os.path.join(AUDIO_DIR, "recordings")
LATEST_WAV = os.path.join(AUDIO_DIR, "latest.wav")

_recorder: Optional[AudioRecorder] = None

_stop_lock = threading.Lock()
_stop_inflight = False
_stop_done = False
_stop_error: Optional[str] = None
_stop_path: Optional[str] = None


def _get_recorder() -> AudioRecorder:
    global _recorder
    if _recorder is None:
        _recorder = AudioRecorder(RecorderConfig(samplerate=16000, channels=1, dtype="int16"))
    return _recorder


def _ensure_dirs() -> None:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(RECORDINGS_DIR, exist_ok=True)


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def has_latest_wav() -> bool:
    return os.path.exists(LATEST_WAV) and os.path.getsize(LATEST_WAV) > 0


def get_latest_wav_path() -> str:
    # Prefer the per-recording path if present
    p = st.session_state.get("latest_wav_path")
    if isinstance(p, str) and p.strip() and os.path.exists(p):
        return p
    return LATEST_WAV


def is_stop_inflight() -> bool:
    with _stop_lock:
        return bool(_stop_inflight)


def listen_start() -> None:
    _ensure_dirs()

    # Clear stale UI state so we don't “reuse” old transcript
    st.session_state["current_transcript"] = ""
    st.session_state["stt_last_error"] = ""
    st.session_state["last_transcript_file"] = ""
    st.session_state["latest_wav_path"] = ""

    # Clear old latest.wav to prevent accidental reuse
    _safe_remove(LATEST_WAV)

    global _stop_inflight, _stop_done, _stop_error, _stop_path
    with _stop_lock:
        _stop_inflight = False
        _stop_done = False
        _stop_error = None
        _stop_path = None

    _get_recorder().start()
    st.session_state["system_state"] = "listening"


def _stop_worker(save_path: str) -> None:
    global _stop_inflight, _stop_done, _stop_error, _stop_path
    try:
        _ensure_dirs()
        path = _get_recorder().stop(save_path)

        # Also write/refresh latest.wav as a convenience copy
        try:
            if os.path.exists(path):
                _safe_remove(LATEST_WAV)
                # copy bytes
                with open(path, "rb") as src, open(LATEST_WAV, "wb") as dst:
                    dst.write(src.read())
        except Exception:
            pass

        with _stop_lock:
            _stop_path = path
            _stop_error = None
            _stop_done = True
            _stop_inflight = False

    except Exception as e:
        with _stop_lock:
            _stop_path = None
            _stop_error = str(e)
            _stop_done = True
            _stop_inflight = False


def listen_stop() -> None:
    global _stop_inflight, _stop_done, _stop_error, _stop_path

    st.session_state["system_state"] = "idle"

    with _stop_lock:
        if _stop_inflight:
            return
        _stop_inflight = True
        _stop_done = False
        _stop_error = None
        _stop_path = None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(RECORDINGS_DIR, f"recording_{ts}.wav")

    t = threading.Thread(target=_stop_worker, args=(save_path,), daemon=True)
    t.start()


def pop_stop_result() -> Tuple[bool, Optional[str], Optional[str]]:
    global _stop_done, _stop_error, _stop_path
    with _stop_lock:
        if not _stop_done:
            return False, None, None

        done = _stop_done
        path = _stop_path
        err = _stop_error

        _stop_done = False
        _stop_error = None
        _stop_path = None

        # Save the latest path into session_state so STT uses the right file
        if done and path and not err:
            st.session_state["latest_wav_path"] = path

        return done, path, err
