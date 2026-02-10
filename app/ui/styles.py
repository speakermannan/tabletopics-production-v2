# app/ui/styles.py — V2 Dark Mode Design System
import streamlit as st

# ─── Color Palette ───────────────────────────────────────
# bg-deep:      #0A0E1A   (page background)
# bg-surface:   #141928   (card background)
# bg-elevated:  #1C2237   (elevated cards, inputs)
# accent-cyan:  #00D4AA   (primary accent)
# accent-purple:#7C5CFC   (secondary accent)
# gradient:     #00D4AA → #7C5CFC
# text-primary: #E8ECF5
# text-secondary:#8892A8
# text-muted:   #5A6478
# border:       rgba(255,255,255,0.06)
# success:      #00D4AA
# warning:      #FFB547
# error:        #FF5A5A

_GLOBAL_CSS = """<style>
/* ========== Kill Streamlit chrome ========== */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* ========== Dark background ========== */
html, body, .stApp {
  background: #0A0E1A !important;
  color: #E8ECF5 !important;
  overflow-x: hidden !important;
}

/* Force dark text everywhere */
.stApp, .stApp > header, .stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .main .block-container,
[data-testid="stMainBlockContainer"] {
  background-color: #0A0E1A !important;
  color: #E8ECF5 !important;
}

/* Container sizing */
.main .block-container,
[data-testid="stMainBlockContainer"] {
  max-width: 1200px !important;
  padding-top: 0.6rem !important;
  padding-bottom: 2rem !important;
}

/* Remove phantom borders/boxes */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stElementContainer"],
.element-container {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* ========== Typography overrides ========== */
h1, h2, h3, h4, h5, h6 { color: #E8ECF5 !important; }
p, span, div, label { color: #E8ECF5; }
.stMarkdown { color: #E8ECF5 !important; }

/* Dark inputs — comprehensive BaseWeb overrides */
input, textarea {
  background-color: #1C2237 !important;
  color: #E8ECF5 !important;
  border-color: rgba(255,255,255,0.08) !important;
  caret-color: #00D4AA !important;
}
input::placeholder, textarea::placeholder {
  color: #5A6478 !important;
  opacity: 1 !important;
}

/* BaseWeb input wrapper */
[data-baseweb="input"] {
  background-color: #1C2237 !important;
  border-color: rgba(255,255,255,0.08) !important;
}
[data-baseweb="input"] > div {
  background-color: #1C2237 !important;
  border-color: rgba(255,255,255,0.08) !important;
}
[data-baseweb="base-input"] {
  background-color: #1C2237 !important;
  border-color: rgba(255,255,255,0.08) !important;
}

/* BaseWeb textarea wrapper */
[data-baseweb="textarea"] {
  background-color: #1C2237 !important;
  border-color: rgba(255,255,255,0.08) !important;
}
[data-baseweb="textarea"] > div {
  background-color: #1C2237 !important;
}

/* BaseWeb select — all nested layers */
[data-baseweb="select"] {
  background-color: #1C2237 !important;
  color: #E8ECF5 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-baseweb="select"] > div > div > div {
  background-color: #1C2237 !important;
  color: #E8ECF5 !important;
  border-color: rgba(255,255,255,0.08) !important;
}
/* Select arrow/indicator */
[data-baseweb="select"] svg {
  fill: #8892A8 !important;
}

/* Dropdown popover & menu */
[data-baseweb="popover"] {
  background-color: #1C2237 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 10px !important;
}
[data-baseweb="popover"] > div {
  background-color: #1C2237 !important;
}
[data-baseweb="menu"] {
  background-color: #1C2237 !important;
}
[role="listbox"] {
  background-color: #1C2237 !important;
}
/* Dropdown options — override BaseWeb inline highlight styles */
[role="option"],
[data-baseweb="menu"] li,
[data-baseweb="menu"] ul li {
  color: #E8ECF5 !important;
  background-color: #1C2237 !important;
}
[role="option"]:hover,
[role="option"][aria-selected="true"],
[role="option"]:focus,
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] li[aria-selected="true"],
[data-baseweb="menu"] li:focus,
li[aria-selected="true"],
li[data-highlighted="true"] {
  background-color: #252D45 !important;
  color: #00D4AA !important;
}
/* Catch BaseWeb's isHighlighted prop (renders as inline bg) */
[data-baseweb="menu"] [role="option"][style],
[role="listbox"] [role="option"][style] {
  background-color: #1C2237 !important;
}
[data-baseweb="menu"] [role="option"][style]:hover,
[data-baseweb="menu"] [role="option"][style]:focus,
[role="listbox"] [role="option"][style]:hover {
  background-color: #252D45 !important;
  color: #00D4AA !important;
}

/* Multiselect tags */
[data-baseweb="tag"] {
  background-color: rgba(0,212,170,0.15) !important;
  color: #00D4AA !important;
  border-color: rgba(0,212,170,0.3) !important;
}
[data-baseweb="tag"] span { color: #00D4AA !important; }
[data-baseweb="tag"] svg { fill: #00D4AA !important; }

/* Number input controls */
.stNumberInput button {
  background-color: #1C2237 !important;
  color: #E8ECF5 !important;
  border-color: rgba(255,255,255,0.08) !important;
}
.stNumberInput button:hover {
  background-color: #252D45 !important;
}

/* Focus state — cyan border */
input:focus, textarea:focus {
  border-color: #00D4AA !important;
  box-shadow: 0 0 0 1px rgba(0,212,170,0.3) !important;
}
[data-baseweb="select"]:focus-within > div {
  border-color: #00D4AA !important;
  box-shadow: 0 0 0 1px rgba(0,212,170,0.3) !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="input"]:focus-within > div {
  border-color: #00D4AA !important;
  box-shadow: 0 0 0 1px rgba(0,212,170,0.3) !important;
}

/* Dark selectbox labels */
.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stMultiSelect label,
.stNumberInput label,
.stCheckbox label {
  color: #8892A8 !important;
}

/* Checkbox */
.stCheckbox span { color: #E8ECF5 !important; }

/* Buttons: global dark style */
.stButton > button {
  background: #1C2237 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #E8ECF5 !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: #252D45 !important;
  border-color: rgba(0,212,170,0.3) !important;
}

/* Primary buttons: gradient */
.stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #00D4AA 0%, #7C5CFC 100%) !important;
  border: none !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 20px rgba(0,212,170,0.25) !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 6px 28px rgba(0,212,170,0.4) !important;
  transform: translateY(-1px);
}

/* Download buttons */
.stDownloadButton > button {
  background: #1C2237 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #E8ECF5 !important;
  border-radius: 10px !important;
}
.stDownloadButton > button:hover {
  border-color: rgba(0,212,170,0.3) !important;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Info/warning/error boxes */
[data-testid="stAlert"] {
  background: #141928 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  color: #E8ECF5 !important;
  border-radius: 10px !important;
}

/* Caption text */
.stCaption, [data-testid="stCaptionContainer"] {
  color: #5A6478 !important;
}

/* ========== Navigation bar ========== */
.v2-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0;
  margin-bottom: 0.6rem;
}
.v2-nav-logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 0.7rem;
  color: #FFFFFF;
  flex-shrink: 0;
  margin-right: 0.3rem;
}
.v2-nav-spacer { flex: 1; }

/* Nav buttons via :has() marker */
.v2-nav-marker { display: none; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.v2-nav-marker) {
  max-width: min(1000px, 100%) !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.v2-nav-marker) .stButton > button {
  border-radius: 999px !important;
  padding: 0.4rem 1rem !important;
  font-size: 0.78rem !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  color: #8892A8 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.v2-nav-marker) .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #E8ECF5 !important;
}
/* Active nav button */
[data-testid="stVerticalBlockBorderWrapper"]:has(.v2-nav-marker) .stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, rgba(0,212,170,0.15), rgba(124,92,252,0.15)) !important;
  border: 1px solid rgba(0,212,170,0.3) !important;
  color: #00D4AA !important;
  font-weight: 700 !important;
  box-shadow: none !important;
  transform: none !important;
}

/* ========== Footer ========== */
.v2-footer {
  text-align: center;
  padding: 1.5rem 0 0.5rem;
  color: #5A6478;
  font-size: 0.7rem;
  line-height: 1.5;
}
.v2-footer .accent {
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

/* ========== Glass card helper ========== */
.glass-card {
  background: rgba(20, 25, 40, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  overflow: hidden;
}

/* ========== Gradient text helper ========== */
.gradient-text {
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ========== Pulse animation ========== */
@keyframes v2Pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.85); }
  50% { opacity: 1; transform: scale(1.1); }
}
@keyframes v2Fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
@keyframes v2Glow {
  0%, 100% { box-shadow: 0 0 8px 2px currentColor; }
  50% { box-shadow: 0 0 20px 6px currentColor; }
}
@keyframes v2Spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .main .block-container,
  [data-testid="stMainBlockContainer"] {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }
}
</style>"""


_SETUP_CSS = """<style>
/* ========== Setup page: glass cards via :has() ========== */
.setup-card { display: none; }

[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker)) {
  background: rgba(20, 25, 40, 0.6) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 16px !important;
  padding: 1.2rem 1.4rem !important;
  margin-bottom: 0.8rem !important;
}

/* Tighten gap inside setup cards */
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  [data-testid="stVerticalBlock"] {
  gap: 0.5rem !important;
}

/* Card titles */
.setup-card-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin: 0 0 0.8rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Compact labels */
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stSelectbox label,
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stTextInput label,
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stTextArea label,
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stMultiSelect label,
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stNumberInput label,
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stCheckbox label {
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  color: #8892A8 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

/* Compact buttons */
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card):not(:has(.v2-nav-marker))
  .stButton > button {
  font-size: 0.76rem !important;
  padding: 0.3rem 0.7rem !important;
  border-radius: 8px !important;
}

/* ========== Setup: Launch button ========== */
.setup-launch-marker { display: none; }

[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-launch-marker):not(:has(.v2-nav-marker))
  [data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #00D4AA 0%, #7C5CFC 100%) !important;
  border: none !important;
  color: #FFFFFF !important;
  border-radius: 999px !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  padding: 0.7rem 2.5rem !important;
  box-shadow: 0 4px 20px rgba(0,212,170,0.3) !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-launch-marker):not(:has(.v2-nav-marker))
  [data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 8px 32px rgba(0,212,170,0.5) !important;
}

/* ========== Speaker chips ========== */
.setup-speaker-row {
  display: flex;
  align-items: center;
  padding: 0.35rem 0.6rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.85rem;
  color: #E8ECF5;
}
.setup-speaker-row .num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  color: #FFFFFF;
  font-size: 0.68rem;
  font-weight: 700;
  margin-right: 0.6rem;
  flex-shrink: 0;
}
.setup-speaker-row .name {
  font-weight: 500;
  color: #E8ECF5;
}
</style>"""


def inject_global_styles() -> None:
    """Inject global dark-mode CSS on every rerun."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def inject_setup_styles() -> None:
    """Inject setup-page-specific CSS on every rerun."""
    st.markdown(_SETUP_CSS, unsafe_allow_html=True)
