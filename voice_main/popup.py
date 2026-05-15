"""Phase 2 — standalone popup window for PAT_7 full responses.

Not currently imported or used. The active output path is the integrated
chat area in interface.py (PAT7Interface.show_response).

Reserved for future use when a separate always-on-top response window
is needed independently of the main interface.
"""
import tkinter as tk
from tkinter import scrolledtext
import threading


class PopupWindow:
    """
    Non-intrusive popup window for PAT_7 full responses.
    Runs in its own thread — never blocks the voice loop.
    """

    def __init__(self):
        self._root   = None
        self._text   = None
        self._footer = None
        self._ready  = threading.Event()
        self._lock   = threading.Lock()

        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        self._ready.wait()

    def _run(self):
        self._root = tk.Tk()
        self._root.title("PAT_7")
        self._root.geometry("720x500+60+60")
        self._root.configure(bg="#1e1e1e")
        self._root.attributes("-topmost", True)
        self._root.resizable(True, True)

        # Header
        tk.Label(
            self._root, text="PAT_7",
            bg="#1e1e1e", fg="#00d4ff",
            font=("Segoe UI", 12, "bold"),
            anchor="w", padx=12, pady=8
        ).pack(fill=tk.X)

        tk.Frame(self._root, bg="#2a2a2a", height=1).pack(fill=tk.X)

        # Text area
        self._text = scrolledtext.ScrolledText(
            self._root,
            wrap=tk.WORD,
            bg="#1e1e1e", fg="#d4d4d4",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=14, pady=12,
            state=tk.DISABLED
        )
        self._text.pack(fill=tk.BOTH, expand=True)

        tk.Frame(self._root, bg="#2a2a2a", height=1).pack(fill=tk.X)

        # Footer
        self._footer = tk.Label(
            self._root, text="Waiting...",
            bg="#1e1e1e", fg="#555555",
            font=("Segoe UI", 8),
            anchor="w", padx=12, pady=4
        )
        self._footer.pack(fill=tk.X)

        self._ready.set()
        self._root.mainloop()

    def show(self, spoken: str, full: str, request_type: str = "general"):
        """Update popup with new response."""
        def _update():
            with self._lock:
                self._text.configure(state=tk.NORMAL)
                self._text.delete("1.0", tk.END)

                # Spoken summary section
                self._text.insert(tk.END, "▶  Summary\n", "summary_header")
                self._text.insert(tk.END, f"{spoken}\n\n", "summary_body")
                self._text.insert(tk.END, "─" * 55 + "\n\n", "divider")

                # Full response
                self._text.insert(tk.END, full, "full_body")

                self._text.tag_configure("summary_header", foreground="#00d4ff", font=("Segoe UI", 9, "bold"))
                self._text.tag_configure("summary_body",   foreground="#9cdcfe", font=("Segoe UI", 10))
                self._text.tag_configure("divider",        foreground="#2a2a2a")
                self._text.tag_configure("full_body",      foreground="#d4d4d4", font=("Consolas", 10))

                self._text.configure(state=tk.DISABLED)
                self._text.see("1.0")
                self._footer.configure(text=f"Request type: {request_type}  |  Response ready.")

        if self._root:
            self._root.after(0, _update)

    def clear(self):
        """Clear popup content."""
        def _clear():
            self._text.configure(state=tk.NORMAL)
            self._text.delete("1.0", tk.END)
            self._text.configure(state=tk.DISABLED)
            self._footer.configure(text="Waiting...")
        if self._root:
            self._root.after(0, _clear)