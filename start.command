#!/bin/bash
# One-click launcher for Mac. Sets everything up on first run, then starts the app.
cd "$(dirname "$0")"

if [ ! -d venv ]; then
  echo "First run: setting things up (a few minutes)..."
  python3 -m venv venv || { echo "Python 3 is not installed. Get it from python.org"; exit 1; }
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Open the browser as soon as the server is ready
( until curl -s http://127.0.0.1:7860 >/dev/null 2>&1; do sleep 2; done; open http://127.0.0.1:7860 ) &

python app.py
