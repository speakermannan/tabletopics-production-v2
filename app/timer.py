import time
import streamlit as st


def start_timer() -> None:
    st.session_state["timer_running"] = True
    st.session_state["timer_start_ts"] = time.time()


def stop_timer() -> None:
    st.session_state["timer_running"] = False
    st.session_state["timer_start_ts"] = 0.0


def elapsed_sec() -> int:
    if not st.session_state.get("timer_running") or st.session_state.get("timer_start_ts", 0) <= 0:
        return 0
    return int(time.time() - st.session_state["timer_start_ts"])


def stoplight_state(elapsed: int, target: int) -> tuple[str, str]:
    if target <= 0:
        return ("READY", "neutral")

    # Breakpoints (colors only in final stretch):
    #   60s → neutral 0-30, green 30-45, orange 45-60, red 60+
    #   90s → neutral 0-60, green 60-75, orange 75-90, red 90+
    #  120s → neutral 0-60, green 60-90, orange 90-120, red 120+
    if target <= 90:
        green_at = target - 30
        orange_at = target - 15
    else:
        green_at = target // 2
        orange_at = target * 3 // 4

    if elapsed < green_at:
        return ("", "neutral")
    if elapsed < orange_at:
        return ("GREEN", "green")
    if elapsed < target:
        return ("ORANGE", "orange")
    return ("RED", "red")


def stoplight_html(label: str, elapsed: int, target: int, running: bool) -> str:
    sub = f"{elapsed}s / {target}s" if running else "Timer paused"
    return f"""
    <div style="
        width: 100%;
        border-radius: 18px;
        padding: 18px 16px;
        border: 2px solid rgba(255,255,255,0.2);
        background: rgba(0,0,0,0.35);
        ">
      <div style="display:flex; align-items:center; gap: 14px;">
        <div style="
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: {label.lower()};
            box-shadow: 0 0 20px rgba(255,255,255,0.10);
            border: 2px solid rgba(255,255,255,0.35);
        "></div>
        <div style="flex:1;">
          <div style="font-size: 28px; font-weight: 800; letter-spacing: 0.5px;">
            {label}
          </div>
          <div style="font-size: 18px; opacity: 0.9;">
            {sub}
          </div>
        </div>
      </div>
    </div>
    """
