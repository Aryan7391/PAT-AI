import whisper
import os

# Load Whisper base model once at startup
# Loading once and reusing is faster than loading every time
print("[PAT_7] Loading Whisper base model...")
model = whisper.load_model("base")
print("[PAT_7] Whisper base ready.")


def transcribe_audio(filepath: str) -> str:
    """
    Transcribe a WAV audio file to text using Whisper base.

    Args:
        filepath: Path to the WAV audio file

    Returns:
        Transcribed text string, or empty string if file not found
        or nothing was captured.
    """
    if not os.path.exists(filepath):
        print(f"[PAT_7] Error: File not found — {filepath}")
        return ""

    print(f"[PAT_7] Transcribing {filepath}...")

    result = model.transcribe(
        filepath,
        language="en",        # English — Phase 1
        fp16=False,           # CPU mode — must be False
        verbose=False         # Clean output
    )

    text = result["text"].strip()

    if not text:
        print("[PAT_7] Transcription returned empty — audio may be silent or unclear.")
        return ""

    print(f"[PAT_7] Transcription: {text}")
    return text


if __name__ == "__main__":
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(base_dir, "test_recording.wav")

    text = transcribe_audio(test_file)
    print(f"[PAT_7] Final output: '{text}'")