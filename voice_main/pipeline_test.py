from recorder import select_device, record_push_to_talk
from transcriber import transcribe_audio
from prompt_optimizer import optimize


def run_pipeline() -> str:
    """
    Full pipeline test — push-to-talk record → transcribe → optimize.

    Returns:
        Optimized prompt string
    """
    print("\n[PAT_7] Starting pipeline test...")

    # Step 1 — Record (push-to-talk)
    filepath = record_push_to_talk(filename="pipeline_audio", max_duration=30)

    if not filepath:
        print("[PAT_7] No audio captured.")
        return ""

    # Step 2 — Transcribe
    raw_text = transcribe_audio(filepath)

    if not raw_text.strip():
        print("[PAT_7] Nothing transcribed.")
        return ""

    print(f"\n[PAT_7] Raw transcription:  '{raw_text}'")

    # Step 3 — Optimize
    optimized = optimize(raw_text)

    print(f"\n[PAT_7] Pipeline output:    '{optimized}'")
    return optimized


if __name__ == "__main__":
    select_device()
    result = run_pipeline()