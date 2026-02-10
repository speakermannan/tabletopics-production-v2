# app/pages/live.py — V2 Cinematic Autopilot Live Page
import streamlit as st
from ui.shell import render_shell_start, render_shell_end
from ui.ui_presenter import render_presenter_view
from ui.ui_controls import render_operator_controls, render_live_info_boxes, render_autopilot_bar
from pipeline import run_pipeline

render_shell_start(active="live")

# Check session
if not st.session_state.get("session_started"):
    st.markdown(
        '<div style="text-align:center; padding:3rem 1rem;">'
        '<div style="font-size:1.3rem; font-weight:700; color:#8892A8; margin-bottom:0.5rem;">'
        'No Active Session</div>'
        '<div style="font-size:0.9rem; color:#5A6478;">Start a session from Setup first.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.button("Go to Setup", key="live_go_setup", type="primary"):
        st.switch_page("pages/setup.py")
    st.stop()

# Autopilot pipeline
run_pipeline()

# Autopilot status bar
render_autopilot_bar()

# Two-column: Presenter (left) | Controls (right)
left, right = st.columns([3, 2])

with left:
    render_presenter_view()

with right:
    render_operator_controls()

# Spacer
st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

# Info boxes
render_live_info_boxes()

render_shell_end()
