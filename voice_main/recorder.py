import sounddevice as sd
import numpy as np
import wave
import os

# Audio configuration
SAMPLE_RATE = 16000      # Whisper works best at 16kHz
CHANNELS    = 1          # Mono audio
DTYPE       = np.int16   # Standard audio format

# Device index — set once at startup via select_device()
_selected_device = None


def list_devices() -> list[tuple[int, str]]:
    """Return a list of (device_id, name) tuples for all available input devices."""
    devices = sd.query_devices()
    input_devices = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append((i, dev['name']))
    return input_devices


def select_device() -> int | None:
    """List available input devices and prompt user to pick one.

    Selection is stored globally — called once at startup.

    Returns:
        Selected device index, or None if no input devices are found.
    """
    global _selected_device

    print("\n[PAT_7] Available microphone devices:")
    print("-" * 45)

    input_devices = list_devices()

    if not input_devices:
        print("[PAT_7] No input devices found. Using system default.")
        _selected_device = None
        return None

    for idx, (dev_id, name) in enumerate(input_devices):
        print(f"  [{idx}] {name}  (device id: {dev_id})")

    print("-" * 45)

    while True:
        try:
            choice = input("[PAT_7] Select microphone number: ").strip()
            choice_idx = int(choice)
            if 0 <= choice_idx < len(input_devices):
                _selected_device = input_devices[choice_idx][0]
                print(f"[PAT_7] Microphone set: {input_devices[choice_idx][1]}\n")
                return _selected_device
            else:
                print(f"[PAT_7] Enter a number between 0 and {len(input_devices) - 1}.")
        except ValueError:
            print("[PAT_7] Invalid input. Enter a number.")


def record_audio(duration: int, filename: str) -> str:
    # Phase 2 — fixed-duration recording, not yet used.
    # Active recording path is record_push_to_talk().
    # Reserved for future timed-capture mode (e.g. IoT or scheduled tasks).
    if _selected_device is None:
        print("[PAT_7] Warning: No device selected. Using system default.")

    print(f"[PAT_7] Recording for {duration} seconds...")

    audio_data = sd.rec(
        frames=int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        device=_selected_device
    )

    sd.wait()
    print("[PAT_7] Recording complete.")

    # Build safe output path — always write to same dir as this file
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    safe_name = os.path.basename(filename)           # strip any dir component
    filepath  = os.path.join(base_dir, f"{safe_name}.wav")

    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)                     # 16-bit = 2 bytes
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data.tobytes())

    print(f"[PAT_7] Audio saved → {filepath}")
    return filepath


def record_push_to_talk(filename: str, max_duration: int = 30) -> str:
    """
    Push-to-talk recording — records while user holds ENTER,
    stops on release (or after max_duration seconds).

    Args:
        filename:     Output filename (without extension)
        max_duration: Safety cap in seconds (default 30)

    Returns:
        Path to saved WAV file
    """
    import threading

    print("[PAT_7] Hold ENTER to speak. Release to process.")
    input()                                          # wait for key press

    frames     = []
    stop_event = threading.Event()

    def callback(indata, frame_count, time_info, status):
        if stop_event.is_set():
            raise sd.CallbackStop()
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        device=_selected_device,
        callback=callback
    )

    print("[PAT_7] Recording... (release ENTER to stop)")

    with stream:
        # Wait for ENTER release in a background thread
        def wait_for_release():
            input()
            stop_event.set()

        release_thread = threading.Thread(target=wait_for_release, daemon=True)
        release_thread.start()

        # Also enforce max duration
        release_thread.join(timeout=max_duration)
        stop_event.set()

    print("[PAT_7] Recording complete.")

    if not frames:
        print("[PAT_7] No audio captured.")
        return ""

    audio_data = np.concatenate(frames, axis=0)

    # Build safe output path
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    safe_name = os.path.basename(filename)
    filepath  = os.path.join(base_dir, f"{safe_name}.wav")

    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data.tobytes())

    print(f"[PAT_7] Audio saved → {filepath}")
    return filepath


if __name__ == "__main__":
    select_device()
    path = record_push_to_talk(filename="test_recording")
    print(f"[PAT_7] Test complete. File at: {path}")