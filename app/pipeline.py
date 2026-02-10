# app/pipeline.py — V2 Hybrid Semi-Autopilot Pipeline
#
# State machine with two moderator wait-gates:
#   generating_question → question_ready [WAIT] → speaking_question →
#   waiting_to_listen → listening → processing → turn_complete [WAIT]
#
# Call run_pipeline() on every Live page rerun.

import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

from state import (
    get_current_speaker,
    context_summary_for_prompt,
    get_question_constraints,
    next_speaker,
    end_session,
    clear_turn_fields,
)
from evaluator import start_evaluate_async, pop_evaluate_result, is_eval_inflight
from summarizer import start_summarize_async, pop_summarize_result, is_summarize_inflight
from stt import start_transcribe_async, pop_transcribe_result, is_transcribe_inflight
from audio_io import listen_start, listen_stop, has_latest_wav, get_latest_wav_path, is_stop_inflight
from coach import generate_coach_hint
from timer import start_timer, stop_timer
from tts import generate_tts_mp3, tts_preprocess
from question_gen import (
    generate_initial_question,
    generate_followup_question,
    QuestionConstraints,
)


# ── Helpers ──────────────────────────────────────────────

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


def _constraints_with_theme() -> QuestionConstraints:
    base = get_question_constraints()
    theme = (st.session_state.get("theme") or "").strip()
    if st.session_state.get("prompt_mode") == "Topic Pack":
        pack = (st.session_state.get("topic_pack") or "").strip()
        diff = (st.session_state.get("topic_difficulty") or "").strip()
        if pack:
            theme = f"{pack} ({diff})" if diff else pack
    return QuestionConstraints(
        creativity=base.creativity,
        max_seconds=base.max_seconds,
        style=base.style,
        avoid_topics=base.avoid_topics,
        require_word=base.require_word,
        theme=theme or None,
    )


def _get_prev_summary(idx: int) -> str:
    summaries = st.session_state.get("speaker_summaries")
    if isinstance(summaries, list) and 0 <= idx - 1 < len(summaries):
        s = summaries[idx - 1]
        if isinstance(s, str) and s.strip():
            return s.strip()
    v = st.session_state.get("last_summary", "")
    if isinstance(v, str) and v.strip():
        return v.strip()
    t = st.session_state.get("current_transcript", "")
    return t.strip() if isinstance(t, str) else ""


# ── Autopilot phase handlers ────────────────────────────

def _autopilot_generate_question():
    """Generate a question for the current speaker."""
    st.session_state["system_state"] = "thinking"
    st.session_state["system_state_note"] = "Generating question"

    constraints = _constraints_with_theme()
    speaker = get_current_speaker() or "Speaker"
    ctx = context_summary_for_prompt()
    idx = int(st.session_state.get("speaker_index", 0))

    results = st.session_state.get("speaker_results", [])
    has_prev = idx > 0 and len(results) > 0

    if idx == 0 or not has_prev:
        question = generate_initial_question(
            speaker=speaker, context=ctx, constraints=constraints,
        )
    else:
        speakers = st.session_state.get("speakers", [])
        prev_speaker = speakers[idx - 1] if (idx > 0 and idx - 1 < len(speakers)) else "the previous speaker"
        prev_result = results[-1]
        prev_summary = _get_prev_summary(idx)
        prev_question = prev_result.get("question", "")
        prev_transcript_text = prev_result.get("transcript", "") if not prev_summary else ""
        asked_questions = [r["question"] for r in results if r.get("question")]
        question = generate_followup_question(
            next_speaker=speaker, context=ctx,
            prev_speaker=prev_speaker, prev_transcript=prev_transcript_text,
            prev_summary=prev_summary,
            prev_question=prev_question,
            asked_questions=asked_questions,
            template_index=max(0, idx - 1),
            constraints=constraints,
        )

    st.session_state["approved_question"] = question
    st.session_state["proposed_question"] = ""
    st.session_state["system_state"] = "ready"
    st.session_state["system_state_note"] = "Question ready"
    st.session_state["autopilot_phase"] = "speaking_question"


def _autopilot_question_ready():
    """WAIT gate: moderator must click PLAY to proceed. No-op."""
    pass


def _autopilot_speak_question():
    """TTS reads the approved question aloud."""
    st.session_state["system_state"] = "speaking"
    st.session_state["system_state_note"] = "Reading question aloud"

    text = st.session_state.get("approved_question", "")
    if not text:
        prep_sec = int(st.session_state.get("prep_time_sec", 30))
        st.session_state["autopilot_phase"] = "waiting_to_listen"
        st.session_state["autopilot_advance_at"] = time.time() + prep_sec
        st.session_state["prep_countdown_start_ts"] = time.time()
        return

    try:
        wod = ""
        if st.session_state.get("tts_emphasize_wod"):
            wod = (st.session_state.get("word_of_day") or "").strip()
        shaped = tts_preprocess(text, pace=st.session_state.get("tts_pace", "tight"), emphasize=wod or None)
        audio = generate_tts_mp3(
            shaped,
            model=st.session_state.get("tts_model", "tts-1"),
            voice=st.session_state.get("tts_voice", "nova"),
        )
        st.session_state["tts_audio_mp3"] = audio
        st.session_state["tts_last_text"] = shaped
        st.session_state["tts_last_error"] = ""
    except Exception as e:
        st.session_state["tts_last_error"] = str(e)

    st.session_state["autopilot_phase"] = "waiting_to_listen"
    # Estimate TTS playback duration from word count (~2.2 words/sec + 3s buffer)
    audio_bytes = st.session_state.get("tts_audio_mp3")
    word_count = len(text.split()) if text else 0
    tts_duration = max(5, word_count / 2.2 + 3) if audio_bytes else 0
    prep_sec = int(st.session_state.get("prep_time_sec", 30))
    st.session_state["autopilot_advance_at"] = time.time() + tts_duration + prep_sec
    # prep_countdown_start_ts is a FUTURE timestamp — prep begins after TTS finishes
    st.session_state["prep_countdown_start_ts"] = time.time() + tts_duration


def _autopilot_waiting_to_listen():
    """Wait for prep time, then auto-start recording."""
    advance_at = st.session_state.get("autopilot_advance_at", 0)
    if time.time() >= advance_at:
        st.session_state["prep_countdown_start_ts"] = 0.0
        try:
            listen_start()
            start_timer()
            st.session_state["system_state"] = "listening"
            st.session_state["system_state_note"] = "Recording speaker"
            st.session_state["autopilot_phase"] = "listening"
        except Exception as e:
            st.session_state["system_state"] = "idle"
            st.session_state["system_state_note"] = f"Mic error: {e}"
            st.session_state["autopilot_advance_at"] = time.time() + 3.0


def _autopilot_check_timer_expired():
    """In listening phase, auto-stop when timer + grace period expires."""
    from timer import elapsed_sec
    el = elapsed_sec()
    tgt = int(st.session_state.get("timer_target_sec", 90))
    grace = int(st.session_state.get("grace_time_sec", 15))
    if el >= tgt + grace:
        listen_stop()
        stop_timer()
        st.session_state["awaiting_audio_stop"] = True
        st.session_state["system_state"] = "thinking"
        st.session_state["system_state_note"] = "Finalizing audio"
        st.session_state["autopilot_phase"] = "processing"


def _autopilot_check_processing_complete():
    """Check if all processing (transcribe → summarize → evaluate) is done."""
    if (
        not st.session_state.get("awaiting_audio_stop")
        and not st.session_state.get("awaiting_transcribe")
        and not st.session_state.get("awaiting_summarize")
        and not st.session_state.get("awaiting_evaluate")
        and not is_stop_inflight()
        and not is_transcribe_inflight()
        and not is_summarize_inflight()
        and not is_eval_inflight()
    ):
        # All done — check if we have results
        has_eval = bool((st.session_state.get("evaluator_notes") or "").strip())
        has_summary = bool((st.session_state.get("last_summary") or "").strip())
        has_transcript = bool((st.session_state.get("current_transcript") or "").strip())
        if has_eval or has_summary or has_transcript:
            st.session_state["autopilot_phase"] = "turn_complete"
            st.session_state["system_state"] = "ready"
            st.session_state["system_state_note"] = "Turn complete — review results"


def _autopilot_turn_complete():
    """WAIT gate: moderator must click Next Speaker or Finish. No-op."""
    pass


# ── Main pipeline ────────────────────────────────────────

def run_pipeline() -> None:
    """Run autorefresh + async completion hooks + autopilot state machine."""

    autopilot = st.session_state.get("autopilot_enabled", True)
    phase = st.session_state.get("autopilot_phase", "idle")
    phase_before = phase
    paused = st.session_state.get("autopilot_paused", False)

    # ── Autorefresh polling ──────────────────────────────
    if st.session_state.get("timer_running") and st.session_state.get("system_state") != "thinking":
        st_autorefresh(interval=1000, key="stoplight_tick")

    needs_poll = (
        st.session_state.get("awaiting_audio_stop")
        or is_stop_inflight()
        or is_transcribe_inflight()
        or st.session_state.get("awaiting_transcribe")
        or is_summarize_inflight()
        or st.session_state.get("awaiting_summarize")
        or is_eval_inflight()
        or st.session_state.get("awaiting_evaluate")
        or (autopilot and not paused and phase in (
            "waiting_to_listen", "processing",
        ))
    )
    if needs_poll:
        st_autorefresh(interval=500, key="pipeline_poll")

    # ── Evaluator completion ─────────────────────────────
    done_ev, res_ev, err_ev = pop_evaluate_result()
    if done_ev:
        st.session_state["awaiting_evaluate"] = False
        if err_ev:
            st.session_state["evaluator_last_error"] = err_ev
            st.session_state["evaluator_notes"] = ""
        else:
            st.session_state["evaluator_last_error"] = ""
            st.session_state["evaluator_notes"] = (res_ev.get("notes") or "").strip() if res_ev else ""
        st.session_state["system_state"] = "ready"
        st.session_state["system_state_note"] = "Evaluation complete"

    # ── Summarizer completion ────────────────────────────
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

            # Coach hint
            try:
                transcript = (st.session_state.get("current_transcript") or "").strip()
                raw_wod = st.session_state.get("word_of_day", "")
                wod = raw_wod.strip() if isinstance(raw_wod, str) else ""
                hint = generate_coach_hint(
                    transcript=transcript, summary=res_sum["summary"],
                    word_of_day=wod, model="gpt-4o-mini",
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
                if q and t and not is_eval_inflight() and not st.session_state.get("awaiting_evaluate"):
                    st.session_state["awaiting_evaluate"] = True
                    st.session_state["system_state"] = "thinking"
                    st.session_state["system_state_note"] = "Evaluating response"
                    start_evaluate_async(
                        question=q, transcript=t, word_of_day=wod,
                        model=st.session_state.get("evaluator_model", "gpt-4o-mini"),
                    )

    # ── Transcription completion ─────────────────────────
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

            # Auto-summarize
            if st.session_state.get("auto_summarize_on_transcript", True):
                transcript = (st.session_state.get("current_transcript") or "").strip()
                if transcript and not is_summarize_inflight() and not st.session_state.get("awaiting_summarize"):
                    theme, wod = _theme_and_wod_for_summary()
                    st.session_state["awaiting_summarize"] = True
                    st.session_state["system_state"] = "thinking"
                    st.session_state["system_state_note"] = "Summarizing answer"
                    start_summarize_async(
                        transcript=transcript, theme=theme,
                        word_of_day=wod, model="gpt-4o-mini",
                    )

    # ── Auto-transcribe trigger ──────────────────────────
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
                context=ctx, speaker=speaker,
            )
            wav_path = get_latest_wav_path()
            start_transcribe_async(
                wav_path=wav_path, model=model, prompt=prompt,
                speaker=speaker, context=ctx,
            )

    # ── Autopilot state machine ──────────────────────────
    if autopilot and not paused:
        if phase == "generating_question":
            _autopilot_generate_question()
        elif phase == "question_ready":
            _autopilot_question_ready()      # wait for PLAY click
        elif phase == "speaking_question":
            _autopilot_speak_question()
        elif phase == "waiting_to_listen":
            _autopilot_waiting_to_listen()
        elif phase == "listening":
            _autopilot_check_timer_expired()
        elif phase == "processing":
            _autopilot_check_processing_complete()
        elif phase == "turn_complete":
            _autopilot_turn_complete()       # wait for Next Speaker click

    # Force rerun if phase changed during this pipeline run so
    # autorefresh and UI render with the correct state.
    if st.session_state.get("autopilot_phase", "idle") != phase_before:
        st.rerun()
