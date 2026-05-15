import re
import time

from recorder import select_device, record_push_to_talk
from transcriber import transcribe_audio
from prompt_optimizer import optimize
from prompt_builder import build_prompt
from ollama_client import query_ollama
from response_handler import parse_response
from interface import PAT7Interface

# ── Configuration ──────────────────────────────────────────────────────────
AUDIO_FILE        = "command_audio"




# ── Helpers ────────────────────────────────────────────────────────────────

def get_time_greeting() -> str:
    hour = time.localtime().tm_hour
    if 5 <= hour < 12:
        return "Good morning! PAT_7 is active."
    elif 12 <= hour < 17:
        return "Good afternoon! PAT_7 is active."
    elif 17 <= hour < 21:
        return "Good evening! PAT_7 is active."
    else:
        return "You are up late! PAT_7 is active."


def _normalize(text: str) -> list[str]:
    return re.sub(r'[^a-z0-9 ]', '', text.lower()).split()


def check_for_trigger(text: str) -> str:
    """Classify transcribed text as 'kill', 'attention', 'command', or 'unclear'.

    Whisper may transcribe 'PAT_7' as 'pat7' (one token) or 'pat 7' (two tokens).
    Both are handled by checking whether any token starts with 'pat'.
    The previous ordered_match(set(...)) approach was unreliable because sets
    have no guaranteed iteration order, causing token matching to fail silently.
    """
    tokens = _normalize(text)
    if len(tokens) < 2:
        return "unclear"

    # Covers 'pat' and 'pat7' — both Whisper transcription variants of 'PAT_7'
    has_pat = any(t == "pat" or t.startswith("pat") for t in tokens)

    if has_pat and "bye" in tokens:
        return "kill"
    if has_pat and "listen" in tokens:
        return "attention"
    return "command"


# ── Voice trigger callback ─────────────────────────────────────────────────

def on_voice_trigger(ui: PAT7Interface):
    """
    Called when user presses mic button or SPACE.
    Runs the full pipeline in a background thread.
    """

    # 1 — Record
    ui.set_listening(True)
    audio_path = record_push_to_talk(filename=AUDIO_FILE, max_duration=30)
    ui.set_listening(False)

    if not audio_path:
        ui.show_error("No audio captured. Try again.")
        ui.set_ready()
        return

    # 2 — Transcribe
    raw_text = transcribe_audio(audio_path)

    if not raw_text.strip():
        ui.show_error("Could not hear anything. Please try again.")
        ui.set_ready()
        return

    # 3 — Check trigger
    trigger = check_for_trigger(raw_text)

    if trigger == "kill":
        ui.show_error("Kill phrase detected. Shutting down.")
        ui.set_ready()
        return

    elif trigger == "attention":
        ui.show_error("Attention trigger detected. Ready for new instruction.")
        ui.set_ready()
        return

    elif trigger == "unclear":
        ui.show_error("Could not understand. Please try again.")
        ui.set_ready()
        return

    # 4 — Show user message
    ui.show_user_message(raw_text)

    # 5 — Optimize
    optimized = optimize(raw_text)
    if not optimized:
        ui.show_error("Could not optimize prompt.")
        ui.set_ready()
        return

    # 6 — Build prompt
    request_type, built_prompt = build_prompt(optimized)
    if not built_prompt:
        ui.show_error("Could not build prompt.")
        ui.set_ready()
        return

    # 7 — Query Ollama
    ui.set_thinking()
    raw_response = query_ollama(built_prompt)

    if not raw_response:
        ui.show_error("No response from Ollama. Make sure it is running: ollama serve")
        ui.set_ready()
        return

    # 8 — Parse and display
    spoken, full = parse_response(raw_response, request_type)
    ui.show_response(spoken=spoken, full=full, request_type=request_type)
    ui.set_ready()


# ── Entry point ────────────────────────────────────────────────────────────

def start():
    print("\n[PAT_7] Initializing...")
    select_device()

    PAT7Interface(on_voice_trigger=on_voice_trigger)
    print(f"\n[PAT_7] {get_time_greeting()}")
    print("[PAT_7] Interface ready. Press the mic button or SPACE to speak.\n")

    # Keep main thread alive while UI runs
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[PAT_7] Shutting down.")


if __name__ == "__main__":
    start()