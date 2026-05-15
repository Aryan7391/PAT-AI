import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

print("[PAT_7] Root:", ROOT_DIR)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from session_manager import SessionManager

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "web", "templates"),
    static_folder=os.path.join(BASE_DIR, "web", "static")
)
CORS(app)

sm = SessionManager()


# ─────────────────────────────────────
# Chats
# ─────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chats", methods=["GET"])
def get_chats():
    return jsonify(sm.list_chats())


@app.route("/api/chats", methods=["POST"])
def create_chat():
    data = request.json

    name = data.get("name", "New Chat")

    result = sm.create_chat(name)
    return jsonify(result)


@app.route("/api/load_chat", methods=["POST"])
def load_chat():
    data = request.json

    chat_id = data.get("chat_id")

    result = sm.load_chat(chat_id)
    return jsonify(result)


# ─────────────────────────────────────
# Messages
# ─────────────────────────────────────

@app.route("/api/messages", methods=["GET"])
def get_messages():
    return jsonify(sm.get_messages())


@app.route("/api/message", methods=["POST"])
def send_message():
    data = request.json

    user_text = data.get("message", "")

    if not user_text.strip():
        return jsonify({"error": "Empty message"}), 400

    result = sm.send_message(user_text)
    return jsonify(result)


# ─────────────────────────────────────
# Run
# ─────────────────────────────────────


import os as _os
_UPLOAD_DIR = _os.path.join(_os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..")), "uploads")
_os.makedirs(_UPLOAD_DIR, exist_ok=True)

@app.route("/api/voice", methods=["POST"])
def send_voice():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file."}), 400

    audio_file = request.files["audio"]
    raw_path = _os.path.join(_UPLOAD_DIR, "voice_input.webm")
    wav_path = _os.path.join(_UPLOAD_DIR, "voice_input.wav")
    audio_file.save(raw_path)

    ret = _os.system(f'ffmpeg -y -i "{raw_path}" -ar 16000 -ac 1 -f wav "{wav_path}" -loglevel error')
    if ret != 0:
        import shutil
        shutil.copy(raw_path, wav_path)

    try:
        result = sm.send_voice(wav_path)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)