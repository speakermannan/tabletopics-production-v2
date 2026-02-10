# app/pages/home.py — V2 Dark Landing
import streamlit as st
from state import load_speakers_file, load_fallback_questions
from ui.shell import render_shell_start, render_shell_end

# Handle CTA actions via query param
action = st.query_params.get("action")
if isinstance(action, list):
    action = action[0]

if action == "launch":
    st.query_params.clear()
    if not st.session_state.get("speakers_file_list"):
        st.session_state["speakers_file_list"] = load_speakers_file()
    if not st.session_state.get("fallback_questions"):
        st.session_state["fallback_questions"] = load_fallback_questions()
    st.switch_page("pages/setup.py")

if action == "demo":
    st.query_params.clear()
    st.session_state["theme"] = "Community"
    st.session_state["word_of_day"] = "Civic Duty"
    st.session_state["tone"] = "Neutral"
    st.session_state["question_style"] = "Mixed"
    demo_speakers = ["Alice", "Bob", "Carol", "David"]
    st.session_state["speakers_raw"] = ", ".join(demo_speakers)
    st.session_state["speakers"] = demo_speakers
    st.session_state["speaker_order"] = demo_speakers
    if not st.session_state.get("speakers_file_list"):
        st.session_state["speakers_file_list"] = load_speakers_file()
    if not st.session_state.get("fallback_questions"):
        st.session_state["fallback_questions"] = load_fallback_questions()
    st.switch_page("pages/setup.py")

# Shell
render_shell_start(active="home")

# Hero
hero_html = (
    '<div class="v2-hero">'
    '<div class="v2-hero-logo">TT</div>'
    '<h1>AI Table Topics</h1>'
    '<div class="tagline">'
    'Autopilot your Toastmasters Table Topics sessions.<br>'
    'Set the theme, add speakers, and let the AI handle everything.'
    '</div>'
    '<div class="v2-cta">'
    '<a class="cta-primary" href="?action=launch">Launch Session</a>'
    '<a class="cta-secondary" href="?action=demo">Quick Demo</a>'
    '</div>'
    '<div class="v2-features">'
    '<div class="v2-feature-card">'
    '<div class="v2-feature-icon" style="background:rgba(0,212,170,0.15); color:#00D4AA;">&#9889;</div>'
    '<h4>Autopilot Mode</h4>'
    '<p>Questions, TTS, recording, transcription, and evaluation — all automatic.</p>'
    '</div>'
    '<div class="v2-feature-card">'
    '<div class="v2-feature-icon" style="background:rgba(124,92,252,0.15); color:#7C5CFC;">&#127908;</div>'
    '<h4>Live Transcription</h4>'
    '<p>Real-time speech-to-text with AI-powered summaries and evaluations.</p>'
    '</div>'
    '<div class="v2-feature-card">'
    '<div class="v2-feature-icon" style="background:rgba(255,181,71,0.15); color:#FFB547;">&#128274;</div>'
    '<h4>100% Local</h4>'
    '<p>Audio and data stay on your machine. Privacy by design.</p>'
    '</div>'
    '</div>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

render_shell_end()
