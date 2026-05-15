import tkinter as tk
from tkinter import scrolledtext
import threading


class PAT7Interface:
    """
    PAT_7 main interface.
    - Press the MIC button (or SPACE) to start/stop recording
    - Shows conversation history — user prompts and PAT_7 responses
    - Full response displayed in chat, spoken summary shown as subtitle
    """

    def __init__(self, on_voice_trigger):
        """
        Args:
            on_voice_trigger: Callback function called when user presses mic button.
                              The interface passes itself so the pipeline can call
                              set_listening(), show_user_message(), show_response()
        """
        self._on_voice_trigger = on_voice_trigger
        self._lock             = threading.Lock()
        self._ready            = threading.Event()
        self._is_listening     = False

        thread = threading.Thread(target=self._build, daemon=True)
        thread.start()
        self._ready.wait()

    # ── Build UI ───────────────────────────────────────────────────────────

    def _build(self):
        self._root = tk.Tk()
        self._root.title("PAT_7")
        self._root.geometry("780x580+80+60")
        self._root.configure(bg="#121212")
        self._root.resizable(True, True)

        self._build_header()
        self._build_chat()
        self._build_input_bar()

        # Keyboard shortcut — SPACE to trigger mic
        self._root.bind("<space>", lambda e: self._trigger_mic())

        self._ready.set()
        self._root.mainloop()

    def _build_header(self):
        header = tk.Frame(self._root, bg="#1a1a2e", height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="PAT_7",
            bg="#1a1a2e", fg="#00d4ff",
            font=("Segoe UI", 14, "bold"),
            padx=16
        ).pack(side=tk.LEFT, pady=10)

        self._status_label = tk.Label(
            header,
            text="● Ready",
            bg="#1a1a2e", fg="#4caf50",
            font=("Segoe UI", 9),
            padx=16
        )
        self._status_label.pack(side=tk.RIGHT, pady=10)

    def _build_chat(self):
        chat_frame = tk.Frame(self._root, bg="#121212")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self._chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#121212", fg="#d4d4d4",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=16, pady=12,
            state=tk.DISABLED,
            cursor="arrow"
        )
        self._chat.pack(fill=tk.BOTH, expand=True)

        # Text tags
        self._chat.tag_configure("user_name",    foreground="#00d4ff", font=("Segoe UI", 9, "bold"))
        self._chat.tag_configure("user_text",    foreground="#e0e0e0", font=("Segoe UI", 10))
        self._chat.tag_configure("pat_name",     foreground="#bb86fc", font=("Segoe UI", 9, "bold"))
        self._chat.tag_configure("pat_spoken",   foreground="#9cdcfe", font=("Segoe UI", 10, "italic"))
        self._chat.tag_configure("divider_line", foreground="#2a2a2a")
        self._chat.tag_configure("pat_full",     foreground="#d4d4d4", font=("Consolas", 10))
        self._chat.tag_configure("timestamp",    foreground="#444444", font=("Segoe UI", 8))
        self._chat.tag_configure("thinking",     foreground="#555555", font=("Segoe UI", 10, "italic"))

    def _build_input_bar(self):
        bar = tk.Frame(self._root, bg="#1e1e1e", height=64)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        tk.Frame(self._root, bg="#2a2a2a", height=1).pack(fill=tk.X, side=tk.BOTTOM)

        # Mic button
        self._mic_btn = tk.Button(
            bar,
            text="🎤  Press to Speak",
            command=self._trigger_mic,
            bg="#1f6feb", fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=24, pady=8,
            cursor="hand2",
            activebackground="#388bfd",
            activeforeground="white"
        )
        self._mic_btn.pack(side=tk.LEFT, padx=16, pady=12)

        # Hint
        tk.Label(
            bar,
            text="or press SPACE",
            bg="#1e1e1e", fg="#444444",
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)

        # Request type badge
        self._type_label = tk.Label(
            bar,
            text="",
            bg="#1e1e1e", fg="#666666",
            font=("Segoe UI", 8),
            padx=16
        )
        self._type_label.pack(side=tk.RIGHT)

    # ── Trigger ────────────────────────────────────────────────────────────

    def _trigger_mic(self):
        """Called when mic button or SPACE is pressed."""
        if not self._is_listening:
            threading.Thread(
                target=self._on_voice_trigger,
                args=(self,),
                daemon=True
            ).start()

    # ── Public API — called by the pipeline ───────────────────────────────

    def set_listening(self, listening: bool):
        """Update UI to reflect recording state."""
        def _update():
            if listening:
                self._is_listening = True
                self._mic_btn.configure(
                    text="🔴  Listening...",
                    bg="#c62828"
                )
                self._status_label.configure(text="● Listening", fg="#f44336")
            else:
                self._is_listening = False
                self._mic_btn.configure(
                    text="🎤  Press to Speak",
                    bg="#1f6feb"
                )
                self._status_label.configure(text="● Processing...", fg="#ff9800")

        if self._root:
            self._root.after(0, _update)

    def set_ready(self):
        """Reset UI to ready state."""
        def _update():
            self._is_listening = False
            self._mic_btn.configure(text="🎤  Press to Speak", bg="#1f6feb")
            self._status_label.configure(text="● Ready", fg="#4caf50")

        if self._root:
            self._root.after(0, _update)

    def set_thinking(self):
        """Show thinking state while waiting for LLM."""
        def _update():
            self._status_label.configure(text="● Thinking...", fg="#ff9800")
            self._append("PAT_7 is thinking...\n\n", "thinking")

        if self._root:
            self._root.after(0, _update)

    def show_user_message(self, text: str):
        """Add user message to chat."""
        def _update():
            self._append("You\n", "user_name")
            self._append(f"{text}\n\n", "user_text")

        if self._root:
            self._root.after(0, _update)

    def show_response(self, spoken: str, full: str, request_type: str = "general"):
        """Add PAT_7 response to chat — removes thinking indicator."""
        def _update():
            # Remove last "thinking" line if present
            content = self._chat.get("1.0", tk.END)
            if "PAT_7 is thinking..." in content:
                self._chat.configure(state=tk.NORMAL)
                start = self._chat.search("PAT_7 is thinking...", "1.0", tk.END)
                if start:
                    self._chat.delete(f"{start} linestart", f"{start} lineend +1c +1c")
                self._chat.configure(state=tk.DISABLED)

            self._append("PAT_7\n",          "pat_name")
            self._append(f"{spoken}\n\n",    "pat_spoken")
            self._append("─" * 50 + "\n",   "divider_line")
            self._append(f"{full}\n\n",      "pat_full")

            self._type_label.configure(text=f"Type: {request_type}")
            self._chat.see(tk.END)

        if self._root:
            self._root.after(0, _update)

    def show_error(self, message: str):
        """Show an error message in chat."""
        def _update():
            self._append(f"⚠  {message}\n\n", "thinking")

        if self._root:
            self._root.after(0, _update)

    # ── Internal ───────────────────────────────────────────────────────────

    def _append(self, text: str, tag: str):
        """Append text with tag to chat area."""
        self._chat.configure(state=tk.NORMAL)
        self._chat.insert(tk.END, text, tag)
        self._chat.configure(state=tk.DISABLED)
        self._chat.see(tk.END)


if __name__ == "__main__":
    # Test UI without pipeline
    def dummy_trigger(ui):
        import time
        ui.set_listening(True)
        time.sleep(2)
        ui.set_listening(False)
        ui.show_user_message("Write a Python function to read a CSV file.")
        ui.set_thinking()
        time.sleep(2)
        ui.show_response(
            spoken="Here's a Python function that reads a CSV file using the csv module.",
            full="import csv\n\ndef read_csv(filepath):\n    with open(filepath) as f:\n        return list(csv.DictReader(f))",
            request_type="coding"
        )
        ui.set_ready()

    ui = PAT7Interface(on_voice_trigger=dummy_trigger)
    import time
    time.sleep(60)