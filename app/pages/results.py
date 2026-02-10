# app/pages/results.py — V2 Dark Results Page
import re
import html as html_mod
import streamlit as st
from datetime import datetime
from ui.shell import render_shell_start, render_shell_end
from ui.ui_controls import _format_summary, _format_evaluator

render_shell_start(active="results")

results = st.session_state.get("speaker_results", [])
theme = (st.session_state.get("theme") or "").strip()
wod = (st.session_state.get("word_of_day") or "").strip()

if not results:
    st.markdown(
        '<div style="text-align:center; padding:3rem 1rem;">'
        '<div style="font-size:1.3rem; font-weight:700; color:#8892A8; margin-bottom:0.5rem;">'
        'No Results Yet</div>'
        '<div style="font-size:0.9rem; color:#5A6478;">Complete a live session to see results here.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Go to Setup", key="results_go_setup", type="primary"):
            st.switch_page("pages/setup.py")
    with c2:
        if st.button("Go Home", key="results_go_home"):
            st.switch_page("pages/home.py")
    st.stop()

# Session summary header
summary_html = (
    '<div class="results-header">'
    '<h3>Session Summary</h3>'
    '<div class="results-meta">'
    f'<span><strong>Theme:</strong> {html_mod.escape(theme) or "N/A"}</span>'
    f'<span><strong>Word of the Day:</strong> {html_mod.escape(wod) or "N/A"}</span>'
    f'<span><strong>Speakers:</strong> {len(results)}</span>'
    f'<span><strong>Date:</strong> {datetime.now().strftime("%b %d, %Y")}</span>'
    '</div>'
    '</div>'
)
st.markdown(summary_html, unsafe_allow_html=True)

# Speaker cards
for i, result in enumerate(results):
    name = result.get("name", f"Speaker {i+1}")
    question = result.get("question", "")
    summary = result.get("summary", "")
    evaluator_notes = result.get("evaluator_notes", "")
    coach_hint = result.get("coach_hint", "")
    transcript = result.get("transcript", "")

    # WoD badge
    wod_badge = ""
    if wod and transcript:
        if re.search(rf"\b{re.escape(wod)}\b", transcript, flags=re.IGNORECASE):
            wod_badge = '<span class="result-wod-badge used">WoD Used</span>'
        else:
            wod_badge = '<span class="result-wod-badge not-used">WoD Missed</span>'

    # Question row
    q_html = ""
    if question:
        q_html = (
            '<div class="result-question">'
            '<span class="q-dot"></span>'
            f'<span class="q-text">{html_mod.escape(question)}</span>'
            '</div>'
        )

    # Card top
    card_top = (
        '<div class="result-card">'
        '<div class="result-card-top">'
        f'<div class="result-avatar">{i+1}</div>'
        f'<div class="result-speaker-name">{html_mod.escape(name)}</div>'
        f'{wod_badge}'
        '</div>'
        f'{q_html}'
    )
    st.markdown(card_top, unsafe_allow_html=True)

    # Card body
    body_parts = []
    if summary:
        formatted_summary = _format_summary(summary)
        body_parts.append(
            '<div class="result-body-section">'
            '<div class="result-section-head">Summary</div>'
            f'{formatted_summary}'
            '</div>'
        )
    if evaluator_notes:
        formatted_eval = _format_evaluator(evaluator_notes, coach_hint)
        body_parts.append(
            '<div class="result-body-section">'
            '<div class="result-section-head">Evaluation</div>'
            f'{formatted_eval}'
            '</div>'
        )

    if body_parts:
        body_html = '<div class="result-body">' + "".join(body_parts) + '</div>'
    else:
        body_html = '<div class="result-body"><span class="empty">No details recorded</span></div>'

    st.markdown(body_html + '</div>', unsafe_allow_html=True)

# Speak Summary
def _build_spoken_summary(results_list, theme_text, wod_text):
    """Build a concise spoken recap: 1-2 bullet points per speaker."""
    lines = []
    if theme_text:
        lines.append(f"Here's a quick recap of today's Table Topics on {theme_text}.")
    else:
        lines.append("Here's a quick recap of today's Table Topics.")
    for i, r in enumerate(results_list):
        name = r.get("name", f"Speaker {i+1}")
        summary = (r.get("summary") or "").strip()
        if not summary:
            lines.append(f"{name} spoke but no summary was recorded.")
            continue
        bullets = [b.strip(" -•*\t") for b in re.split(r"[\n•\-\*]+", summary) if b.strip(" -•*\t")]
        kept = bullets[:2]
        lines.append(f"{name}: {'. '.join(kept)}.")
    lines.append("Great session everyone!")
    return " ".join(lines)

if not st.session_state.get("results_spoken_audio"):
    spoken_text = _build_spoken_summary(results, theme, wod)
    voice = st.session_state.get("tts_voice", "alloy")
    model = st.session_state.get("tts_model", "tts-1")
    try:
        from tts import generate_tts_mp3
        st.session_state["results_spoken_audio"] = generate_tts_mp3(
            spoken_text, model=model, voice=voice,
        )
    except Exception as exc:
        st.error(f"TTS failed: {exc}")

if st.session_state.get("results_spoken_audio"):
    st.markdown(
        '<div class="results-section-head" style="margin-top:0.8rem;">Session Recap</div>',
        unsafe_allow_html=True,
    )
    st.audio(st.session_state["results_spoken_audio"], format="audio/mp3")

# Export
st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

export_lines = [
    "Table Topics Session Results",
    "=" * 40,
    f"Theme: {theme or 'N/A'}",
    f"Word of the Day: {wod or 'N/A'}",
    f"Speakers: {len(results)}",
    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "",
]
for i, result in enumerate(results):
    export_lines.append(f"--- Speaker {i+1}: {result.get('name', 'Unknown')} ---")
    export_lines.append(f"Question: {result.get('question', 'N/A')}")
    export_lines.append(f"Summary: {result.get('summary', 'N/A')}")
    if result.get("evaluator_notes"):
        export_lines.append(f"Evaluator: {result['evaluator_notes']}")
    export_lines.append("")
export_text = "\n".join(export_lines)

md_lines = [
    "# Table Topics Session Results\n",
    f"**Theme:** {theme or 'N/A'}  ",
    f"**Word of the Day:** {wod or 'N/A'}  ",
    f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
]
for i, result in enumerate(results):
    md_lines.append(f"## {result.get('name', f'Speaker {i+1}')}\n")
    md_lines.append(f"**Question:** {result.get('question', 'N/A')}\n")
    if result.get("summary"):
        md_lines.append(f"**Summary:**\n{result['summary']}\n")
    if result.get("evaluator_notes"):
        md_lines.append(f"**Evaluator Notes:**\n{result['evaluator_notes']}\n")
md_text = "\n".join(md_lines)

csv_lines = ["Speaker,Question,Summary,Evaluator Notes"]
for result in results:
    n = result.get("name", "").replace('"', "'")
    q = result.get("question", "").replace('"', "'").replace("\n", " ")
    s = result.get("summary", "").replace('"', "'").replace("\n", " ")
    e = result.get("evaluator_notes", "").replace('"', "'").replace("\n", " ")
    csv_lines.append(f'"{n}","{q}","{s}","{e}"')
csv_text = "\n".join(csv_lines)

with st.container():
    st.markdown('<span class="results-export-marker"></span>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button(
            "Download .txt", data=export_text,
            file_name=f"table_topics_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True, key="btn_download_txt",
        )
    with e2:
        st.download_button(
            "Download .md", data=md_text,
            file_name=f"table_topics_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown", use_container_width=True, key="btn_download_md",
        )
    with e3:
        st.download_button(
            "Export CSV", data=csv_text,
            file_name=f"table_topics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True, key="btn_download_csv",
        )

# Navigation
st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
nc1, nc2 = st.columns(2)
with nc1:
    if st.button("New Session", use_container_width=True, type="primary", key="results_new_session"):
        from state import reset_session
        reset_session()
        st.switch_page("pages/home.py")
with nc2:
    if st.button("Back to Live", use_container_width=True, key="results_back_live"):
        st.switch_page("pages/live.py")

render_shell_end()
