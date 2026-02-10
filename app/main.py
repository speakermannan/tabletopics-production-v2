# app/main.py — Production v1 Entry Point (router only)
#
# IMPORTANT:
# - Do NOT render UI here (no st.markdown, no st_autorefresh, no widgets)
# - If you render anything here, it can create "phantom" layout artifacts.
# - Keep this file as a clean router into pages/home.py

import sys
import os

# Ensure app/ directory is on sys.path for all page imports
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from paths import ensure_dirs
from state import (
    init_session_state,
    load_speakers_file,
    load_fallback_questions,
)

# =============================================
# Page config (must be first Streamlit command)
# =============================================
st.set_page_config(
    page_title="AI Table Topics Co-Host",
    page_icon="TT",
    layout="wide",
)

# =============================================
# Init (NO UI here)
# =============================================
ensure_dirs()
init_session_state()

# Preload once (NO UI)
if not st.session_state.get("speakers_file_list"):
    st.session_state["speakers_file_list"] = load_speakers_file()
if not st.session_state.get("fallback_questions"):
    st.session_state["fallback_questions"] = load_fallback_questions()

# =============================================
# Route immediately (NO UI before this)
# =============================================
st.switch_page("pages/home.py")