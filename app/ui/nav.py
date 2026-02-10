# app/ui/nav.py
import streamlit as st
from ui.styles import inject_global_styles
from ui.ui_shell import inject_custom_css


def render_page_shell(page_title: str = "") -> None:
    """Single entry point for the consistent page shell.

    Injects all CSS (global + custom) and renders the shared top
    navigation bar.  Call this once at the top of every page.
    """
    inject_global_styles()
    inject_custom_css()
    render_nav(page_title)


def render_footer() -> None:
    """Shared footer rendered at the bottom of every page."""
    st.markdown(
        '<div class="tt-footer">'
        '<div>&copy; AI Table Topics Co-Host</div>'
        '<div>Built for Toastmasters &bull; Local-first &bull; No data leaves your machine</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_nav(page_title: str = "") -> None:
    """Shared top navigation used on every page.

    Renders a centered page title followed by the logo badge and four
    pill-shaped nav buttons (Home / Setup / Live Session / Results).
    Styling comes from the global CSS in styles.py (tt-page-title,
    tt-topbar-logo, tt-topbar-badge, and the :has(.tt-topbar-logo)
    scoped button rules).
    """
    if page_title:
        st.markdown(
            f'<div class="tt-page-title">{page_title}</div>',
            unsafe_allow_html=True,
        )

    logo_col, b1, b2, b3, b4 = st.columns(
        [0.6, 1, 1, 1.3, 1], gap="small"
    )
    with logo_col:
        st.markdown(
            '<div class="tt-topbar-logo">'
            '<div class="tt-topbar-badge">'
            '<div class="inner"><span class="big">TT</span>TOPICS</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with b1:
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.switch_page("pages/home.py")
    with b2:
        if st.button("Setup", use_container_width=True, key="nav_setup"):
            st.switch_page("pages/setup.py")
    with b3:
        if st.button("Live Session", use_container_width=True, key="nav_live"):
            st.switch_page("pages/live.py")
    with b4:
        if st.button("Results", use_container_width=True, key="nav_results"):
            st.switch_page("pages/results.py")
