# app/ui/ui_controls.py — V2 Hybrid Controls + Status Bar + Info Boxes
import time
import streamlit as st
from state import (
    get_current_speaker,
    context_summary_for_prompt,
    get_question_constraints,
    next_speaker,
    skip_speaker,
    end_session,
)
from timer import stop_timer, start_timer
from audio_io import listen_start, listen_stop
from question_gen import QuestionConstraints


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


# ── Status Bar ────────────────────────────────────────────

_PHASE_LABELS = {
    "idle": "Ready",
    "generating_question": "Generating Question...",
    "speaking_question": "Playing Question...",
    "waiting_to_listen": "Get Ready to Speak...",
    "listening": "Listening...",
    "processing": "Processing Response...",
    "turn_complete": "Turn Complete — Review Results",
    "complete": "Session Complete",
}

_PHASE_STEPS = [
    "generating_question", "speaking_question",
    "waiting_to_listen", "listening", "processing", "turn_complete",
]


def render_autopilot_bar():
    """Render the status bar with phase indicator and timeline."""
    phase = st.session_state.get("autopilot_phase", "idle")
    paused = st.session_state.get("autopilot_paused", False)

    dot_cls = "autopilot-dot"
    label_cls = "autopilot-label"
    if paused:
        dot_cls += " paused"
        label_cls += " paused"
    elif phase == "complete":
        dot_cls += " complete"
        label_cls += " complete"

    label_text = "PAUSED" if paused else _PHASE_LABELS.get(phase, phase)

    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    progress = f"Speaker {idx + 1} of {len(speakers)}" if speakers else ""

    current_step_idx = _PHASE_STEPS.index(phase) if phase in _PHASE_STEPS else -1
    steps_html = ""
    for i, step in enumerate(_PHASE_STEPS):
        if i < current_step_idx:
            steps_html += '<div class="at-step done"></div>'
        elif i == current_step_idx:
            steps_html += '<div class="at-step active"></div>'
        else:
            steps_html += '<div class="at-step"></div>'

    bar_html = (
        '<div class="autopilot-bar">'
        f'<span class="{dot_cls}"></span>'
        f'<span class="{label_cls}">{label_text}</span>'
        f'<span class="autopilot-phase">{progress}</span>'
        '</div>'
        f'<div class="autopilot-timeline">{steps_html}</div>'
    )
    st.markdown(bar_html, unsafe_allow_html=True)


# ── Operator Controls ────────────────────────────────────

def render_operator_controls():
    """Phase-aware operator panel with moderator gates."""
    st.markdown('<span class="controls-marker"></span>', unsafe_allow_html=True)
    session_active = st.session_state.get("session_started", False)
    phase = st.session_state.get("autopilot_phase", "idle")

    st.markdown("### Controls")

    # Up-next compact list
    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    up_next = [speakers[i] for i in range(idx + 1, min(idx + 3, len(speakers)))]
    if up_next:
        rows = "".join(
            f'<div class="up-next-row">'
            f'<div class="up-next-dot"></div>{name}</div>'
            for name in up_next
        )
        st.markdown(
            f'<div style="margin-bottom:0.3rem;">'
            f'<strong style="font-size:0.75rem; color:#5A6478; text-transform:uppercase; letter-spacing:0.5px;">Up Next</strong>'
            f'{rows}</div>',
            unsafe_allow_html=True,
        )

    # ── Phase-specific controls ──────────────────────────

    if phase == "listening":
        _render_listening_controls()

    elif phase == "turn_complete":
        _render_turn_complete_controls(session_active)

    elif phase == "waiting_to_listen":
        _render_waiting_to_listen_controls(session_active)

    elif phase in ("generating_question", "speaking_question"):
        # Show question text during speaking phase
        if phase == "speaking_question":
            question = (st.session_state.get("approved_question") or "").strip()
            if question:
                st.markdown(
                    f'<div style="background:#141928; border:1px solid rgba(255,255,255,0.06); '
                    f'border-radius:10px; padding:0.7rem 0.9rem; margin-bottom:0.5rem; '
                    f'font-size:0.9rem; color:#E8ECF5; line-height:1.5;">'
                    f'{question}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            f'<div style="text-align:center; padding:0.6rem 0; color:#8892A8; font-size:0.85rem;">'
            f'{_PHASE_LABELS.get(phase, phase)}</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            with st.container():
                st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
                if st.button("Regenerate",
                             disabled=not session_active or phase == "generating_question",
                             use_container_width=True, key="btn_regen_auto"):
                    st.session_state["tts_audio_mp3"] = None
                    st.session_state["autopilot_phase"] = "generating_question"
                    st.rerun()
        with c2:
            with st.container():
                st.markdown('<span class="btn-color-dark"></span>', unsafe_allow_html=True)
                if st.button("Skip Speaker", disabled=not session_active,
                             use_container_width=True, key="btn_skip_auto"):
                    skip_speaker(stop_timer)
                    st.session_state["autopilot_phase"] = "generating_question"
                    st.rerun()

    elif phase == "processing":
        _render_processing_status()

    # ── Always visible: End Session ──────────────────────
    st.markdown('<div style="height:0.4rem"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="btn-color-red"></span>', unsafe_allow_html=True)
        if st.button("End Session", disabled=not session_active,
                     use_container_width=True, key="btn_end_session"):
            end_session(stop_timer)
            st.session_state["autopilot_phase"] = "complete"
            st.switch_page("pages/results.py")

    # Errors
    if st.session_state.get("tts_last_error"):
        st.error(f"TTS: {st.session_state['tts_last_error']}")
    if st.session_state.get("stt_last_error"):
        st.error(f"STT: {st.session_state['stt_last_error']}")
    if st.session_state.get("summarizer_last_error"):
        st.warning(f"Summarizer: {st.session_state['summarizer_last_error']}")


# ── Phase control helpers ─────────────────────────────────

def _render_next_speaker_disabled(key_suffix: str):
    """Show a disabled Next Speaker (or Finish) button as visual indicator."""
    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    is_last = idx >= len(speakers) - 1
    label = "Finish Session" if is_last else "Next Speaker"
    with st.container():
        st.markdown('<span class="btn-color-dark"></span>', unsafe_allow_html=True)
        st.button(label, disabled=True, use_container_width=True,
                  key=f"btn_next_{key_suffix}")


def _render_question_ready_controls(session_active):
    """Controls for the question_ready wait-gate: PLAY, Regenerate, Edit."""
    question = (st.session_state.get("approved_question") or "").strip()

    if question:
        st.markdown(
            f'<div style="background:#141928; border:1px solid rgba(255,255,255,0.06); '
            f'border-radius:10px; padding:0.7rem 0.9rem; margin-bottom:0.5rem; '
            f'font-size:0.9rem; color:#E8ECF5; line-height:1.5;">'
            f'{question}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("No question generated.")

    # PLAY — primary action
    with st.container():
        st.markdown('<span class="btn-color-green"></span>', unsafe_allow_html=True)
        if st.button("PLAY Question", use_container_width=True,
                     type="primary", key="btn_play_question",
                     disabled=not question):
            st.session_state["autopilot_phase"] = "speaking_question"
            st.rerun()

    # Regenerate / Skip
    r1, r2 = st.columns(2)
    with r1:
        with st.container():
            st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
            if st.button("Regenerate", use_container_width=True, key="btn_regen"):
                st.session_state["autopilot_phase"] = "generating_question"
                st.rerun()
    with r2:
        with st.container():
            st.markdown('<span class="btn-color-dark"></span>', unsafe_allow_html=True)
            if st.button("Skip Speaker", disabled=not session_active,
                         use_container_width=True, key="btn_skip_qr"):
                skip_speaker(stop_timer)
                st.session_state["autopilot_phase"] = "generating_question"
                st.rerun()

    # Edit question
    edited = st.text_area("Edit question:", value=question, height=68,
                          key="edit_question_input")
    if edited.strip() and edited.strip() != question:
        if st.button("Apply Edit", key="btn_apply_edit"):
            st.session_state["approved_question"] = edited.strip()
            st.rerun()


def _render_listening_controls():
    """Controls during listening: Stop Speaking + disabled Next Speaker + timer."""
    from audio_io import is_cloud
    if is_cloud():
        return _render_listening_controls_cloud()
    from timer import elapsed_sec, stoplight_state
    el = elapsed_sec()
    tgt = int(st.session_state.get("timer_target_sec", 90))
    label, color = stoplight_state(el, tgt)
    color_hex = {
        "neutral": "#8892A8",
        "green": "#00D4AA",
        "orange": "#FF6B35", "red": "#FF3366",
    }.get(color, "#8892A8")
    mins, secs = divmod(el, 60)

    grace = int(st.session_state.get("grace_time_sec", 15))
    stop_note = f"{label} — auto-stops {grace}s after red" if grace > 0 else f"{label} — auto-stops at red"

    st.markdown(
        f'<div style="text-align:center; padding:0.5rem 0;">'
        f'<span style="font-size:1.8rem; font-weight:800; font-family:monospace; '
        f'color:{color_hex};">{mins}:{secs:02d}</span>'
        f'<div style="font-size:0.7rem; color:#8892A8; margin-top:0.2rem;">{stop_note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.markdown('<span class="btn-color-red"></span>', unsafe_allow_html=True)
            if st.button("Stop Speaking", use_container_width=True, key="btn_stop_early"):
                listen_stop()
                stop_timer()
                st.session_state["awaiting_audio_stop"] = True
                st.session_state["system_state"] = "thinking"
                st.session_state["system_state_note"] = "Finalizing audio"
                st.session_state["autopilot_phase"] = "processing"
                st.rerun()
    with c2:
        _render_next_speaker_disabled("listen")


def _render_listening_controls_cloud():
    """Cloud listening: same layout as local + st.audio_input for recording."""
    from audio_io import save_cloud_audio
    from timer import elapsed_sec, stoplight_state

    # ── Same timer display as local ──────────────────────
    el = elapsed_sec()
    tgt = int(st.session_state.get("timer_target_sec", 90))
    label, color = stoplight_state(el, tgt)
    color_hex = {
        "neutral": "#8892A8",
        "green": "#00D4AA",
        "orange": "#FF6B35", "red": "#FF3366",
    }.get(color, "#8892A8")
    mins, secs = divmod(el, 60)

    grace = int(st.session_state.get("grace_time_sec", 15))
    stop_note = f"{label} — auto-stops {grace}s after red" if grace > 0 else f"{label} — auto-stops at red"

    st.markdown(
        f'<div style="text-align:center; padding:0.5rem 0;">'
        f'<span style="font-size:1.8rem; font-weight:800; font-family:monospace; '
        f'color:{color_hex};">{mins}:{secs:02d}</span>'
        f'<div style="font-size:0.7rem; color:#8892A8; margin-top:0.2rem;">{stop_note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Browser mic widget (unique key per speaker so it resets between turns) ──
    speaker_idx = st.session_state.get("speaker_index", 0)
    audio_data = st.audio_input(
        "Tap mic to record, tap again to stop",
        key=f"cloud_mic_{speaker_idx}",
    )

    # Save audio eagerly as soon as widget returns data.
    # This ensures auto-stop (timer expiry) can find the WAV on disk.
    if audio_data is not None and not st.session_state.get("_cloud_audio_processed"):
        wav_bytes = audio_data.getvalue()
        if len(wav_bytes) > 1024:
            save_cloud_audio(wav_bytes)
            st.session_state["_cloud_audio_processed"] = True

    if st.session_state.get("_cloud_audio_processed"):
        st.success("Audio saved! Tap **Stop Speaking** or wait for auto-stop.")

    # ── Same button layout as local ──────────────────────
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.markdown('<span class="btn-color-red"></span>', unsafe_allow_html=True)
            if st.button("Stop Speaking", use_container_width=True, key="btn_stop_early"):
                listen_stop()
                stop_timer()
                st.session_state["awaiting_audio_stop"] = True
                st.session_state["system_state"] = "thinking"
                st.session_state["system_state_note"] = "Finalizing audio"
                st.session_state["autopilot_phase"] = "processing"
                st.rerun()
    with c2:
        _render_next_speaker_disabled("listen")


def _render_waiting_to_listen_controls(session_active):
    """Controls during prep countdown: Start Speaking override + countdown display."""
    question = (st.session_state.get("approved_question") or "").strip()
    if question:
        st.markdown(
            f'<div style="background:#141928; border:1px solid rgba(255,255,255,0.06); '
            f'border-radius:10px; padding:0.7rem 0.9rem; margin-bottom:0.5rem; '
            f'font-size:0.9rem; color:#E8ECF5; line-height:1.5;">'
            f'{question}</div>',
            unsafe_allow_html=True,
        )

    # Countdown display (handles TTS playback then prep countdown)
    prep_start = st.session_state.get("prep_countdown_start_ts", 0)
    prep_duration = int(st.session_state.get("prep_time_sec", 30))
    now = time.time()

    if prep_start > now:
        # TTS still playing — show dashes, not a countdown number
        countdown_color = "#7C5CFC"
        countdown_label = "Playing question..."
        countdown_time = "--:--"
    else:
        # Prep countdown active
        countdown_color = "#3498DB"
        countdown_label = "PREP — speaker thinking time"
        remaining = max(0, prep_duration - int(now - prep_start)) if prep_start > 0 else 0
        r_mins, r_secs = divmod(remaining, 60)
        countdown_time = f"{r_mins}:{r_secs:02d}"

    st.markdown(
        f'<div style="text-align:center; padding:0.5rem 0;">'
        f'<span style="font-size:1.8rem; font-weight:800; font-family:monospace; '
        f'color:{countdown_color};">{countdown_time}</span>'
        f'<div style="font-size:0.7rem; color:#8892A8; margin-top:0.2rem;">'
        f'{countdown_label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Start Speaking — override to skip prep countdown
    with st.container():
        st.markdown('<span class="btn-color-green"></span>', unsafe_allow_html=True)
        if st.button("Start Speaking", use_container_width=True,
                     type="primary", key="btn_start_speaking",
                     disabled=not session_active):
            st.session_state["prep_countdown_start_ts"] = 0.0
            listen_start()
            start_timer()
            st.session_state["system_state"] = "listening"
            st.session_state["system_state_note"] = "Recording speaker"
            st.session_state["autopilot_phase"] = "listening"
            st.rerun()

    # Regenerate + Skip
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
            if st.button("Regenerate", disabled=not session_active,
                         use_container_width=True, key="btn_regen_wait"):
                st.session_state["prep_countdown_start_ts"] = 0.0
                st.session_state["tts_audio_mp3"] = None
                st.session_state["autopilot_phase"] = "generating_question"
                st.rerun()
    with c2:
        with st.container():
            st.markdown('<span class="btn-color-dark"></span>', unsafe_allow_html=True)
            if st.button("Skip Speaker", disabled=not session_active,
                         use_container_width=True, key="btn_skip_wait"):
                st.session_state["prep_countdown_start_ts"] = 0.0
                skip_speaker(stop_timer)
                st.session_state["autopilot_phase"] = "generating_question"
                st.rerun()

    # Disabled Next Speaker preview
    _render_next_speaker_disabled("wait")


def _render_processing_status():
    """Show which processing step is currently running."""
    from audio_io import is_stop_inflight
    from stt import is_transcribe_inflight
    from summarizer import is_summarize_inflight
    from evaluator import is_eval_inflight

    if st.session_state.get("awaiting_audio_stop") or is_stop_inflight():
        stage = "Finalizing audio..."
    elif st.session_state.get("awaiting_transcribe") or is_transcribe_inflight():
        stage = "Transcribing speech..."
    elif st.session_state.get("awaiting_summarize") or is_summarize_inflight():
        stage = "Summarizing response..."
    elif st.session_state.get("awaiting_evaluate") or is_eval_inflight():
        stage = "Evaluating performance..."
    else:
        stage = "Processing..."

    st.markdown(
        f'<div style="text-align:center; padding:0.8rem 0;">'
        f'<div style="font-size:0.85rem; color:#00D4AA; font-weight:600;">{stage}</div>'
        f'<div style="font-size:0.7rem; color:#5A6478; margin-top:0.3rem;">Results will appear below</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Disabled Next Speaker preview
    _render_next_speaker_disabled("proc")


def _render_turn_complete_controls(session_active):
    """Controls for turn_complete wait-gate: Next Speaker/Finish + re-run buttons."""
    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    is_last = idx >= len(speakers) - 1

    # Primary: Next Speaker or Finish
    with st.container():
        st.markdown('<span class="btn-color-green"></span>', unsafe_allow_html=True)
        if is_last:
            if st.button("Finish Session", use_container_width=True,
                         type="primary", key="btn_finish_session"):
                end_session(stop_timer)
                st.session_state["autopilot_phase"] = "complete"
                st.switch_page("pages/results.py")
        else:
            if st.button("Next Speaker", use_container_width=True,
                         type="primary", key="btn_next_speaker"):
                next_speaker(stop_timer)
                st.session_state["autopilot_phase"] = "generating_question"
                st.rerun()

    # Re-run section
    st.markdown(
        '<div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; '
        'letter-spacing:1px; color:#5A6478; margin:0.5rem 0 0.2rem;">Re-process</div>',
        unsafe_allow_html=True,
    )
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        with st.container():
            st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
            if st.button("Re-transcribe", use_container_width=True, key="btn_retranscribe"):
                _trigger_retranscribe()
    with rc2:
        with st.container():
            st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
            if st.button("Re-summarize", use_container_width=True, key="btn_resummarize"):
                _trigger_resummarize()
    with rc3:
        with st.container():
            st.markdown('<span class="btn-color-orange"></span>', unsafe_allow_html=True)
            if st.button("Re-evaluate", use_container_width=True, key="btn_reevaluate"):
                _trigger_reevaluate()


# ── Re-trigger helpers ────────────────────────────────────

def _trigger_retranscribe():
    """Re-run transcription from turn_complete."""
    from audio_io import has_latest_wav, get_latest_wav_path
    from stt import start_transcribe_async, is_transcribe_inflight

    if is_transcribe_inflight():
        return
    if not has_latest_wav():
        return

    st.session_state["current_transcript"] = ""
    st.session_state["last_summary"] = ""
    st.session_state["evaluator_notes"] = ""
    st.session_state["coach_hint"] = ""
    st.session_state["awaiting_transcribe"] = True
    st.session_state["autopilot_phase"] = "processing"
    st.session_state["system_state"] = "thinking"
    st.session_state["system_state_note"] = "Re-transcribing"

    speaker = get_current_speaker() or "Unknown"
    ctx = context_summary_for_prompt()
    model = st.session_state.get("stt_model", "gpt-4o-mini-transcribe")
    wav_path = get_latest_wav_path()
    start_transcribe_async(
        wav_path=wav_path, model=model, prompt="",
        speaker=speaker, context=ctx,
    )
    st.rerun()


def _trigger_resummarize():
    """Re-run summarization from turn_complete."""
    from summarizer import start_summarize_async, is_summarize_inflight

    if is_summarize_inflight():
        return
    transcript = (st.session_state.get("current_transcript") or "").strip()
    if not transcript:
        return

    st.session_state["last_summary"] = ""
    st.session_state["evaluator_notes"] = ""
    st.session_state["coach_hint"] = ""
    st.session_state["awaiting_summarize"] = True
    st.session_state["autopilot_phase"] = "processing"
    st.session_state["system_state"] = "thinking"
    st.session_state["system_state_note"] = "Re-summarizing"

    theme = (st.session_state.get("theme") or "").strip()
    wod = (st.session_state.get("word_of_day") or "").strip()
    start_summarize_async(
        transcript=transcript, theme=theme,
        word_of_day=wod, model="gpt-4o-mini",
    )
    st.rerun()


def _trigger_reevaluate():
    """Re-run evaluation from turn_complete."""
    from evaluator import start_evaluate_async, is_eval_inflight

    if is_eval_inflight():
        return
    q = (st.session_state.get("approved_question") or "").strip()
    t = (st.session_state.get("current_transcript") or "").strip()
    if not q or not t:
        return

    st.session_state["evaluator_notes"] = ""
    st.session_state["coach_hint"] = ""
    st.session_state["awaiting_evaluate"] = True
    st.session_state["autopilot_phase"] = "processing"
    st.session_state["system_state"] = "thinking"
    st.session_state["system_state_note"] = "Re-evaluating"

    wod = (st.session_state.get("word_of_day") or "").strip()
    start_evaluate_async(
        question=q, transcript=t, word_of_day=wod,
        model=st.session_state.get("evaluator_model", "gpt-4o-mini"),
    )
    st.rerun()


# ── Formatters ───────────────────────────────────────────

def _processing_html(text: str) -> str:
    return (
        '<div class="processing">'
        '<span class="pulse-dot"></span>'
        f'<span class="proc-text">{text}</span>'
        '</div>'
    )


def _format_transcript(raw: str) -> str:
    import html as html_mod
    import re
    text = html_mod.escape(raw.strip())
    sentences = re.split(r'(?<=[.!?])\s+', text)
    paragraphs = []
    chunk = []
    for s in sentences:
        chunk.append(s)
        if len(chunk) >= 3:
            paragraphs.append(' '.join(chunk))
            chunk = []
    if chunk:
        paragraphs.append(' '.join(chunk))
    html_parts = ''.join(f'<p>{p}</p>' for p in paragraphs)
    return f'<div class="fmt-transcript">{html_parts}</div>'


def _format_summary(raw: str) -> str:
    import html as html_mod
    lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
    items = []
    for line in lines:
        clean = line.lstrip("-").lstrip("•").strip()
        if clean:
            items.append(f'<li>{html_mod.escape(clean)}</li>')
    if not items:
        return html_mod.escape(raw)
    return '<ul class="fmt-summary">' + "".join(items) + '</ul>'


def _format_evaluator(notes: str, hint: str) -> str:
    import html as html_mod
    import re
    full = " ".join(notes.strip().split())
    impression = ""
    strength = ""
    improvement = ""
    rephrase = ""
    wod_usage = ""

    patterns = [
        ("wod_usage",    r'(?:word\s+of\s+(?:the\s+)?day)\s*(?:usage)?\s*:\s*'),
        ("rephrase",     r'(?:(?:a\s+)?suggested\s+)?rephrase\s*(?:could\s+be)?\s*:\s*'),
        ("improvement",  r'(?:to\s+)?improve(?:ment)?\s*[:,]\s*'),
        ("strength",     r'(?:one\s+)?strength\s*(?:is)?\s*:\s*'),
    ]
    remaining = full
    for slot, pat in patterns:
        m = re.search(pat, remaining, re.IGNORECASE)
        if m:
            value = remaining[m.end():].strip()
            remaining = remaining[:m.start()].strip()
            if slot == "wod_usage":
                wod_usage = value
            elif slot == "rephrase":
                rephrase = value
            elif slot == "improvement":
                improvement = value
            elif slot == "strength":
                strength = value
    impression = remaining.strip()

    for slot_text, trimmer in [
        (improvement, r'\.\s*(?:a\s+)?(?:suggested\s+)?rephrase'),
        (improvement, r'\.\s*word\s+of\s+(?:the\s+)?day'),
        (strength,    r'\.\s*(?:to\s+)?improve'),
    ]:
        if slot_text:
            m2 = re.search(trimmer, slot_text, re.IGNORECASE)
            if m2:
                leftover = slot_text[m2.start() + 1:].strip()
                trimmed = slot_text[:m2.start() + 1].strip()
                if trimmer.startswith(r'\.\s*(?:to\s+)?improve'):
                    strength = trimmed
                    if not improvement:
                        improvement = re.sub(r'^(?:to\s+)?improve(?:ment)?\s*[:,]\s*', '', leftover, flags=re.IGNORECASE).strip()
                else:
                    improvement = trimmed

    good_items = []
    if impression:
        good_items.append(f'<p>{html_mod.escape(impression)}</p>')
    if strength:
        good_items.append(f'<p>{html_mod.escape(strength)}</p>')
    good_body = "".join(good_items) if good_items else '<p class="eval-empty">--</p>'

    improve_items = []
    if improvement:
        improve_items.append(f'<p>{html_mod.escape(improvement)}</p>')
    skip_rephrase = {"no rephrase needed", "no rephrase needed.", "n/a", "-", "none", "none."}
    if rephrase and rephrase.lower().strip(".") not in {s.strip(".") for s in skip_rephrase}:
        clean_rp = re.sub(r'^["\'\u201c(]+', '', rephrase).strip()
        clean_rp = re.sub(r'["\'\u201d)]+$', '', clean_rp).strip()
        if clean_rp:
            improve_items.append(f'<p class="eval-rephrase">Try: &ldquo;{html_mod.escape(clean_rp)}&rdquo;</p>')
    improve_body = "".join(improve_items) if improve_items else '<p class="eval-empty">Nothing major</p>'

    notes_items = []
    if wod_usage:
        notes_items.append(f'<p><span class="eval-tag">WoD</span> {html_mod.escape(wod_usage.rstrip(".").strip())}</p>')
    if hint:
        notes_items.append(f'<p><span class="eval-tag coach">Coach</span> {html_mod.escape(hint)}</p>')
    notes_body = "".join(notes_items) if notes_items else '<p class="eval-empty">--</p>'

    return (
        '<div class="fmt-evaluator">'
        f'<div class="eval-card eval-good"><div class="eval-card-head">What Went Well</div>{good_body}</div>'
        f'<div class="eval-card eval-improve"><div class="eval-card-head">To Improve</div>{improve_body}</div>'
        f'<div class="eval-card eval-notes"><div class="eval-card-head">Notes</div>{notes_body}</div>'
        '</div>'
    )


# ── Info Boxes ───────────────────────────────────────────

def render_live_info_boxes():
    """Render transcript / summary / evaluator info boxes."""
    transcript = (st.session_state.get("current_transcript") or "").strip()
    summary = (st.session_state.get("last_summary") or "").strip()
    notes = (st.session_state.get("evaluator_notes") or "").strip()
    hint = (st.session_state.get("coach_hint") or "").strip()

    awaiting_stop = st.session_state.get("awaiting_audio_stop", False)
    awaiting_tx = st.session_state.get("awaiting_transcribe", False)
    awaiting_sum = st.session_state.get("awaiting_summarize", False)
    awaiting_eval = st.session_state.get("awaiting_evaluate", False)

    b1, b2, b3 = st.columns(3, gap="medium")

    with b1:
        if awaiting_stop or awaiting_tx:
            stage = "Finalizing audio..." if awaiting_stop else "Transcribing..."
            t_body = _processing_html(stage)
        elif transcript:
            t_body = _format_transcript(transcript)
        else:
            t_body = '<span class="empty">No transcript yet</span>'
        st.markdown(
            f'<div class="live-info-box transcript">'
            f'<h4>Transcript</h4>'
            f'<div class="box-content">{t_body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with b2:
        if awaiting_sum:
            s_body = _processing_html("Summarizing...")
        elif summary:
            s_body = _format_summary(summary)
        else:
            s_body = '<span class="empty">No summary yet</span>'
        st.markdown(
            f'<div class="live-info-box summary">'
            f'<h4>Summary</h4>'
            f'<div class="box-content">{s_body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with b3:
        if awaiting_eval:
            e_body = _processing_html("Evaluating...")
        elif notes:
            e_body = _format_evaluator(notes, hint)
        else:
            e_body = '<span class="empty">No evaluation yet</span>'
        st.markdown(
            f'<div class="live-info-box evaluator">'
            f'<h4>Evaluation</h4>'
            f'<div class="box-content">{e_body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
