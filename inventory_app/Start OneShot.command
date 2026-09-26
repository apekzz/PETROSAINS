#!/bin/bash
# Double-click in Finder. Terminal stays open while the server runs.
# Ctrl-C or closing this window stops OneShot.
cd "$(dirname "$0")" || exit 1

PY="/opt/miniconda3/bin/python"
URL="http://127.0.0.1:8000"

if [[ ! -x "$PY" ]]; then
  echo "Need $PY (conda base with YOLO)."
  echo "This launcher does not use /usr/local/bin/python3."
  exit 1
fi

if nc -z 127.0.0.1 8000 >/dev/null 2>&1; then
  open "$URL"
  echo "OneShot already running. Opened $URL"
  exit 0
fi

exec "$PY" main.py
