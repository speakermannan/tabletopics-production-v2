# app/audio_browser.py — Browser-based microphone capture for Streamlit Cloud
#
# Data flow:
#   Browser mic -> JS AudioContext -> WAV encode -> base64 ->
#   Streamlit component value -> Python decode -> WAV file -> STT pipeline
#
# The existing transcription pipeline (stt.py) picks up the WAV file
# from audio/latest.wav, exactly as it does with server-side recording.

import os
import base64
from datetime import datetime
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

from audio_io import AUDIO_DIR, RECORDINGS_DIR, LATEST_WAV, _ensure_dirs, _safe_remove

# Declare the browser audio Streamlit component.
# Points to the directory containing index.html with the JS capture logic.
_COMPONENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "components", "browser_audio"
)
_browser_audio_component = components.declare_component(
    "browser_audio", path=_COMPONENT_DIR
)


def render_browser_audio() -> Optional[str]:
    """Render the browser audio component and return WAV path if audio received.

    Must be called on every Live page rerun when in Cloud mode.
    The component is invisible (height=0) when idle and shows a small
    "Recording..." indicator when the mic is active.

    Returns:
        Path to saved WAV file when new audio data arrives, None otherwise.
    """
    recording = st.session_state.get("browser_recording", False)

    # Render the component — JS handles mic capture based on the recording flag
    result = _browser_audio_component(
        recording=recording, key="browser_audio_cap", default=None
    )

    if not result or not isinstance(result, dict):
        return None

    audio_id = result.get("id")
    last_id = st.session_state.get("_browser_audio_last_id")

    # Only process each audio submission once (keyed by unique timestamp id)
    if not audio_id or audio_id == last_id:
        return None

    audio_b64 = result.get("audio", "")
    if not audio_b64:
        return None

    st.session_state["_browser_audio_last_id"] = audio_id

    # Decode base64 -> WAV bytes -> disk
    try:
        audio_bytes = base64.b64decode(audio_b64)
        return _save_browser_audio(audio_bytes)
    except Exception as e:
        st.session_state["stt_last_error"] = f"Browser audio error: {e}"
        return None


def _save_browser_audio(wav_bytes: bytes) -> str:
    """Save browser-captured WAV bytes to disk.

    Writes to both a timestamped recording file and the latest.wav
    convenience copy, matching the same output format as the
    server-side recorder (audio_io._stop_worker).
    """
    _ensure_dirs()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(RECORDINGS_DIR, f"recording_{ts}.wav")

    # Write timestamped recording
    with open(save_path, "wb") as f:
        f.write(wav_bytes)

    # Copy to latest.wav (pipeline checks has_latest_wav() for this file)
    _safe_remove(LATEST_WAV)
    with open(LATEST_WAV, "wb") as f:
        f.write(wav_bytes)

    # Store path in session state so STT uses the right file
    st.session_state["latest_wav_path"] = save_path

    return save_path
