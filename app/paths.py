import os

APP_DIR = os.path.dirname(__file__)

AUDIO_DIR = os.path.join(APP_DIR, "audio")
LATEST_WAV = os.path.join(AUDIO_DIR, "latest.wav")

TRANSCRIPTS_DIR = os.path.join(APP_DIR, "transcripts")


def ensure_dirs() -> None:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
