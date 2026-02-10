# app/ui/ui_shell.py — V2 Dark Component CSS
import streamlit as st


def inject_custom_css():
    st.markdown("""<style>
/* ========================================================
   V2 DARK MODE COMPONENT STYLES
   ======================================================== */

/* ---- Presenter panel (cinematic dark gradient) ---- */
.presenter-panel {
  background: linear-gradient(160deg, #0D1B2A 0%, #1B2838 40%, #0A1628 100%);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 0;
  min-height: 440px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
  position: relative;
}

/* Subtle gradient glow at top */
.presenter-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00D4AA, #7C5CFC, transparent);
  border-radius: 2px;
}

/* Theme strip */
.presenter-panel .theme-strip {
  background: rgba(255,255,255,0.04);
  padding: 0.6rem 1.6rem;
  font-size: 0.82rem;
  color: rgba(255,255,255,0.5);
  text-align: center;
  letter-spacing: 0.3px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.presenter-panel .theme-strip strong {
  color: #00D4AA;
  font-weight: 700;
}
.presenter-panel .theme-strip .sep {
  margin: 0 0.8rem;
  opacity: 0.3;
}

/* Speaker name */
.presenter-panel .speaker-name {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 400;
  color: rgba(255,255,255,0.6);
  padding: 1.4rem 1.8rem 0.7rem;
}
.presenter-panel .speaker-name strong {
  font-weight: 800;
  color: #FFFFFF;
}

/* Divider */
.presenter-panel .pres-divider {
  width: 60%;
  margin: 0 auto;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
}

/* Question area */
.presenter-panel .question-area {
  text-align: center;
  padding: 1.3rem 2.2rem;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.presenter-panel .question-text {
  font-size: 1.3rem;
  font-weight: 500;
  line-height: 1.6;
  color: #FFFFFF;
}
.presenter-panel .question-empty {
  opacity: 0.25;
  font-size: 0.95rem;
  font-style: italic;
  color: #8892A8;
}

/* WoD badge */
.presenter-panel .wod-badge {
  text-align: center;
  padding: 0.4rem 0 0.6rem;
}
.presenter-panel .wod-pill {
  display: inline-block;
  background: rgba(0,212,170,0.1);
  border: 1px solid rgba(0,212,170,0.25);
  color: #00D4AA;
  padding: 0.4rem 1.4rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* Timer — bold digital */
.presenter-panel .timer-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem 1.8rem 1.3rem;
  margin-top: auto;
  border-top: 1px solid rgba(255,255,255,0.04);
  background: rgba(0,0,0,0.15);
}
.presenter-panel .timer-light {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.15);
  flex-shrink: 0;
  animation: v2Glow 2s ease-in-out infinite;
}
.presenter-panel .timer-digits {
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', 'Menlo', monospace;
  font-size: 2.6rem;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 3px;
  text-shadow: 0 0 30px rgba(255,255,255,0.1);
  font-variant-numeric: tabular-nums;
}
.presenter-panel .timer-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  background: rgba(255,255,255,0.06);
}

/* ---- Autopilot status bar ---- */
.autopilot-bar {
  background: rgba(20, 25, 40, 0.8);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 0.7rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin: 0.6rem 0;
}
.autopilot-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00D4AA;
  flex-shrink: 0;
  animation: v2Pulse 1.5s ease-in-out infinite;
}
.autopilot-dot.paused {
  background: #FFB547;
  animation: none;
}
.autopilot-dot.complete {
  background: #7C5CFC;
  animation: none;
}
.autopilot-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #00D4AA;
}
.autopilot-label.paused { color: #FFB547; }
.autopilot-label.complete { color: #7C5CFC; }
.autopilot-phase {
  font-size: 0.78rem;
  color: #8892A8;
  margin-left: auto;
}

/* ---- Autopilot timeline ---- */
.autopilot-timeline {
  display: flex;
  gap: 0.3rem;
  padding: 0.5rem 0;
}
.at-step {
  flex: 1;
  height: 3px;
  border-radius: 2px;
  background: rgba(255,255,255,0.06);
  position: relative;
  overflow: hidden;
}
.at-step.done {
  background: linear-gradient(90deg, #00D4AA, #7C5CFC);
}
.at-step.active {
  background: rgba(255,255,255,0.08);
}
.at-step.active::after {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 50%;
  background: linear-gradient(90deg, #00D4AA, #7C5CFC);
  border-radius: 2px;
  animation: timelineProgress 1.5s ease-in-out infinite;
}
@keyframes timelineProgress {
  0% { width: 0%; }
  50% { width: 100%; }
  100% { width: 0%; }
}

/* ---- Controls panel (dark glass) ---- */
.controls-marker { display: none; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.controls-marker):not(:has(.v2-nav-marker)) {
  background: rgba(20, 25, 40, 0.6) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 16px !important;
  padding: 0.8rem 1rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.controls-marker):not(:has(.v2-nav-marker))
  [data-testid="stVerticalBlock"] {
  gap: 0.3rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.controls-marker):not(:has(.v2-nav-marker)) h3 {
  font-size: 0.85rem !important;
  margin: 0 0 0.3rem !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
}

/* ---- Button color markers ---- */
.btn-color-green, .btn-color-red, .btn-color-orange,
.btn-color-teal, .btn-color-dark { display: none; }

/* Cyan — primary action (Ask Q, Listen) */
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-green):not(:has(.controls-marker)) .stButton > button,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-teal):not(:has(.controls-marker)) .stButton > button {
  background: linear-gradient(135deg, #00D4AA, #00B894) !important;
  border: none !important;
  color: #0A0E1A !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-green):not(:has(.controls-marker)) .stButton > button:hover,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-teal):not(:has(.controls-marker)) .stButton > button:hover {
  box-shadow: 0 4px 16px rgba(0,212,170,0.3) !important;
}

/* Red — stop / end */
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-red):not(:has(.controls-marker)) .stButton > button {
  background: rgba(255,90,90,0.15) !important;
  border: 1px solid rgba(255,90,90,0.3) !important;
  color: #FF5A5A !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-red):not(:has(.controls-marker)) .stButton > button:hover {
  background: rgba(255,90,90,0.25) !important;
}

/* Purple — secondary (Follow-Up, Emergency Q) */
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-orange):not(:has(.controls-marker)) .stButton > button {
  background: rgba(124,92,252,0.15) !important;
  border: 1px solid rgba(124,92,252,0.3) !important;
  color: #7C5CFC !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-orange):not(:has(.controls-marker)) .stButton > button:hover {
  background: rgba(124,92,252,0.25) !important;
}

/* Gray — skip */
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-dark):not(:has(.controls-marker)) .stButton > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  color: #8892A8 !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-dark):not(:has(.controls-marker)) .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: #E8ECF5 !important;
}

/* Disabled state for all colored buttons */
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-green):not(:has(.controls-marker)) .stButton > button:disabled,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-red):not(:has(.controls-marker)) .stButton > button:disabled,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-orange):not(:has(.controls-marker)) .stButton > button:disabled,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-teal):not(:has(.controls-marker)) .stButton > button:disabled,
[data-testid="stVerticalBlockBorderWrapper"]:has(.btn-color-dark):not(:has(.controls-marker)) .stButton > button:disabled {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(255,255,255,0.04) !important;
  color: #5A6478 !important;
  cursor: not-allowed !important;
  opacity: 1 !important;
  box-shadow: none !important;
}

/* ---- Up-Next list ---- */
.up-next-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.2rem 0;
  font-size: 0.8rem;
  color: #8892A8;
}
.up-next-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  background: #7C5CFC;
}

/* ---- Live info boxes (dark glass with accent border) ---- */
.live-info-box {
  background: rgba(20, 25, 40, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 0.9rem 1.1rem;
  min-height: 120px;
  border-left: 3px solid rgba(255,255,255,0.06);
}
.live-info-box h4 {
  margin: 0 0 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.live-info-box .box-content {
  font-size: 0.82rem;
  line-height: 1.55;
  color: #C8CED8;
}
.live-info-box.transcript {
  border-left-color: #00D4AA;
}
.live-info-box.transcript h4 { color: #00D4AA; }
.live-info-box.summary {
  border-left-color: #7C5CFC;
}
.live-info-box.summary h4 { color: #7C5CFC; }
.live-info-box.evaluator {
  border-left-color: #FFB547;
}
.live-info-box.evaluator h4 { color: #FFB547; }
.live-info-box .empty {
  opacity: 0.3;
  font-style: italic;
  font-size: 0.8rem;
  color: #5A6478;
}

/* Processing indicators */
.live-info-box .processing {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0;
}
.live-info-box .processing .pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: v2Pulse 1.2s ease-in-out infinite;
}
.live-info-box.transcript .processing .pulse-dot { background: #00D4AA; }
.live-info-box.summary .processing .pulse-dot { background: #7C5CFC; }
.live-info-box.evaluator .processing .pulse-dot { background: #FFB547; }
.live-info-box .processing .proc-text {
  font-size: 0.82rem;
  font-weight: 600;
  animation: v2Fade 1.2s ease-in-out infinite;
}
.live-info-box.transcript .processing .proc-text { color: #00D4AA; }
.live-info-box.summary .processing .proc-text { color: #7C5CFC; }
.live-info-box.evaluator .processing .proc-text { color: #FFB547; }

/* ---- Transcript formatting ---- */
.fmt-transcript p {
  margin: 0 0 0.5rem;
  font-size: 0.84rem;
  line-height: 1.65;
  color: #C8CED8;
}
.fmt-transcript p:last-child { margin-bottom: 0; }

/* ---- Summary bullet list ---- */
.fmt-summary {
  list-style: none;
  padding: 0;
  margin: 0;
}
.fmt-summary li {
  position: relative;
  padding: 0.35rem 0 0.35rem 1.3rem;
  font-size: 0.84rem;
  line-height: 1.5;
  color: #C8CED8;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.fmt-summary li:last-child { border-bottom: none; }
.fmt-summary li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.65rem;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #7C5CFC;
}

/* ---- Evaluator mini-cards ---- */
.fmt-evaluator {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.eval-card {
  border-radius: 10px;
  padding: 0.5rem 0.7rem;
  background: rgba(255,255,255,0.02);
}
.eval-card-head {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 0.25rem;
}
.eval-card p {
  margin: 0 0 0.2rem;
  font-size: 0.8rem;
  line-height: 1.5;
  color: #C8CED8;
}
.eval-card p:last-child { margin-bottom: 0; }
.eval-rephrase {
  font-style: italic;
  color: #8892A8 !important;
  font-size: 0.78rem !important;
}
.eval-empty {
  opacity: 0.3;
  font-style: italic;
}

.eval-good {
  border-left: 3px solid #00D4AA;
}
.eval-good .eval-card-head { color: #00D4AA; }

.eval-improve {
  border-left: 3px solid #FFB547;
}
.eval-improve .eval-card-head { color: #FFB547; }

.eval-notes {
  border-left: 3px solid #7C5CFC;
}
.eval-notes .eval-card-head { color: #7C5CFC; }

.eval-tag {
  display: inline-block;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  background: rgba(0,212,170,0.15);
  color: #00D4AA;
  margin-right: 0.3rem;
  vertical-align: middle;
}
.eval-tag.coach {
  background: rgba(124,92,252,0.15);
  color: #7C5CFC;
}

/* ---- Results page ---- */
.results-header {
  background: rgba(20, 25, 40, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 1.2rem 1.6rem;
  margin-bottom: 0.8rem;
}
.results-header h3 {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin: 0 0 0.7rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.results-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: #8892A8;
}
.results-meta strong { color: #E8ECF5; }

/* Result card */
.result-card {
  background: rgba(20, 25, 40, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 0;
  margin-bottom: 0.8rem;
  overflow: hidden;
}
.result-card-top {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.4rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.result-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.result-speaker-name {
  font-size: 1rem;
  font-weight: 700;
  color: #E8ECF5;
}
.result-wod-badge {
  margin-left: auto;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.result-wod-badge.used {
  background: rgba(0,212,170,0.15);
  color: #00D4AA;
}
.result-wod-badge.not-used {
  background: rgba(255,181,71,0.15);
  color: #FFB547;
}
.result-question {
  padding: 0.7rem 1.4rem;
  font-size: 0.88rem;
  color: #8892A8;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}
.result-question .q-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #00D4AA;
  flex-shrink: 0;
  margin-top: 0.4rem;
}
.result-question .q-text {
  font-style: italic;
  line-height: 1.5;
}
.result-body {
  padding: 0.8rem 1.4rem;
}
.result-body-section {
  margin-bottom: 0.6rem;
}
.result-body-section:last-child { margin-bottom: 0; }
.result-section-head {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #5A6478;
  margin-bottom: 0.3rem;
}

/* Export bar */
.results-export-marker { display: none; }
[data-testid="stVerticalBlockBorderWrapper"]:has(.results-export-marker):not(:has(.v2-nav-marker)) {
  background: rgba(20, 25, 40, 0.4) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 14px !important;
  padding: 0.8rem 1.2rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.results-export-marker):not(:has(.v2-nav-marker))
  .stDownloadButton > button {
  border-radius: 999px !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  padding: 0.4rem 1rem !important;
}

/* ---- Home hero (dark) ---- */
.v2-hero {
  text-align: center;
  padding: 3rem 2rem 2rem;
}
.v2-hero-logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.2rem;
  color: #FFFFFF;
  margin-bottom: 1.2rem;
  box-shadow: 0 8px 32px rgba(0,212,170,0.3);
}
.v2-hero h1 {
  font-size: 2.2rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.v2-hero .tagline {
  font-size: 0.95rem;
  color: #8892A8;
  margin-bottom: 2rem;
  line-height: 1.5;
}

/* CTA buttons */
.v2-cta {
  display: flex;
  gap: 0.8rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}
.v2-cta a {
  text-decoration: none !important;
  color: inherit;
  display: inline-block;
  padding: 0.7rem 2rem;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: 700;
  transition: all 0.2s ease;
}
.v2-cta .cta-primary {
  background: linear-gradient(135deg, #00D4AA, #7C5CFC);
  color: #FFFFFF !important;
  box-shadow: 0 4px 20px rgba(0,212,170,0.3);
}
.v2-cta .cta-primary:hover {
  box-shadow: 0 8px 32px rgba(0,212,170,0.5);
  transform: translateY(-2px);
}
.v2-cta .cta-secondary {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #E8ECF5 !important;
}
.v2-cta .cta-secondary:hover {
  background: rgba(255,255,255,0.08);
}

/* Feature cards */
.v2-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}
.v2-feature-card {
  background: rgba(20, 25, 40, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 1.2rem 1rem;
  text-align: center;
}
.v2-feature-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  margin-bottom: 0.7rem;
}
.v2-feature-card h4 {
  margin: 0 0 0.3rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: #E8ECF5;
}
.v2-feature-card p {
  margin: 0;
  font-size: 0.78rem;
  color: #8892A8;
  line-height: 1.45;
}

@media (max-width: 768px) {
  .v2-features { grid-template-columns: 1fr; }
  .v2-cta { flex-direction: column; align-items: center; }
}
</style>""", unsafe_allow_html=True)


def render_header(subtitle: str = ""):
    """Legacy — kept for compatibility."""
    inject_custom_css()


def render_state_pill(state: str):
    colors = {
        "idle": "#5A6478",
        "listening": "#00D4AA",
        "thinking": "#FFB547",
        "ready": "#7C5CFC",
        "speaking": "#00D4AA",
    }
    c = colors.get(state.lower(), "#5A6478")
    return (
        f'<span style="display:inline-block; padding:0.2rem 0.7rem; border-radius:999px; '
        f'font-weight:700; font-size:0.72rem; letter-spacing:0.5px; '
        f'background:rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.15); '
        f'color:{c};">{state.upper()}</span>'
    )


def render_sidebar():
    """Legacy sidebar — kept for compatibility but hidden by default in v2."""
    pass
