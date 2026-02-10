# app/question_gen.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import json
import re

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path


load_dotenv()


@dataclass(frozen=True)
class QuestionConstraints:
    creativity: int = 70
    max_seconds: int = 75
    style: str = "toastmasters"
    avoid_topics: Optional[List[str]] = None
    require_word: Optional[str] = None
    theme: Optional[str] = None

def load_prompt(path: str) -> str:
    base = Path(__file__).parent  # points to /app
    return (base / path).read_text(encoding="utf-8")

# -----------------------------
# Utils
# -----------------------------
def _sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _safe_list(xs: Optional[List[str]]) -> List[str]:
    return [x.strip() for x in (xs or []) if x and x.strip()]


def _creativity_to_temperature(creativity: int) -> float:
    c = max(0, min(100, int(creativity)))
    return 0.2 + (c / 100) * 0.8


def _client() -> OpenAI:
    return OpenAI()


def _cap_words(text: str, n: int) -> str:
    w = _sanitize(text).split()
    if len(w) <= n:
        return " ".join(w)
    return " ".join(w[:n]).strip()


def _cap_to_one_question(text: str) -> str:
    """
    1–2 sentences max, only one '?'.
    """
    t = _sanitize(text)
    if not t:
        return ""

    parts = re.split(r"(?<=[.!?])\s+", t)
    parts = [p.strip() for p in parts if p.strip()]
    t = " ".join(parts[:2]).strip() if parts else t

    if t.count("?") > 1:
        t = t.split("?", 1)[0].strip() + "?"
    if "?" not in t:
        t = t.rstrip(".") + "?"
    return t


def _strip_ai_narration(text: str) -> str:
    """
    Remove narrator patterns.
    """
    t = _sanitize(text)
    kill_prefixes = [
        r"^thanks[, ]+.*?\.\s*",
        r"^thank you[, ]+.*?\.\s*",
        r"^you highlighted\s+",
        r"^you mentioned\s+",
        r"^based on\s+",
        r"^considering\s+",
    ]
    for pat in kill_prefixes:
        t = re.sub(pat, "", t, flags=re.I)
    t = re.sub(r"\s+,", ",", t)
    return _sanitize(t)


# -----------------------------
# Anchor extraction + paraphrase (NEUTRAL)
# -----------------------------
def _extract_anchor(prev_summary: str) -> str:
    """
    Pull a short anchor from first bullet/line.
    """
    s = (prev_summary or "").strip()
    if not s:
        return ""

    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    bullet = ""
    for ln in lines:
        if ln.startswith(("-", "•", "*")):
            bullet = ln.lstrip("-•*").strip()
            break

    base = bullet or lines[0]
    base = base.split(".")[0].strip()
    base = base.split(";")[0].strip()
    base = base.split("—")[0].strip()
    base = _sanitize(base)
    return _cap_words(base, 10).strip(" .,:;—-")


def _paraphrase_anchor_neutral(anchor: str, theme: str, word_of_day: str, model: str) -> str:
    """
    Paraphrase anchor into a neutral phrase that DOES NOT assign ownership.
    """
    anchor = _sanitize(anchor)
    if not anchor:
        return ""

    system = load_prompt("prompts/paraphrase_anchor_system.txt")

    user = {
        "theme": _sanitize(theme) or None,
        "word_of_day": _sanitize(word_of_day) or None,
        "anchor_phrase": anchor,
        "examples": [
            {"in": "Team members decide which approach to pursue", "out": "letting the team choose the approach"},
            {"in": "set low expectations to avoid embarrassment", "out": "starting with low expectations to stay comfortable"},
        ],
    }

    try:
        resp = _client().chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=70,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
        )
        text = resp.choices[0].message.content or ""
        data = json.loads(text)
        phrase = _sanitize(data.get("phrase", ""))
        phrase = phrase.strip(' "“”')
        phrase = _cap_words(phrase, 12)
        phrase = re.sub(r"\b(based on|considering|highlighted)\b", "", phrase, flags=re.I)
        return _sanitize(phrase)
    except Exception:
        a = re.sub(r"^(proposes|suggests|focuses on|discusses|consider)\s+", "", anchor, flags=re.I).strip()
        a = a or anchor
        return _cap_words(a, 12)


# -----------------------------
# Facilitation scaffolding (keep light + not repetitive)
# -----------------------------
_BRIDGE_TEMPLATES = [
    "{next}, quick follow-up to {prev}'s point on {anchor}:",
    "{next}, building on {prev}'s idea about {anchor}:",
    "{next}, take {prev}'s {anchor} and push it one step further:",
]


def _bridge(next_speaker: str, prev_speaker: str, anchor_phrase: str, template_index: int) -> str:
    t = _BRIDGE_TEMPLATES[template_index % len(_BRIDGE_TEMPLATES)]
    return t.format(next=next_speaker, prev=prev_speaker, anchor=anchor_phrase or "that").strip()


# -----------------------------
# Quality gate: detect dull followups
# -----------------------------
_DULL_PATTERNS = [
    r"\bwhat do you do first\b",
    r"\bwhat would you do first\b",
    r"\bhow would you do it\b",
    r"\bwhat steps would you take\b",
    r"\bhow would you handle\b",
    r"\bwalk me through\b",
    r"\bfirst step\b",
]


def _is_dull(q: str) -> bool:
    t = _sanitize(q).lower()
    return any(re.search(pat, t, flags=re.I) for pat in _DULL_PATTERNS)


# -----------------------------
# Initial question (unchanged behavior)
# -----------------------------
def generate_initial_question(
    speaker: str,
    context: str,
    constraints: QuestionConstraints,
    model: str = "gpt-4o-mini",
) -> str:
    speaker = _sanitize(speaker) or "Speaker"
    context = _sanitize(context)
    avoid = _safe_list(constraints.avoid_topics)
    require_word = _sanitize(constraints.require_word) or ""
    theme = _sanitize(constraints.theme) or ""

    temperature = _creativity_to_temperature(constraints.creativity)

    sys = load_prompt("prompts/question_initial_system.txt")

    user = {
        "speaker": speaker,
        "theme": theme or None,
        "meeting_context": context,
        "target_seconds": constraints.max_seconds,
        "require_word": require_word or None,
        "avoid_topics": avoid or None,
    }

    try:
        resp = _client().chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=150,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
            ],
        )
        text = resp.choices[0].message.content or ""
        data = json.loads(text)
        q = _cap_to_one_question(data.get("question", ""))
        q = _strip_ai_narration(q)

        if not q:
            q = f"{speaker}, imagine a real situation tied to {context}. What do you do—and why?"
            q = _cap_to_one_question(q)

        if require_word and require_word.lower() not in q.lower():
            q += f' Try to naturally use the word: "{require_word}".'

        return q

    except Exception:
        q = f"{speaker}, imagine a real situation tied to {context}. What do you do—and why?"
        q = _cap_to_one_question(q)
        if require_word:
            q += f' Try to naturally use the word: "{require_word}".'
        return q


# -----------------------------
# Follow-up question (CREATIVE, LLM-led, minimal deterministic guardrails)
# -----------------------------
def generate_followup_question(
    next_speaker: str,
    context: str,
    prev_speaker: str,
    prev_transcript: str,
    constraints: QuestionConstraints,
    model: str = "gpt-4o-mini",
    *,
    prev_summary: Optional[str] = None,
    prev_question: Optional[str] = None,
    asked_questions: Optional[List[str]] = None,
    template_index: int = 0,
) -> str:
    """
    Follow-up belongs to prev_speaker's content, asked to next_speaker.
    We keep deterministic logic ONLY for:
    - safety + formatting
    - a quality gate (1 retry) to avoid dull procedural questions
    """
    next_speaker = _sanitize(next_speaker) or "Speaker"
    prev_speaker = _sanitize(prev_speaker) or "the previous speaker"
    context = _sanitize(context)
    avoid = _safe_list(constraints.avoid_topics)
    require_word = _sanitize(constraints.require_word) or ""
    theme = _sanitize(constraints.theme) or ""

    temperature = _creativity_to_temperature(constraints.creativity)

    source = _sanitize(prev_summary) if prev_summary else _sanitize(prev_transcript)
    raw_anchor = _extract_anchor(source)
    anchor_phrase = _paraphrase_anchor_neutral(raw_anchor, theme or context, require_word, model)

    bridge = _bridge(next_speaker, prev_speaker, anchor_phrase, template_index)

    sys = load_prompt("prompts/question_followup_system.txt")

    clean_asked = [_sanitize(q) for q in (asked_questions or []) if q and q.strip()]

    user = {
        "next_speaker": next_speaker,
        "meeting_theme": theme or None,
        "meeting_context": context,
        "previous_speaker": prev_speaker,
        "previous_summary": source or None,
        "previous_question": _sanitize(prev_question) or None,
        "anchor_phrase": anchor_phrase or None,
        "already_asked_questions": clean_asked or None,
        "avoid_topics": avoid or None,
        "target_seconds": constraints.max_seconds,
        "style": "Toastmasters Table Topics",
        "twist_menu": [
            "time pressure (30 seconds to decide)",
            "role shift (you're the leader / the outsider / the person affected)",
            "trade-off (fairness vs speed, honesty vs harmony, risk vs opportunity)",
            "new constraint (budget cut, one rule change, unexpected audience)",
            "reverse it (argue the opposite choice convincingly)",
        ],
    }

    def _llm_followup(extra_instruction: str = "") -> str:
        payload = dict(user)
        if extra_instruction:
            payload["extra_instruction"] = extra_instruction

        resp = _client().chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=170,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        )
        text = resp.choices[0].message.content or ""
        data = json.loads(text)
        q = _sanitize(data.get("question", ""))
        q = _strip_ai_narration(_cap_to_one_question(q))
        return q

    try:
        q = _llm_followup()

        # ✅ Quality gate: if dull, regenerate once with explicit creativity push
        if _is_dull(q):
            q = _llm_followup(
                "Make it more imaginative and specific. Add a twist. Avoid any 'first/steps/how would you do it' phrasing."
            )

        # Word of the Day enforcement
        if require_word and require_word.lower() not in q.lower():
            q += f' Try to naturally use the word: "{require_word}".'

        return f"{bridge} {q}".strip()

    except Exception:
        # Safe fallback (still less procedural)
        q = f"Imagine {anchor_phrase or 'that idea'} suddenly backfires—what’s the trade-off you accept?"
        q = _strip_ai_narration(_cap_to_one_question(q))
        if require_word and require_word.lower() not in q.lower():
            q += f' Try to naturally use the word: "{require_word}".'
        return f"{bridge} {q}".strip()


def simplify_question(question: str) -> str:
    q = _sanitize(question)
    q = _strip_ai_narration(q)
    return _cap_to_one_question(q)


def approve_question(proposed: str) -> str:
    return _sanitize(proposed)

