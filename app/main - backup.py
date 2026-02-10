# app/main.py — Production v1 Entry Point
#
# This is the single entry point for the 4-page Streamlit application.
# It handles: page config, session state init, autorefresh polling,
# async completion hooks, sidebar shell, and page navigation.

import sys
import os

# Ensure app/ directory is on sys.path for all page imports
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

from paths import ensure_dirs
from state import (
    init_session_state,
    get_current_speaker,
    context_summary_for_prompt,
    load_speakers_file,
    load_fallback_questions,
)

from evaluator import (
    start_evaluate_async,
    pop_evaluate_result,
    is_eval_inflight,
)

from summarizer import (
    start_summarize_async,
    pop_summarize_result,
    is_summarize_inflight,
)

from stt import (
    start_transcribe_async,
    pop_transcribe_result,
    is_transcribe_inflight,
)

from audio_io import (
    has_latest_wav,
    get_latest_wav_path,
    is_stop_inflight,
)

from coach import generate_coach_hint
from timer import stop_timer

# Sidebar rendering moved to individual pages that need it

# =============================================
# Page config
# =============================================
st.set_page_config(
    page_title="AI Table Topics Co-Host",
    page_icon="TT",
    layout="wide",
)

# =============================================
# Init
# =============================================
ensure_dirs()
init_session_state()

# Load speakers and fallback questions on first run
if not st.session_state.get("speakers_file_list"):
    st.session_state["speakers_file_list"] = load_speakers_file()
if not st.session_state.get("fallback_questions"):
    st.session_state["fallback_questions"] = load_fallback_questions()


# =============================================
# Helpers (moved from old main.py)
# =============================================
def _render_prompt(template_path: str, **vars) -> str:
    text = Path(template_path).read_text(encoding="utf-8")
    for k, v in vars.items():
        text = text.replace(f"{{{{{k}}}}}", v or "")
    return text


def _theme_and_wod_for_summary() -> tuple:
    theme = (st.session_state.get("theme") or "").strip()
    wod = (st.session_state.get("word_of_day") or "").strip()

    if st.session_state.get("prompt_mode") == "Topic Pack":
        pack = (st.session_state.get("topic_pack") or "").strip()
        diff = (st.session_state.get("topic_difficulty") or "").strip()
        if pack:
            theme = f"{pack} ({diff})" if diff else pack
            wod = ""

    return theme, wod


def _ensure_summaries_len(target_len: int) -> None:
    if target_len <= 0:
        return
    summaries = st.session_state.get("speaker_summaries")
    if not isinstance(summaries, list):
        summaries = []
    while len(summaries) < target_len:
        summaries.append("")
    st.session_state["speaker_summaries"] = summaries


def _store_summary_for_current_speaker(summary_text: str) -> None:
    idx = int(st.session_state.get("speaker_index", 0))
    speakers = st.session_state.get("speakers", [])
    target_len = max(len(speakers), idx + 1)
    _ensure_summaries_len(target_len)
    st.session_state["speaker_summaries"][idx] = summary_text.strip()
    st.session_state["last_summary"] = summary_text.strip()


# =============================================
# Autorefresh polling (runs on every page)
# =============================================
if st.session_state.get("timer_running") and st.session_state.get("system_state") != "thinking":
    st_autorefresh(interval=1000, key="stoplight_tick")

if (
    st.session_state.get("awaiting_audio_stop")
    or is_stop_inflight()
    or is_transcribe_inflight()
    or st.session_state.get("awaiting_transcribe")
    or is_summarize_inflight()
    or st.session_state.get("awaiting_summarize")
    or is_eval_inflight()
    or st.session_state.get("awaiting_evaluate")
):
    st_autorefresh(interval=250, key="pipeline_poll")


# =============================================
# Async completion hooks (run on every rerun)
# =============================================

# --- Evaluator ---
done_ev, res_ev, err_ev = pop_evaluate_result()
if done_ev:
    st.session_state["awaiting_evaluate"] = False
    if err_ev:
        st.session_state["evaluator_last_error"] = err_ev
        st.session_state["evaluator_notes"] = ""
        st.session_state["system_state"] = "ready"
        st.session_state["system_state_note"] = "Evaluator failed"
    else:
        st.session_state["evaluator_last_error"] = ""
        st.session_state["evaluator_notes"] = (res_ev.get("notes") or "").strip() if res_ev else ""
        st.session_state["system_state"] = "ready"
        st.session_state["system_state_note"] = "Evaluator notes ready"

# --- Summarizer ---
done_sum, res_sum, err_sum = pop_summarize_result()
if done_sum:
    st.session_state["awaiting_summarize"] = False
    used_llm = bool(res_sum.get("used_llm")) if res_sum else False
    st.session_state["summarizer_used_llm"] = used_llm
    st.session_state["summarizer_last_error"] = err_sum or ""
    st.session_state["system_state"] = "ready"
    st.session_state["system_state_note"] = "Summary ready"

    if res_sum and (res_sum.get("summary") or "").strip():
        _store_summary_for_current_speaker(res_sum["summary"])

        # Coach hint (private)
        try:
            transcript = (st.session_state.get("current_transcript") or "").strip()
            raw_wod = st.session_state.get("word_of_day", "")
            wod = raw_wod.strip() if isinstance(raw_wod, str) else ""
            hint = generate_coach_hint(
                transcript=transcript,
                summary=res_sum["summary"],
                word_of_day=wod,
                model="gpt-4o-mini",
            )
            st.session_state["coach_hint"] = hint.strip()
            st.session_state["coach_hint_last_error"] = ""
        except Exception as e:
            st.session_state["coach_hint"] = ""
            st.session_state["coach_hint_last_error"] = str(e)

        # Auto-evaluate after summary
        if st.session_state.get("auto_evaluate_on_summary", True):
            q = (st.session_state.get("approved_question") or "").strip()
            t = (st.session_state.get("current_transcript") or "").strip()
            raw_wod = st.session_state.get("word_of_day", "")
            wod = raw_wod.strip() if isinstance(raw_wod, str) else ""

            if q and t and (not is_eval_inflight()) and (not st.session_state.get("awaiting_evaluate")):
                st.session_state["awaiting_evaluate"] = True
                st.session_state["system_state"] = "thinking"
                st.session_state["system_state_note"] = "Evaluating response"
                start_evaluate_async(
                    question=q,
                    transcript=t,
                    word_of_day=wod,
                    model=st.session_state.get("evaluator_model", "gpt-4o-mini"),
                )

# --- Transcription ---
done_tx, res_tx, err_tx = pop_transcribe_result()
if done_tx:
    st.session_state["awaiting_transcribe"] = False
    if err_tx:
        st.session_state["stt_last_error"] = err_tx
        st.session_state["system_state"] = "idle"
        st.session_state["system_state_note"] = "Transcription failed"
    else:
        st.session_state["stt_last_error"] = ""
        st.session_state["current_transcript"] = (res_tx.get("text") or "").strip()
        st.session_state["last_transcript_file"] = res_tx.get("out_path") or ""
        st.session_state["system_state"] = "ready"
        st.session_state["system_state_note"] = "Transcript ready"

        # Auto-summarize after transcript
        if st.session_state.get("auto_summarize_on_transcript", True):
            transcript = (st.session_state.get("current_transcript") or "").strip()
            if transcript and not is_summarize_inflight() and not st.session_state.get("awaiting_summarize"):
                theme, wod = _theme_and_wod_for_summary()
                st.session_state["awaiting_summarize"] = True
                st.session_state["system_state"] = "thinking"
                st.session_state["system_state_note"] = "Summarizing answer"
                start_summarize_async(
                    transcript=transcript,
                    theme=theme,
                    word_of_day=wod,
                    model="gpt-4o-mini",
                )

# --- Auto-transcribe trigger (WAV-first, async) ---
if (
    st.session_state.get("awaiting_audio_stop")
    and st.session_state.get("auto_transcribe_on_stop", True)
    and not is_transcribe_inflight()
    and not st.session_state.get("awaiting_transcribe")
):
    if not is_stop_inflight() and has_latest_wav():
        st.session_state["awaiting_audio_stop"] = False
        st.session_state["awaiting_transcribe"] = True
        st.session_state["system_state"] = "thinking"
        st.session_state["system_state_note"] = "Transcribing audio"

        speaker = get_current_speaker() or "Unknown"
        ctx = context_summary_for_prompt()
        model = st.session_state.get("stt_model", "gpt-4o-mini-transcribe")

        prompt = _render_prompt(
            "app/prompts/stt_prompt.txt",
            context=ctx,
            speaker=speaker,
        )

        wav_path = get_latest_wav_path()
        start_transcribe_async(
            wav_path=wav_path,
            model=model,
            prompt=prompt,
            speaker=speaker,
            context=ctx,
        )


# =============================================
# Navigation (sidebar hidden — pages have their own nav buttons)
# =============================================

st.switch_page("pages/home.py")