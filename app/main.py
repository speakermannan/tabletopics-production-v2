# app/main.py — Production v1 Entry Point (router only)
#
# IMPORTANT:
# - Keep this file as a clean router into pages/home.py
# - Only exception: show a blocking error if API key is missing

import sys
import os

# Ensure app/ directory is on sys.path for all page imports
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

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
# API key: .env (local) → st.secrets (Cloud)
# =============================================
if not os.environ.get("OPENAI_API_KEY"):
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError, AttributeError):
        pass

if not os.environ.get("OPENAI_API_KEY"):
    st.error(
        "**OPENAI_API_KEY is not configured.**\n\n"
        "**Streamlit Cloud:** Go to your app dashboard → "
        "**Settings** → **Secrets** and add:\n\n"
        '```\nOPENAI_API_KEY = "sk-your-key-here"\n```\n\n'
        "**Local:** Create a `.env` file in the project root with:\n\n"
        '```\nOPENAI_API_KEY=sk-your-key-here\n```'
    )
    st.stop()

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
