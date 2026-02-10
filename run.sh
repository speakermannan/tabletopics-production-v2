#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

PY="./venv/Scripts/python.exe"

if [ ! -f "$PY" ]; then
  echo "[run.sh] venv not found. Creating venv..."
  python -m venv venv
fi

echo "[run.sh] Installing requirements..."
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r requirements.txt

echo "[run.sh] Starting Streamlit..."
"$PY" -m streamlit run app/main.py