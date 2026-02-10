# bridge.py
"""
Step 9: Bridging Logic (Template-first + bounded LLM fill)

Goal:
- Keep continuity across speakers like a panel discussion
- Stay deterministic for structure
- Use LLM ONLY to generate a short "bridge phrase" (max 8 words)
- Never let the LLM write the full bridge paragraph
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# -----------------------------
# Deterministic templates
# -----------------------------
TEMPLATES = [
    "Thanks, {prev}. You highlighted {phrase}. {next}, building on that—{question_lead}",
    "Appreciate that, {prev}. You brought up {phrase}. {next}, let’s stay with that idea—{question_lead}",
    "Great point, {prev}. The key theme was {phrase}. {next}, picking up from there—{question_lead}",
]

QUESTION_LEADS = [
    "here’s your question",
    "here’s one for you",
    "your question is",
]


@dataclass
class BridgeResult:
    bridge_text: str
    bridge_phrase: str
    used_llm: bool


# -----------------------------
# LLM-bounded phrase generator
# -----------------------------
def _safe_clip(text: str, max_len: int) -> str:
    text = (text or "").strip()
    return text[:max_len].strip()


def _fallback_phrase(summary: str) -> str:
    """
    Deterministic fallback: grab a short slice of the summary.
    We keep it boring and safe.
    """
    summary = (summary or "").strip()
    if not summary:
        return "a helpful example"
    # take first sentence-ish chunk
    chunk = summary.split("\n")[0]
    chunk = chunk.split(".")[0]
    chunk = _safe_clip(chunk, 60)
    return chunk if chunk else "a helpful example"


def _choose_template(i: int) -> str:
    return TEMPLATES[i % len(TEMPLATES)]


def _choose_question_lead(i: int) -> str:
    return QUESTION_LEADS[i % len(QUESTION_LEADS)]


def _extract_phrase_from_llm_json(text: str) -> Optional[str]:
    """
    We expect a tiny JSON object like: {"phrase":"..."}
    Keep parsing simple and safe (no heavy deps).
    """
    text = (text or "").strip()
    if not text:
        return None

    # very small "parsing" to avoid external libs
    # look for "phrase":"..."
    key = '"phrase"'
    if key not in text:
        return None
    after = text.split(key, 1)[1]
    if ":" not in after:
        return None
    after = after.split(":", 1)[1].strip()

    # remove leading quotes/braces
    if after.startswith('"'):
        after = after[1:]
    # phrase ends at next quote
    if '"' in after:
        phrase = after.split('"', 1)[0]
        phrase = phrase.strip()
        return phrase or None
    return None


def generate_bridge_phrase_llm(
    client,
    model: str,
    prev_summary: str,
    theme: str,
    word_of_day: str,
) -> Optional[str]:
    """
    Uses LLM to generate ONE short phrase only.
    Hard constraints:
    - <= 8 words
    - neutral tone
    - no judgment, no advice
    - derived from summary
    Output must be JSON: {"phrase":"..."}
    """
    prev_summary = _safe_clip(prev_summary, 600)
    theme = _safe_clip(theme, 80)
    word_of_day = _safe_clip(word_of_day, 40)

    system = (
        "You generate a single neutral bridging phrase for a moderator.\n"
        "Rules:\n"
        "- Output ONLY valid JSON in this exact shape: {\"phrase\":\"...\"}\n"
        "- The phrase must be 3–8 words.\n"
        "- It must summarize the prior speaker's point neutrally.\n"
        "- No advice. No praise. No judgment. No clichés.\n"
        "- Do NOT include the next speaker's name.\n"
        "- Do NOT include quotes.\n"
    )

    user = (
        f"Theme: {theme}\n"
        f"Word of the day: {word_of_day}\n"
        f"Prior speaker summary:\n{prev_summary}\n\n"
        "Return the best bridging phrase."
    )

    try:
        # Works with the current OpenAI Python client patterns
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=40,
        )
        text = resp.choices[0].message.content
        phrase = _extract_phrase_from_llm_json(text)
        if not phrase:
            return None

        # Enforce word cap
        words = phrase.split()
        if len(words) > 8:
            phrase = " ".join(words[:8]).strip()

        # Final cleanup
        phrase = phrase.strip(" .,-—")
        return phrase or None

    except Exception:
        return None


def build_bridge(
    prev_speaker: str,
    next_speaker: str,
    prev_summary: str,
    theme: str,
    word_of_day: str,
    client=None,
    model: str = "gpt-4o-mini",
    template_index: int = 0,
    use_llm_phrase: bool = True,
) -> BridgeResult:
    """
    Returns a single bridge line that YOU can show/speak before the next question.

    Template-first:
    - Deterministic structure
    - LLM only fills a short phrase (optional)
    """
    prev_speaker = _safe_clip(prev_speaker, 40) or "Thanks"
    next_speaker = _safe_clip(next_speaker, 40) or "Next"

    used_llm = False
    phrase = None

    if use_llm_phrase and client is not None:
        phrase = generate_bridge_phrase_llm(
            client=client,
            model=model,
            prev_summary=prev_summary,
            theme=theme,
            word_of_day=word_of_day,
        )
        used_llm = phrase is not None

    if not phrase:
        phrase = _fallback_phrase(prev_summary)

    tpl = _choose_template(template_index)
    lead = _choose_question_lead(template_index)

    bridge_text = tpl.format(
        prev=prev_speaker,
        next=next_speaker,
        phrase=phrase,
        question_lead=lead,
    )

    return BridgeResult(bridge_text=bridge_text, bridge_phrase=phrase, used_llm=used_llm)
