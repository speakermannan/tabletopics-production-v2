# app/ui/shell.py — V2 Dark Shell (nav + footer)
from __future__ import annotations
import streamlit as st
from ui.styles import inject_global_styles
from ui.ui_shell import inject_custom_css


def render_shell_start(active: str, title: str | None = None) -> None:
    """Render v2 dark shell: CSS injection + minimal nav bar."""
    inject_global_styles()
    inject_custom_css()

    # Nav bar with logo + buttons
    st.markdown('<span class="v2-nav-marker"></span>', unsafe_allow_html=True)
    logo_col, b1, b2, b3, b4 = st.columns([0.5, 1, 1, 1.3, 1], gap="small")

    with logo_col:
        st.markdown(
            '<div style="display:flex; align-items:center; justify-content:center; padding-top:0.2rem;">'
            '<div class="v2-nav-logo">TT</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with b1:
        if st.button("Home", use_container_width=True, key="nav_home",
                      type="primary" if active == "home" else "secondary"):
            st.switch_page("pages/home.py")
    with b2:
        if st.button("Setup", use_container_width=True, key="nav_setup",
                      type="primary" if active == "setup" else "secondary"):
            st.switch_page("pages/setup.py")
    with b3:
        if st.button("Live Session", use_container_width=True, key="nav_live",
                      type="primary" if active == "live" else "secondary"):
            st.switch_page("pages/live.py")
    with b4:
        if st.button("Results", use_container_width=True, key="nav_results",
                      type="primary" if active == "results" else "secondary"):
            st.switch_page("pages/results.py")


def render_shell_end() -> None:
    """Render the v2 footer."""
    st.markdown(
        '<div class="v2-footer">'
        '<div><span class="accent">AI Table Topics</span> Co-Host</div>'
        '<div>Built for Toastmasters &bull; Local-first &bull; '
        'No data leaves your machine</div>'
        '</div>',
        unsafe_allow_html=True,
    )
