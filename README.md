# Hindi + English Transcribe

Upload an audio file and get a transcript in Hindi and English, mixed the way it was spoken.
Runs fully on your own computer. No API key, no cost, audio never leaves your machine.

## Use it (Mac)

1. Install Python 3.9+ from https://www.python.org if you don't have it.
2. Download this project (green **Code** button > **Download ZIP**) and unzip it.
3. Open Terminal in the folder and run:

   ```
   bash start.command
   ```

   The first run installs everything and downloads the speech model (a few minutes).
   Your browser opens automatically at http://127.0.0.1:7860

4. Choose an audio file, pick **Hindi + English mixed**, click **Transcribe**.

Next time, just run `bash start.command` again. Press `Ctrl + C` in Terminal to stop.

## Manual setup (any system)

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:7860

## Options

| What | How |
|---|---|
| Faster, less accurate | `WHISPER_MODEL=small bash start.command` |
| More accurate, slower | `WHISPER_MODEL=large-v3 bash start.command` |
| Hindi in Roman letters | Choose "Roman letters" in the page |

Mixed-language output is best-effort. Clear audio gives the best result.
