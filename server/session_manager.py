from memory.manager import MemoryManager
from memory.context import build_full_prompt

from voice_main.prompt_optimizer import optimize
from voice_main.prompt_builder import build_prompt
from voice_main.ollama_client import query_ollama
from voice_main.response_handler import parse_response


class SessionManager:

    def __init__(self):
        self.mm = MemoryManager()

    # ─────────────────────────────────────
    # Chats
    # ─────────────────────────────────────

    def list_chats(self):
        return self.mm.list_chats()

    def create_chat(self, name: str):
        chat_id = self.mm.create_chat(name)
        return {
            "chat_id": chat_id,
            "name": name
        }

    def load_chat(self, chat_id: int):
        self.mm.load_chat(chat_id)
        return {
            "status": "ok",
            "chat_id": chat_id
        }

    def delete_chat(self, chat_id: int):
        self.mm.delete_chat(chat_id)
        return {
            "status": "deleted"
        }

    # ─────────────────────────────────────
    # Messages
    # ─────────────────────────────────────

    def get_messages(self, limit: int = 50):
        return self.mm.get_recent(limit)

    # ─────────────────────────────────────
    # Main cognition loop
    # ─────────────────────────────────────

    def send_message(self, user_text: str):
        """
        Main PAT_7 reasoning cycle.
        """

        if not self.mm.active_chat_id:
            raise RuntimeError("No active chat loaded.")

        # Save raw user message
        self.mm.save_message("user", user_text)

        # Optimize
        optimized = optimize(user_text)

        # Build structured prompt
        request_type, structured_prompt = build_prompt(optimized)

# Build memory payload
        payload = build_full_prompt(self.mm)

# Add structured user request
        payload["messages"].append({
        "role": "user",
        "content": structured_prompt
        })

        # Query Ollama
        raw_response = query_ollama(payload)

        # Parse response
        spoken, full = parse_response(raw_response, request_type)

        # Save assistant response
        self.mm.save_message("assistant", full)

        return {
            "spoken": spoken,
            "full": full,
            "request_type": request_type
        }

    def close(self):
        self.mm.close()
    def send_voice(self, audio_path: str):
        """Transcribe audio file then run through the same pipeline as send_message."""
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from voice_main.transcriber import transcribe_audio

        user_text = transcribe_audio(audio_path)
        if not user_text.strip():
            raise ValueError("Could not transcribe audio.")
        return self.send_message(user_text)