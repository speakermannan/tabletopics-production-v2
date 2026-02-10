# app/pages/setup.py
import streamlit as st
from ui.ui_shell import render_header, inject_custom_css, render_sidebar
from ui.styles import inject_setup_styles
from state import (
    parse_speakers,
    can_start_session,
    start_session,
    load_speakers_file,
    load_fallback_questions,
    TONE_OPTIONS,
    QUESTION_STYLES,
    TIME_LIMIT_OPTIONS,
    TTS_VOICES,
    TOPIC_PACKS,
    DIFFICULTY_LEVELS,
)
from timer import stop_timer
from tts import generate_tts_mp3

inject_custom_css()
inject_setup_styles()
render_sidebar()
render_header("Configure your Table Topics session")

# Ensure speakers file list is loaded
if not st.session_state.get("speakers_file_list"):
    st.session_state["speakers_file_list"] = load_speakers_file()
if not st.session_state.get("fallback_questions"):
    st.session_state["fallback_questions"] = load_fallback_questions()

# ============================================================
# TWO-COLUMN LAYOUT
# ============================================================
left_col, right_col = st.columns(2, gap="medium")

# ────────────────────────────────────────────────────────────
# LEFT COLUMN
# ────────────────────────────────────────────────────────────
with left_col:

    # ── Card: Meeting Setup ──────────────────────────────────
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Meeting Setup</div>', unsafe_allow_html=True)

        st.session_state["prompt_mode"] = st.selectbox(
            "Prompt Mode",
            ["Theme + Word", "Topic Pack"],
            index=0 if st.session_state.get("prompt_mode") == "Theme + Word" else 1,
            key="setup_prompt_mode",
        )

        if st.session_state["prompt_mode"] == "Theme + Word":
            st.session_state["theme"] = st.text_input(
                "Theme",
                value=st.session_state.get("theme", ""),
                placeholder="e.g., Community, Leadership, Innovation",
                key="setup_theme",
            )
            st.session_state["word_of_day"] = st.text_input(
                "Word of the Day",
                value=st.session_state.get("word_of_day", ""),
                placeholder="e.g., Resilience, Empathy",
                key="setup_wod",
            )
        else:
            st.session_state["topic_pack"] = st.selectbox(
                "Topic Pack",
                TOPIC_PACKS,
                index=TOPIC_PACKS.index(st.session_state.get("topic_pack", TOPIC_PACKS[0]))
                if st.session_state.get("topic_pack") in TOPIC_PACKS
                else 0,
                key="setup_topic_pack",
            )
            st.session_state["topic_difficulty"] = st.selectbox(
                "Difficulty",
                DIFFICULTY_LEVELS,
                index=DIFFICULTY_LEVELS.index(st.session_state.get("topic_difficulty", "Medium"))
                if st.session_state.get("topic_difficulty") in DIFFICULTY_LEVELS
                else 1,
                key="setup_difficulty",
            )

        st.session_state["tone"] = st.selectbox(
            "Tone",
            TONE_OPTIONS,
            index=TONE_OPTIONS.index(st.session_state.get("tone", "Neutral"))
            if st.session_state.get("tone") in TONE_OPTIONS
            else 0,
            key="setup_tone",
        )
        st.session_state["question_style"] = st.selectbox(
            "Question Style",
            QUESTION_STYLES,
            index=QUESTION_STYLES.index(st.session_state.get("question_style", "Mixed"))
            if st.session_state.get("question_style") in QUESTION_STYLES
            else 3,
            key="setup_q_style",
        )

    # ── Card: Audio & Settings ───────────────────────────────
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Audio & Settings</div>', unsafe_allow_html=True)

        # Mic device selector
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [
                f"{i}: {d['name']}" for i, d in enumerate(devices)
                if d.get("max_input_channels", 0) > 0
            ]
            if input_devices:
                selected_mic = st.selectbox(
                    "Microphone",
                    options=["Default"] + input_devices,
                    index=0,
                    key="setup_mic",
                )
                st.session_state["mic_device"] = selected_mic
            else:
                st.caption("No input devices found")
        except Exception:
            st.caption("Audio device detection unavailable")

        st.session_state["tts_voice"] = st.selectbox(
            "TTS Voice",
            TTS_VOICES,
            index=TTS_VOICES.index(st.session_state.get("tts_voice", "alloy"))
            if st.session_state.get("tts_voice") in TTS_VOICES
            else 0,
            key="setup_tts_voice",
        )

        if st.button("Test Voice", key="setup_test_voice"):
            try:
                audio = generate_tts_mp3(
                    "Welcome to Table Topics. Let's get started!",
                    voice=st.session_state.get("tts_voice", "alloy"),
                )
                st.audio(audio, format="audio/mp3")
            except Exception as e:
                st.error(f"TTS test failed: {e}")

        # Time Limit per Speaker
        time_labels = list(TIME_LIMIT_OPTIONS.keys())
        current_sec = st.session_state.get("timer_target_sec", 90)
        # Find closest label
        default_label = "1:30"
        for label, sec in TIME_LIMIT_OPTIONS.items():
            if sec == current_sec:
                default_label = label
                break

        selected_time = st.selectbox(
            "Time Limit per Speaker",
            time_labels,
            index=time_labels.index(default_label),
            key="setup_time_limit",
        )
        st.session_state["timer_target_sec"] = TIME_LIMIT_OPTIONS[selected_time]

# ────────────────────────────────────────────────────────────
# RIGHT COLUMN
# ────────────────────────────────────────────────────────────
with right_col:

    # ── Card: Speaker Roster ─────────────────────────────────
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Speaker Roster</div>', unsafe_allow_html=True)

        speakers_file = st.session_state.get("speakers_file_list", [])

        if speakers_file:
            st.multiselect(
                "Pick speakers from file",
                options=speakers_file,
                key="speaker_picks",
            )
        else:
            st.caption("No speakers.txt found. Enter names manually below.")

        custom_speakers = st.text_area(
            "Or paste speaker names (one per line or comma-separated)",
            value="",
            height=80,
            key="setup_custom_speakers",
            placeholder="Alice\nBob\nCarol",
        )

        st.markdown("**Current Order**")
        cur = st.session_state.get("speaker_order", [])
        if cur:
            for i, name in enumerate(cur):
                st.markdown(
                    f'<div class="setup-speaker-row">{i+1}. {name}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No speakers added yet")

        # Speaker management buttons
        sb1, sb2 = st.columns(2)
        with sb1:
            if st.button("Add Selected", key="setup_add_sel"):
                picks = st.session_state.get("speaker_picks", [])
                if picks:
                    cur = st.session_state.get("speaker_order", [])
                    for name in picks:
                        if name not in cur:
                            cur.append(name)
                    st.session_state["speaker_order"] = cur
                    st.rerun()

        with sb2:
            if st.button("Add Custom", key="setup_add_custom"):
                raw = st.session_state.get("setup_custom_speakers", "")
                if raw.strip():
                    # Handle both comma-separated and newline-separated
                    names = []
                    for line in raw.replace(",", "\n").splitlines():
                        name = line.strip()
                        if name:
                            names.append(name)
                    cur = st.session_state.get("speaker_order", [])
                    for name in names:
                        if name not in cur:
                            cur.append(name)
                    st.session_state["speaker_order"] = cur
                    st.rerun()

        sb3, sb4 = st.columns(2)
        with sb3:
            if st.button("Clear All", key="setup_clear_speakers"):
                st.session_state["speaker_order"] = []
                st.rerun()

        with sb4:
            if st.button("Reload File", key="setup_reload"):
                st.session_state["speakers_file_list"] = load_speakers_file()
                st.rerun()

        # Reorder controls
        cur = st.session_state.get("speaker_order", [])
        if len(cur) > 1:
            move_idx = st.number_input(
                "Move speaker # (1-based)",
                min_value=1,
                max_value=len(cur),
                value=1,
                step=1,
                key="setup_move_idx",
            )
            m1, m2 = st.columns(2)
            with m1:
                if st.button("Move Up", key="setup_move_up"):
                    i = int(move_idx) - 1
                    if i > 0:
                        cur[i - 1], cur[i] = cur[i], cur[i - 1]
                        st.session_state["speaker_order"] = cur
                        st.rerun()
            with m2:
                if st.button("Move Down", key="setup_move_down"):
                    i = int(move_idx) - 1
                    if i < len(cur) - 1:
                        cur[i + 1], cur[i] = cur[i], cur[i + 1]
                        st.session_state["speaker_order"] = cur
                        st.rerun()

    # ── Card: Privacy & Settings ─────────────────────────────
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Privacy & Settings</div>', unsafe_allow_html=True)

        st.session_state["panel_mode"] = st.checkbox(
            "Panel Mode (follow-up references previous speaker)",
            value=bool(st.session_state.get("panel_mode", False)),
            key="setup_panel_mode",
        )

        st.session_state["avoid_sensitive"] = st.checkbox(
            "Avoid sensitive topics",
            value=bool(st.session_state.get("avoid_sensitive", True)),
            key="setup_avoid_sensitive",
        )

        st.session_state["require_wod_reminder"] = st.checkbox(
            "Require Word of Day (gentle reminder)",
            value=bool(st.session_state.get("require_wod_reminder", True)),
            key="setup_require_wod",
        )

# ============================================================
# BOTTOM ACTIONS (centered)
# ============================================================
st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

with st.container():
    st.markdown('<span class="setup-actions-marker"></span>', unsafe_allow_html=True)
    _, act1, act2, _ = st.columns([1.5, 1, 1.2, 1.5])
    with act1:
        if st.button("Save Setup", use_container_width=True, key="setup_save"):
            # Apply speaker order to session
            cur = st.session_state.get("speaker_order", [])
            if cur:
                order_str = ", ".join(cur)
                st.session_state["speakers_raw"] = order_str
                st.session_state["speakers"] = parse_speakers(order_str)
                st.session_state["speaker_summaries"] = [""] * len(st.session_state["speakers"])
            st.success("Setup saved!")

    with act2:
        if st.button("Start Live Session", use_container_width=True, type="primary", key="setup_start"):
            # Apply speaker order
            cur = st.session_state.get("speaker_order", [])
            if cur:
                order_str = ", ".join(cur)
                st.session_state["speakers_raw"] = order_str
                st.session_state["speakers"] = parse_speakers(order_str)

            # Validate
            mode = st.session_state.get("prompt_mode", "Theme + Word")
            errors = []
            if mode == "Theme + Word":
                if not (st.session_state.get("theme") or "").strip():
                    errors.append("Theme is required")
                if not (st.session_state.get("word_of_day") or "").strip():
                    errors.append("Word of the Day is required")
            else:
                if not (st.session_state.get("topic_pack") or "").strip():
                    errors.append("Topic Pack is required")

            if not st.session_state.get("speakers"):
                errors.append("At least one speaker is required")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                start_session(stop_timer)
                st.session_state["system_state"] = "ready"
                st.session_state["system_state_note"] = "Session started"
                st.switch_page("pages/live.py")
