# app/ui/ui_presenter.py — V2 Dark Presenter Panel
import time
import streamlit as st
from timer import elapsed_sec, stoplight_state


def render_presenter_view():
    """Render the left-column presenter view (cinematic dark theme)."""
    theme = (st.session_state.get("theme") or "").strip()
    wod = (st.session_state.get("word_of_day") or "").strip()

    if st.session_state.get("prompt_mode") == "Topic Pack":
        pack = (st.session_state.get("topic_pack") or "").strip()
        diff = (st.session_state.get("topic_difficulty") or "").strip()
        theme = f"{pack} ({diff})" if pack else theme
        wod = ""

    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    current_speaker = speakers[idx] if speakers and 0 <= idx < len(speakers) else "---"

    question = (st.session_state.get("approved_question") or "").strip()

    # Timer — format as M:SS digital display
    autopilot_phase = st.session_state.get("autopilot_phase", "idle")

    if autopilot_phase == "waiting_to_listen":
        prep_start = st.session_state.get("prep_countdown_start_ts", 0)
        prep_duration = int(st.session_state.get("prep_time_sec", 30))
        now = time.time()

        if prep_start > now:
            # TTS still playing — show dashes, not a number (avoids confusion)
            time_display = "--:--"
            label = "PLAYING"
            color_hex = "#7C5CFC"
        else:
            # Prep countdown active — counts down to 0
            remaining = max(0, prep_duration - int(now - prep_start)) if prep_start > 0 else prep_duration
            mins, secs = divmod(remaining, 60)
            time_display = f"{mins}:{secs:02d}"
            label = "PREP"
            color_hex = "#3498DB"
    else:
        el = elapsed_sec()
        tgt = int(st.session_state.get("timer_target_sec", 90))
        label, color = stoplight_state(el, tgt)
        mins, secs = divmod(el, 60)
        time_display = f"{mins}:{secs:02d}"

        # V2 dark-theme stoplight colors (neutral→green→orange→red)
        color_hex = {
            "neutral": "#8892A8",
            "green": "#00D4AA",
            "orange": "#FF6B35", "red": "#FF3366",
        }.get(color, "#8892A8")

    # Build WoD badge
    wod_badge = ""
    if wod:
        wod_badge = (
            '<div class="wod-badge">'
            f'<span class="wod-pill">Please use: &ldquo;{wod}&rdquo;</span>'
            '</div>'
        )

    # Build question area
    if question:
        q_inner = f'<span class="question-text">{question}</span>'
    else:
        q_inner = '<span class="question-empty">No question yet &mdash; generate one from the operator panel</span>'

    # Assemble presenter panel (no blank lines — CommonMark safe)
    html = (
        '<div class="presenter-panel">'
        '<div class="theme-strip">'
        f'<strong>Theme:</strong> {theme or "---"}'
        '<span class="sep">|</span>'
        f'<strong>Word of the Day:</strong> {wod or "---"}'
        '</div>'
        f'<div class="speaker-name">Now Speaking: <strong>{current_speaker}</strong></div>'
        '<div class="pres-divider"></div>'
        f'<div class="question-area">{q_inner}</div>'
        f'{wod_badge}'
        '<div class="pres-divider"></div>'
        '<div class="timer-row">'
        f'<span class="timer-light" style="background:{color_hex}; color:{color_hex};"></span>'
        f'<span class="timer-digits">{time_display}</span>'
        f'<span class="timer-label" style="color:{color_hex};">{label}</span>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

    # Audio player (if TTS generated)
    if st.session_state.get("tts_audio_mp3"):
        st.audio(st.session_state["tts_audio_mp3"], format="audio/mp3")
