# app/pages/setup.py — V2 Streamlined Quick-Start Setup
import streamlit as st
from ui.styles import inject_setup_styles
from ui.shell import render_shell_start, render_shell_end
from state import (
    parse_speakers,
    start_session,
    load_speakers_file,
    load_fallback_questions,
    TONE_OPTIONS,
    QUESTION_STYLES,
    TIME_LIMIT_OPTIONS,
    TTS_VOICES,
    TTS_MODELS,
    _GPT4O_MINI_TTS_ONLY,
    TOPIC_PACKS,
    DIFFICULTY_LEVELS,
    PREP_TIME_OPTIONS,
    GRACE_TIME_OPTIONS,
)
from timer import stop_timer
from tts import generate_tts_mp3

render_shell_start(active="setup")
inject_setup_styles()

# Preload
if not st.session_state.get("speakers_file_list"):
    st.session_state["speakers_file_list"] = load_speakers_file()
if not st.session_state.get("fallback_questions"):
    st.session_state["fallback_questions"] = load_fallback_questions()

# Two-column layout
left_col, right_col = st.columns(2, gap="medium")

# ── LEFT COLUMN ────────────────────────────────────────────
with left_col:

    # Card: Session Theme
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Session Theme</div>', unsafe_allow_html=True)

        st.session_state["prompt_mode"] = st.selectbox(
            "Mode",
            ["Theme + Word", "Topic Pack"],
            index=0 if st.session_state.get("prompt_mode") == "Theme + Word" else 1,
            key="setup_prompt_mode",
        )

        if st.session_state["prompt_mode"] == "Theme + Word":
            st.session_state["theme"] = st.text_input(
                "Theme",
                value=st.session_state.get("theme", ""),
                placeholder="e.g., Community, Leadership",
                key="setup_theme",
            )
            st.session_state["word_of_day"] = st.text_input(
                "Word of the Day",
                value=st.session_state.get("word_of_day", ""),
                placeholder="e.g., Resilience",
                key="setup_wod",
            )
        else:
            st.session_state["topic_pack"] = st.selectbox(
                "Topic Pack",
                TOPIC_PACKS,
                index=TOPIC_PACKS.index(st.session_state.get("topic_pack", TOPIC_PACKS[0]))
                if st.session_state.get("topic_pack") in TOPIC_PACKS else 0,
                key="setup_topic_pack",
            )
            st.session_state["topic_difficulty"] = st.selectbox(
                "Difficulty",
                DIFFICULTY_LEVELS,
                index=DIFFICULTY_LEVELS.index(st.session_state.get("topic_difficulty", "Medium"))
                if st.session_state.get("topic_difficulty") in DIFFICULTY_LEVELS else 1,
                key="setup_difficulty",
            )

        tc1, tc2 = st.columns(2)
        with tc1:
            st.session_state["tone"] = st.selectbox(
                "Tone", TONE_OPTIONS,
                index=TONE_OPTIONS.index(st.session_state.get("tone", "Neutral"))
                if st.session_state.get("tone") in TONE_OPTIONS else 0,
                key="setup_tone",
            )
        with tc2:
            st.session_state["question_style"] = st.selectbox(
                "Style", QUESTION_STYLES,
                index=QUESTION_STYLES.index(st.session_state.get("question_style", "Mixed"))
                if st.session_state.get("question_style") in QUESTION_STYLES else 3,
                key="setup_q_style",
            )

    # Card: Voice & Timer
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Voice & Timer</div>', unsafe_allow_html=True)

        vc1, vc2 = st.columns([2, 1])
        with vc1:
            st.session_state["tts_voice"] = st.selectbox(
                "Voice", TTS_VOICES,
                index=TTS_VOICES.index(st.session_state.get("tts_voice", "nova"))
                if st.session_state.get("tts_voice") in TTS_VOICES else 0,
                key="setup_tts_voice",
            )
        with vc2:
            st.session_state["tts_model"] = st.selectbox(
                "Model", TTS_MODELS,
                index=TTS_MODELS.index(st.session_state.get("tts_model", "tts-1"))
                if st.session_state.get("tts_model") in TTS_MODELS else 0,
                key="setup_tts_model",
            )

        # Auto-upgrade for gpt-4o-mini-tts voices
        chosen_voice = st.session_state.get("tts_voice", "nova")
        if chosen_voice in _GPT4O_MINI_TTS_ONLY and st.session_state.get("tts_model") != "gpt-4o-mini-tts":
            st.session_state["tts_model"] = "gpt-4o-mini-tts"
            st.caption(f"Model auto-switched to gpt-4o-mini-tts for {chosen_voice}")

        if st.button("Test Voice", key="setup_test_voice"):
            try:
                audio = generate_tts_mp3(
                    "Welcome to Table Topics. Let's get started!",
                    model=st.session_state.get("tts_model", "tts-1"),
                    voice=st.session_state.get("tts_voice", "nova"),
                )
                st.audio(audio, format="audio/mp3")
            except Exception as e:
                st.error(f"TTS test failed: {e}")

        time_labels = list(TIME_LIMIT_OPTIONS.keys())
        current_sec = st.session_state.get("timer_target_sec", 90)
        default_label = "1:30"
        for label, sec in TIME_LIMIT_OPTIONS.items():
            if sec == current_sec:
                default_label = label
                break
        selected_time = st.selectbox(
            "Time per Speaker", time_labels,
            index=time_labels.index(default_label),
            key="setup_time_limit",
        )
        st.session_state["timer_target_sec"] = TIME_LIMIT_OPTIONS[selected_time]

        # Prep Time (thinking time before speaker timer starts)
        prep_labels = list(PREP_TIME_OPTIONS.keys())
        current_prep = st.session_state.get("prep_time_sec", 30)
        default_prep_label = "30s"
        for plabel, psec in PREP_TIME_OPTIONS.items():
            if psec == current_prep:
                default_prep_label = plabel
                break
        selected_prep = st.selectbox(
            "Prep Time (thinking time before timer)",
            prep_labels,
            index=prep_labels.index(default_prep_label),
            key="setup_prep_time",
        )
        st.session_state["prep_time_sec"] = PREP_TIME_OPTIONS[selected_prep]

        # Grace Time (extra seconds after red before auto-stop)
        grace_labels = list(GRACE_TIME_OPTIONS.keys())
        current_grace = st.session_state.get("grace_time_sec", 15)
        default_grace_label = "15s"
        for glabel, gsec in GRACE_TIME_OPTIONS.items():
            if gsec == current_grace:
                default_grace_label = glabel
                break
        selected_grace = st.selectbox(
            "Grace Period (extra time after red before auto-stop)",
            grace_labels,
            index=grace_labels.index(default_grace_label),
            key="setup_grace_time",
        )
        st.session_state["grace_time_sec"] = GRACE_TIME_OPTIONS[selected_grace]

# ── RIGHT COLUMN ───────────────────────────────────────────
with right_col:

    # Card: Speakers
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Speakers</div>', unsafe_allow_html=True)

        speakers_file = st.session_state.get("speakers_file_list", [])
        if speakers_file:
            st.multiselect("Pick from file", options=speakers_file, key="speaker_picks")
        else:
            st.caption("No speakers.txt found")

        custom_speakers = st.text_area(
            "Or type names (comma or newline)",
            value="", height=68, key="setup_custom_speakers",
            placeholder="Alice, Bob, Carol",
        )

        # Current roster
        st.markdown(
            '<div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; '
            'letter-spacing:1px; color:#8892A8; margin:0.3rem 0 0.2rem;">'
            'Current Roster</div>',
            unsafe_allow_html=True,
        )
        cur = st.session_state.get("speaker_order", [])
        if cur:
            rows_html = "".join(
                f'<div class="setup-speaker-row">'
                f'<span class="num">{i+1}</span>'
                f'<span class="name">{name}</span>'
                f'</div>'
                for i, name in enumerate(cur)
            )
            st.markdown(rows_html, unsafe_allow_html=True)
        else:
            st.caption("No speakers added")

        sb1, sb2, sb3, sb4 = st.columns(4)
        with sb1:
            if st.button("Add Picked", key="setup_add_sel", use_container_width=True):
                picks = st.session_state.get("speaker_picks", [])
                if picks:
                    cur = st.session_state.get("speaker_order", [])
                    for name in picks:
                        if name not in cur:
                            cur.append(name)
                    st.session_state["speaker_order"] = cur
                    st.rerun()
        with sb2:
            if st.button("Add Custom", key="setup_add_custom", use_container_width=True):
                raw = st.session_state.get("setup_custom_speakers", "")
                if raw.strip():
                    names = [line.strip() for line in raw.replace(",", "\n").splitlines() if line.strip()]
                    cur = st.session_state.get("speaker_order", [])
                    for name in names:
                        if name not in cur:
                            cur.append(name)
                    st.session_state["speaker_order"] = cur
                    st.rerun()
        with sb3:
            if st.button("Clear", key="setup_clear_speakers", use_container_width=True):
                st.session_state["speaker_order"] = []
                st.rerun()
        with sb4:
            if st.button("Reload", key="setup_reload", use_container_width=True):
                st.session_state["speakers_file_list"] = load_speakers_file()
                st.rerun()

        # Reorder
        cur = st.session_state.get("speaker_order", [])
        if len(cur) > 1:
            rc1, rc2, rc3 = st.columns([2, 1, 1])
            with rc1:
                move_idx = st.number_input("Move #", min_value=1, max_value=len(cur), value=1, step=1, key="setup_move_idx")
            with rc2:
                if st.button("Up", key="setup_move_up", use_container_width=True):
                    i = int(move_idx) - 1
                    if i > 0:
                        cur[i-1], cur[i] = cur[i], cur[i-1]
                        st.session_state["speaker_order"] = cur
                        st.rerun()
            with rc3:
                if st.button("Down", key="setup_move_down", use_container_width=True):
                    i = int(move_idx) - 1
                    if i < len(cur) - 1:
                        cur[i+1], cur[i] = cur[i], cur[i+1]
                        st.session_state["speaker_order"] = cur
                        st.rerun()

    # Card: Options
    with st.container():
        st.markdown('<span class="setup-card"></span>', unsafe_allow_html=True)
        st.markdown('<div class="setup-card-title">Options</div>', unsafe_allow_html=True)

        st.session_state["autopilot_enabled"] = st.checkbox(
            "Semi-Auto Mode (auto-generate + auto-process, manual play + advance)",
            value=bool(st.session_state.get("autopilot_enabled", True)),
            key="setup_autopilot",
        )
        st.session_state["avoid_sensitive"] = st.checkbox(
            "Avoid sensitive topics",
            value=bool(st.session_state.get("avoid_sensitive", True)),
            key="setup_avoid_sensitive",
        )
        st.session_state["panel_mode"] = st.checkbox(
            "Panel mode (follow-up references previous)",
            value=bool(st.session_state.get("panel_mode", False)),
            key="setup_panel_mode",
        )

# ── LAUNCH BUTTON ──────────────────────────────────────────
st.markdown(
    '<div style="height:1px; background:rgba(255,255,255,0.04); margin:1rem 0;"></div>',
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<span class="setup-launch-marker"></span>', unsafe_allow_html=True)
    _, center, _ = st.columns([1.5, 2, 1.5])
    with center:
        if st.button("Start Session", use_container_width=True, type="primary", key="setup_start"):
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
                if st.session_state.get("autopilot_enabled", True):
                    st.session_state["autopilot_phase"] = "generating_question"
                st.switch_page("pages/live.py")

render_shell_end()
