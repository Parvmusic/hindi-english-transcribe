"""
Personal transcription app: upload audio -> mixed Hindi + English text.
Runs fully on your own computer (no API key, audio never leaves your machine).

Run:   python app.py
Open:  http://127.0.0.1:7860
"""
import json
import os
import tempfile

from flask import Flask, Response, request, send_from_directory
from faster_whisper import WhisperModel

# --- settings (change with environment variables) --------------------------
# Better accuracy for Hindi: large-v3 (needs more RAM / a GPU to be fast)
# Faster on a normal laptop: small  or  medium
MODEL_NAME = os.environ.get("WHISPER_MODEL", "medium")
DEVICE = os.environ.get("WHISPER_DEVICE", "auto")      # auto | cpu | cuda
COMPUTE = os.environ.get("WHISPER_COMPUTE", "auto")    # auto | int8 | float16
PORT = int(os.environ.get("PORT", "7860"))

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

print(f"Loading model '{MODEL_NAME}' (first run downloads it, please wait)...")
model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE)
print("Model ready.")

# A short mixed-language prompt nudges Whisper to keep English words in English
# and Hindi words in the chosen script, instead of forcing everything into one.
PROMPT_DEVANAGARI = (
    "आज हम project के बारे में बात करेंगे, and then next steps decide करेंगे. "
    "Okay, let's start the meeting."
)
PROMPT_ROMAN = (
    "Aaj hum project ke baare mein baat karenge, and then next steps decide karenge. "
    "Okay, let's start the meeting."
)


def settings_for(mode: str, script: str):
    """Return (language, initial_prompt) for the chosen options."""
    if mode == "english":
        return "en", None
    if mode == "hindi":
        return "hi", None
    if mode == "auto":
        return None, None
    # default: mixed Hindi + English
    return "hi", (PROMPT_ROMAN if script == "roman" else PROMPT_DEVANAGARI)


@app.get("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.post("/transcribe")
def transcribe():
    upload = request.files.get("audio")
    if not upload:
        return Response("No audio file received.", status=400)

    mode = request.form.get("mode", "mixed")
    script = request.form.get("script", "devanagari")
    language, prompt = settings_for(mode, script)

    suffix = os.path.splitext(upload.filename or "")[1] or ".audio"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    upload.save(tmp)
    tmp.close()

    def stream():
        try:
            segments, info = model.transcribe(
                tmp.name,
                language=language,
                initial_prompt=prompt,
                beam_size=5,
                vad_filter=True,                  # skip silence
                condition_on_previous_text=False,  # avoids repeated-text loops
            )
            yield json.dumps({
                "type": "info",
                "duration": info.duration,
                "language": info.language,
            }) + "\n"
            for seg in segments:
                yield json.dumps({
                    "type": "seg",
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                }, ensure_ascii=False) + "\n"
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as exc:  # show the problem in the page
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    return Response(stream(), mimetype="application/x-ndjson")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, threaded=True)
