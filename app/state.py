# app/state.py
import streamlit as st
from pathlib import Path

ALLOWED_SYSTEM_STATES = {"idle", "listening", "thinking", "ready", "speaking", "preparing"}

TOPIC_PACKS = [
    "Interview",
    "Games",
    "Leadership",
    "Workplace",
    "Personal Growth",
    "Ethics",
    "Travel",
    "Technology",
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

STT_MODELS = [
    "gpt-4o-mini-transcribe",
    "gpt-4o-transcribe",
    "whisper-1",
]

TTS_MODELS = [
    "tts-1",            # fast, good quality
    "tts-1-hd",         # slower, higher fidelity
    "gpt-4o-mini-tts",  # newest — all 13 voices, steerable
]

# Voices that require gpt-4o-mini-tts model
_GPT4O_MINI_TTS_ONLY = {"ballad", "verse", "marin", "cedar"}

TTS_VOICES = [
    # tts-1 / tts-1-hd voices
    "nova",       # bright, energetic female — great for kids
    "shimmer",    # warm, friendly female
    "fable",      # expressive, storytelling British
    "alloy",      # neutral, balanced
    "ash",        # soft, conversational
    "coral",      # warm, clear
    "sage",       # calm, measured
    "echo",       # cool, steady male
    "onyx",       # deep, authoritative male
    # gpt-4o-mini-tts only (richer, steerable)
    "ballad",     # melodic, expressive
    "verse",      # dynamic, versatile
    "marin",      # natural, approachable — OpenAI recommended
    "cedar",      # smooth, polished — OpenAI recommended
]

TONE_OPTIONS = ["Neutral", "Fun", "Deep", "Professional"]

QUESTION_STYLES = ["Scenario", "Personal", "Opinion", "Mixed"]

TIME_LIMIT_OPTIONS = {
    "1:00": 60,
    "1:30": 90,
    "2:00": 120,
}

PREP_TIME_OPTIONS = {
    "0s (no prep)": 0,
    "15s": 15,
    "30s": 30,
    "45s": 45,
    "60s": 60,
}

GRACE_TIME_OPTIONS = {
    "0s (no grace)": 0,
    "15s": 15,
    "30s": 30,
    "45s": 45,
    "60s": 60,
}

DEFAULT_STATE = {
    # Topic mode
    "prompt_mode": "Theme + Word",
    "topic_pack": "Interview",
    "topic_difficulty": "Medium",

    # Meeting setup
    "theme": "",
    "word_of_day": "",
    "tone": "Neutral",
    "question_style": "Mixed",
    "speakers_raw": "",
    "speakers": [],

    # Speaker management
    "speaker_index": 0,
    "speaker_summaries": [],
    "speaker_order": [],
    "speaker_picks": [],
    "speaker_order_index": 0,
    "speakers_file_list": [],
    "panel_mode": False,

    # Current turn
    "current_transcript": "",
    "proposed_question": "",
    "approved_question": "",
    "last_summary": "",

    # Session flow
    "system_state": "idle",
    "system_state_note": "",
    "session_started": False,
    "session_complete": False,

    # Timer
    "timer_running": False,
    "timer_start_ts": 0.0,
    "timer_target_sec": 90,

    # Prep countdown (thinking time before speaking)
    "prep_time_sec": 30,
    "prep_countdown_start_ts": 0.0,

    # Grace period (extra seconds after red before auto-stop)
    "grace_time_sec": 15,

    # Audio & Voice
    "browser_recording": False,   # Legacy — kept for compat
    "_cloud_audio_processed": False,  # True after st.audio_input data is saved
    "mic_device": "",
    "tts_voice": "nova",
    "tts_model": "tts-1",
    "tts_pace": "tight",
    "tts_emphasize_wod": True,
    "tts_audio_mp3": None,
    "tts_last_text": "",
    "tts_last_error": "",

    # STT
    "stt_model": "gpt-4o-mini-transcribe",
    "stt_last_error": "",
    "last_transcript_file": "",

    # Summarizer
    "summarizer_last_error": "",
    "summarizer_used_llm": False,

    # Evaluator
    "evaluator_notes": "",
    "evaluator_last_error": "",
    "evaluator_model": "gpt-4o-mini",

    # Coach hint
    "coach_hint": "",
    "coach_hint_last_error": "",

    # Question controls
    "q_creativity": 50,
    "q_avoid_topics": "politics, religion, sex, violence",

    # Automation flags
    "auto_transcribe_on_stop": True,
    "auto_summarize_on_transcript": True,
    "auto_evaluate_on_summary": True,

    # Pipeline state
    "awaiting_audio_stop": False,
    "awaiting_transcribe": False,
    "awaiting_summarize": False,
    "awaiting_evaluate": False,

    # Guardrails
    "avoid_sensitive": True,
    "require_wod_reminder": True,

    # Results
    "speaker_results": [],

    # Fallback questions
    "fallback_questions": [],

    # Autopilot v2
    "autopilot_enabled": True,
    "autopilot_phase": "idle",
    # Phases: idle, generating_question, question_ready, speaking_question,
    #         waiting_to_listen, listening, processing, turn_complete, complete
    "autopilot_paused": False,
    "autopilot_advance_at": 0.0,  # timestamp for timed auto-advance
}


def init_session_state() -> None:
    for k, v in DEFAULT_STATE.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session() -> None:
    for k, v in DEFAULT_STATE.items():
        st.session_state[k] = v


def set_system_state(new_state: str, note: str = "") -> None:
    if new_state not in ALLOWED_SYSTEM_STATES:
        raise ValueError(f"Invalid system_state: {new_state}")
    st.session_state["system_state"] = new_state
    st.session_state["system_state_note"] = note


def parse_speakers(raw: str) -> list[str]:
    items = [s.strip() for s in raw.split(",")]
    cleaned, seen = [], set()
    for name in items:
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(name)
    return cleaned


def get_current_speaker() -> str:
    speakers = st.session_state.get("speakers", [])
    idx = st.session_state.get("speaker_index", 0)
    if not speakers or idx < 0 or idx >= len(speakers):
        return ""
    return speakers[idx]


def context_summary_for_prompt() -> str:
    mode = st.session_state.get("prompt_mode", "Theme + Word")
    if mode == "Theme + Word":
        theme = (st.session_state.get("theme") or "").strip()
        wod = (st.session_state.get("word_of_day") or "").strip()
        return f"Theme: {theme}. Word of the Day: {wod}."
    topic = (st.session_state.get("topic_pack") or "").strip()
    diff = (st.session_state.get("topic_difficulty") or "").strip()
    return f"Topic Pack: {topic}. Difficulty: {diff}."


def can_start_session() -> bool:
    has_speakers = len(st.session_state.get("speakers", [])) > 0
    mode = st.session_state.get("prompt_mode", "Theme + Word")

    if mode == "Theme + Word":
        return (
            bool((st.session_state.get("theme") or "").strip())
            and bool((st.session_state.get("word_of_day") or "").strip())
            and has_speakers
        )
    return bool((st.session_state.get("topic_pack") or "").strip()) and has_speakers


def start_session(stop_timer_fn) -> None:
    st.session_state["speaker_index"] = 0
    st.session_state["speaker_summaries"] = []
    st.session_state["current_transcript"] = ""
    st.session_state["proposed_question"] = ""
    st.session_state["approved_question"] = ""
    st.session_state["session_started"] = True
    st.session_state["session_complete"] = False
    st.session_state["speaker_results"] = []
    stop_timer_fn()
    set_system_state("idle")


def clear_turn_fields(stop_timer_fn) -> None:
    st.session_state["current_transcript"] = ""
    st.session_state["proposed_question"] = ""
    st.session_state["approved_question"] = ""
    st.session_state["stt_last_error"] = ""
    st.session_state["last_transcript_file"] = ""
    st.session_state["tts_audio_mp3"] = None
    st.session_state["tts_last_text"] = ""
    st.session_state["tts_last_error"] = ""
    st.session_state["last_summary"] = ""
    st.session_state["summarizer_last_error"] = ""
    st.session_state["coach_hint"] = ""
    st.session_state["coach_hint_last_error"] = ""
    st.session_state["evaluator_notes"] = ""
    st.session_state["evaluator_last_error"] = ""
    st.session_state["prep_countdown_start_ts"] = 0.0
    st.session_state["browser_recording"] = False
    st.session_state["_cloud_audio_processed"] = False
    stop_timer_fn()
    set_system_state("idle")


def _save_current_speaker_result() -> None:
    """Save the current speaker's results before moving to the next."""
    speaker = get_current_speaker()
    if not speaker:
        return

    result = {
        "name": speaker,
        "question": (st.session_state.get("approved_question") or "").strip(),
        "summary": (st.session_state.get("last_summary") or "").strip(),
        "evaluator_notes": (st.session_state.get("evaluator_notes") or "").strip(),
        "transcript": (st.session_state.get("current_transcript") or "").strip(),
        "coach_hint": (st.session_state.get("coach_hint") or "").strip(),
    }

    results = st.session_state.get("speaker_results", [])
    if not isinstance(results, list):
        results = []
    results.append(result)
    st.session_state["speaker_results"] = results


def next_speaker(stop_timer_fn) -> None:
    if not st.session_state.get("session_started"):
        return
    _save_current_speaker_result()
    if st.session_state["speaker_index"] < len(st.session_state.get("speakers", [])) - 1:
        st.session_state["speaker_index"] += 1
        clear_turn_fields(stop_timer_fn)


def skip_speaker(stop_timer_fn) -> None:
    next_speaker(stop_timer_fn)


def end_session(stop_timer_fn) -> None:
    """End the session and save the final speaker's results."""
    if not st.session_state.get("session_started"):
        return
    _save_current_speaker_result()
    st.session_state["session_complete"] = True
    stop_timer_fn()
    set_system_state("idle", "Session complete")


def get_question_constraints():
    from question_gen import QuestionConstraints

    avoid_raw = (st.session_state.get("q_avoid_topics") or "").strip()
    avoid_topics = [x.strip() for x in avoid_raw.split(",") if x.strip()]

    if st.session_state.get("avoid_sensitive", True):
        sensitive = ["politics", "religion", "sex", "violence"]
        for topic in sensitive:
            if topic not in [t.lower() for t in avoid_topics]:
                avoid_topics.append(topic)

    require_word = None
    if st.session_state.get("prompt_mode") == "Theme + Word":
        require_word = (st.session_state.get("word_of_day") or "").strip()

    return QuestionConstraints(
        creativity=int(st.session_state.get("q_creativity", 50)),
        max_seconds=int(st.session_state.get("timer_target_sec", 90)),
        avoid_topics=avoid_topics,
        require_word=require_word,
    )


def load_speakers_file(path=None) -> list[str]:
    if path is None:
        path = Path(__file__).parent / "prompts" / "speakers.txt"
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        return [s.strip() for s in lines if s.strip()]
    except Exception:
        return []


def load_fallback_questions(path=None) -> list[str]:
    if path is None:
        path = Path(__file__).parent / "prompts" / "fallback_questions.txt"
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        return [q.strip() for q in lines if q.strip()]
    except Exception:
        return []
