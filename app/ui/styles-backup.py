# app/ui/styles.py
import streamlit as st

_GLOBAL_CSS = """

<style>
/* ---------- Kill Streamlit chrome that causes top bars/strips ---------- */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* These are the usual suspects for the "mystery top strip" */
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* Sidebar off */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* ---------- App background (one continuous surface) ---------- */
html, body, .stApp {
  background: #F5F7FA !important;
  overflow-x: hidden !important;
}

/* Container sizing */
.main .block-container,
[data-testid="stMainBlockContainer"] {
  max-width: 1200px !important;
  padding-top: 0.8rem !important;
  padding-bottom: 2.2rem !important;
}

/* Remove phantom borders/boxes Streamlit sometimes wraps around blocks */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stElementContainer"],
.element-container {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

/* ---------- Page wrapper (one cohesive layout) ---------- */
.tt-wrap {
  width: 100%;
  margin: 0 auto;
  padding: 0.8rem 0 0;
}

/* Footer */
.tt-footer {
  width: min(980px, 100%);
  margin: 1.4rem auto 0;
  text-align: center;
  color: #97A6B5;
  font-size: 0.72rem;
  line-height: 1.4;
}

/* ===== Page title ===== */
.tt-page-title {
  text-align: center;
  font-size: 1.35rem;
  font-weight: 700;
  color: #1B3A5C;
  margin: 0.2rem 0 0.6rem;
}

/* ===== Compact navigation cluster ===== */
/* Constrain nav row to hero card width and center it */
[data-testid="stVerticalBlockBorderWrapper"]:has(.tt-topbar-logo) {
  max-width: min(980px, 100%) !important;
  margin-left: auto !important;
  margin-right: auto !important;
  margin-bottom: 0.4rem !important;
}

/* Logo badge */
.tt-topbar-logo {
  display: flex;
  align-items: center;
  justify-content: center;
}
.tt-topbar-badge {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1B3A5C;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #3B6B9B;
  flex-shrink: 0;
}
.tt-topbar-badge .inner {
  color: #fff;
  font-weight: 900;
  text-transform: uppercase;
  font-size: 0.48rem;
  line-height: 1.05;
  text-align: center;
}
.tt-topbar-badge .inner .big {
  display: block;
  font-size: 0.82rem;
  letter-spacing: 1px;
  margin-bottom: 1px;
}

/* Nav buttons: pill-shaped, calm */
[data-testid="stVerticalBlockBorderWrapper"]:has(.tt-topbar-logo) .stButton > button {
  width: 100% !important;
  border-radius: 999px !important;
  padding: 0.5rem 1rem !important;
  background: rgba(255,255,255,0.75) !important;
  border: 1px solid #D9E0E7 !important;
  color: #1B3A5C !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.tt-topbar-logo) .stButton > button:hover {
  background: rgba(255,255,255,0.95) !important;
}

/* ===== Hero card like your mock ===== */
.tt-hero-card {
  width: min(980px, 100%);
  margin: 0.8rem auto 0;
  background: #FFFFFF;
  border: 1px solid #E6EBF0;
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.10);
  overflow: hidden;
}

.tt-hero-body {
  padding: 1.8rem 1.8rem 1.2rem;
  text-align: center;
}

.tt-hero-logo {
  margin: 0 auto 0.9rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #1B3A5C;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #3B6B9B;
  box-shadow: 0 0 0 4px rgba(27,58,92,0.10);
}

.tt-hero-title {
  font-size: 1.55rem;
  font-weight: 850;
  color: #1B3A5C;
  margin: 0.2rem 0 0.5rem;
}

.tt-hero-tagline {
  font-size: 0.95rem;
  color: #475569;
  margin: 0 0 0.4rem;
}

/* Divider band inside card */
.tt-hero-divider {
  height: 1px;
  background: #EDF2F7;
}

/* Feature cards row inside card */
.tt-feature-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.9rem;
  padding: 1.1rem 1.2rem 1.3rem;
  background: #F8FAFC;
}

.tt-feature-card {
  background: #FFFFFF;
  border: 1px solid #E6EBF0;
  border-radius: 12px;
  padding: 0.95rem 0.95rem;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
}

.tt-feature-card h4 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
  font-weight: 850;
  color: #1B3A5C;
}

.tt-feature-card p {
  margin: 0;
  font-size: 0.80rem;
  color: #475569;
  line-height: 1.35;
}

/* ===== HTML CTA buttons (anchors) ===== */
.tt-cta{
  width: min(520px, 100%);
  margin: 1.1rem auto 0;
  display: grid;
  gap: 0.65rem;
}
.tt-cta a {
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}
.tt-btn-primary,
.tt-btn-secondary{
  display: block;
  text-align: center;
  text-decoration: none !important;
  border-radius: 999px;
  padding: 0.65rem 2.2rem;
  font-size: 1.0rem;
  font-weight: 700;
}

.tt-btn-primary{
  background: #3B6B9B;
  border: 1px solid #3B6B9B;
  color: #fff !important;
}
.tt-btn-primary:hover{
  background: #2C5A85;
  border-color: #2C5A85;
}

.tt-btn-secondary{
  background: rgba(255,255,255,0.75);
  border: 1px solid #D9E0E7;
  color: #1B3A5C !important;
}
.tt-btn-secondary:hover{
  background: rgba(255,255,255,0.95);
}

/* Responsive */
@media (max-width: 900px) {
  .tt-feature-row { grid-template-columns: 1fr; }
}
</style>
"""

_SETUP_CSS = """
<style>
/* ===== Setup page: card containers via :has() ===== */
.setup-card { display: none; }

[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-card) {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 1rem 1.3rem 1.2rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06) !important;
}

/* Card titles — italic navy, thin bottom border */
.setup-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1B3A5C;
    font-style: italic;
    margin: 0 0 0.5rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid #EDF2F7;
}

/* ===== Setup page: green "Start Live Session" button ===== */
.setup-actions-marker { display: none; }

[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-actions-marker)
    [data-testid="stBaseButton-primary"] {
    background-color: #2E7D32 !important;
    border-color: #2E7D32 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-actions-marker)
    [data-testid="stBaseButton-primary"]:hover {
    background-color: #1B5E20 !important;
    border-color: #1B5E20 !important;
}

/* Save Setup button: outlined, calm */
[data-testid="stVerticalBlockBorderWrapper"]:has(.setup-actions-marker)
    [data-testid="stBaseButton-secondary"] {
    border-radius: 8px !important;
    border: 1px solid #CBD5E1 !important;
    color: #1B3A5C !important;
    font-weight: 600 !important;
}

/* ===== Setup page: speaker rows ===== */
.setup-speaker-row {
    padding: 0.3rem 0.5rem;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.9rem;
    color: #334155;
}
</style>
"""


def inject_setup_styles() -> None:
    """Inject setup-page-specific CSS on every rerun."""
    st.markdown(_SETUP_CSS, unsafe_allow_html=True)


def inject_global_styles() -> None:
    """
    Inject global CSS on every rerun.
    Streamlit rebuilds the DOM each rerun, so the <style> tag must be
    re-emitted every time — a session-state guard would skip injection
    after the first run, leaving subsequent reruns unstyled.
    """
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

