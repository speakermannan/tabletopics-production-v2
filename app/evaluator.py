# app/evaluator.py
import json
import re
import threading
import queue
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_eval_q: "queue.Queue[tuple[bool, dict | None, str]]" = queue.Queue()
_eval_lock = threading.Lock()
_eval_inflight = False


def _sanitize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _clip_lines(text: str, max_lines: int = 5) -> str:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return "\n".join(lines[:max_lines])


@lru_cache(maxsize=4)
def load_prompt(rel_path: str) -> str:
    base = Path(__file__).parent  # …/app
    p = base / rel_path
    return p.read_text(encoding="utf-8")


def generate_evaluation(
    *,
    question: str,
    transcript: str,
    word_of_day: str = "",
    model: str = "gpt-4o-mini",
    timeout_sec: float = 8.0,
) -> str:
    q = _sanitize(question)
    t = _sanitize(transcript)
    wod = _sanitize(word_of_day)

    if not t:
        return "No transcript available.\nStrength: —\nImprovement: —\nNo rephrase needed.\nWord of the Day usage: Not used"

    system = load_prompt("prompts/evaluator_prompt.txt")

    user = {"question": q, "transcript": t[:2000], "word_of_day": wod}

    client = OpenAI(timeout=timeout_sec)
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=240,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    )

    text = (resp.choices[0].message.content or "").strip()
    text = _clip_lines(text, max_lines=5)
    return text or "Clear response with a relatable example.\nStrength: —\nImprovement: —\nNo rephrase needed.\nWord of the Day usage: Not used"


def is_eval_inflight() -> bool:
    global _eval_inflight
    with _eval_lock:
        return _eval_inflight


def start_evaluate_async(
    *,
    question: str,
    transcript: str,
    word_of_day: str = "",
    model: str = "gpt-4o-mini",
) -> None:
    global _eval_inflight
    with _eval_lock:
        if _eval_inflight:
            return
        _eval_inflight = True

    def _worker():
        global _eval_inflight
        try:
            text = generate_evaluation(
                question=question,
                transcript=transcript,
                word_of_day=word_of_day,
                model=model,
            )
            _eval_q.put((True, {"notes": text}, ""))
        except Exception as e:
            _eval_q.put((True, None, str(e)))
        finally:
            with _eval_lock:
                _eval_inflight = False

    threading.Thread(target=_worker, daemon=True).start()


def pop_evaluate_result():
    """
    Returns (done, result_dict, error_str)
    """
    try:
        done, res, err = _eval_q.get_nowait()
        return done, res, err
    except queue.Empty:
        return False, None, ""
