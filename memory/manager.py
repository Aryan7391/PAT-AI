"""
PAT_7 Memory V1 — manager.py
The single interface between the Brain and the memory system.
Import this. Call nothing else directly.

Usage:
    from memory.manager import MemoryManager

    mm = MemoryManager()
    mm.load_chat(chat_id)   # or mm.create_chat("My Project")
    mm.save_message("user", "Hello")
    mm.save_message("assistant", "Hi there!")
    context = mm.get_recent()
    mm.close()
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import Optional

# ─────────────────────────────────────────
# Paths
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "memory.db")


class MemoryManager:

    def __init__(self):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Database not found at {DB_PATH}. Run init.py first."
            )
        self._conn = sqlite3.connect(DB_PATH,check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.row_factory = sqlite3.Row
        self._active_chat_id: Optional[int] = None

    # ─────────────────────────────────────
    # Connection
    # ─────────────────────────────────────

    def close(self) -> None:
        """Always call this when done."""
        self._conn.close()

    # ─────────────────────────────────────
    # User profile
    # ─────────────────────────────────────

    def get_user_profile(self) -> dict:
        """Return the user profile as a plain dict."""
        row = self._conn.execute("SELECT * FROM users WHERE id = 1").fetchone()
        if row is None:
            raise RuntimeError("No user profile found. Run init.py first.")
        return dict(row)

    def update_user(self, **kwargs) -> None:
        """
        Update one or more user profile fields.
        Allowed fields: name, language, timezone, ollama_model
        Example: mm.update_user(name="Aryan", ollama_model="mistral")
        """
        allowed = {"name", "language", "timezone", "ollama_model"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        sets = ", ".join(f"{k} = :{k}" for k in updates)
        updates["updated_at"] = _now()
        self._conn.execute(
            f"UPDATE users SET {sets}, updated_at = :updated_at WHERE id = 1",
            updates,
        )
        self._conn.commit()

    # ─────────────────────────────────────
    # Chat management
    # ─────────────────────────────────────

    def create_chat(self, name: str) -> int:
        """
        Create a new chat. Returns the new chat_id.
        Automatically sets it as the active chat.
        """
        cur = self._conn.execute(
            "INSERT INTO chats (name) VALUES (?)", (name,)
        )
        self._conn.commit()
        self._active_chat_id = cur.lastrowid
        return self._active_chat_id

    def list_chats(self) -> list[dict]:
        """Return all chats, most recently active first."""
        rows = self._conn.execute(
            "SELECT * FROM chats ORDER BY last_active DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def load_chat(self, chat_id: int) -> None:
        """
        Set a chat as active. Updates last_active timestamp.
        Raises ValueError if chat_id doesn't exist.
        """
        row = self._conn.execute(
            "SELECT id FROM chats WHERE id = ?", (chat_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Chat {chat_id} not found.")
        self._conn.execute(
            "UPDATE chats SET last_active = ? WHERE id = ?",
            (_now(), chat_id),
        )
        self._conn.commit()
        self._active_chat_id = chat_id

    def delete_chat(self, chat_id: int) -> None:
        """
        Delete a chat and all its messages (CASCADE handles messages).
        """
        self._conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        self._conn.commit()
        if self._active_chat_id == chat_id:
            self._active_chat_id = None

    def rename_chat(self, chat_id: int, new_name: str) -> None:
        self._conn.execute(
            "UPDATE chats SET name = ? WHERE id = ?", (new_name, chat_id)
        )
        self._conn.commit()

    # ─────────────────────────────────────
    # Messages
    # ─────────────────────────────────────

    def save_message(self, role: str, content: str) -> None:
        """
        Save a message to the active chat.
        role must be 'user' or 'assistant'.
        """
        self._require_active_chat()
        if role not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'.")
        self._conn.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (self._active_chat_id, role, content),
        )
        self._conn.execute(
            "UPDATE chats SET last_active = ? WHERE id = ?",
            (_now(), self._active_chat_id),
        )
        self._conn.commit()

    def get_recent(self, n: int = 20) -> list[dict]:
        """
        Return the last n messages from the active chat, oldest first.
        This is the primary context restore method.
        """
        self._require_active_chat()
        rows = self._conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (self._active_chat_id, n),
        ).fetchall()
        # Reverse so oldest is first (chronological order for the prompt)
        return [dict(r) for r in reversed(rows)]

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """
        Keyword search within the active chat.
        Returns matching messages, most recent first.
        query is matched as a substring (case-insensitive).
        """
        self._require_active_chat()
        rows = self._conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE chat_id = ?
              AND content LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (self._active_chat_id, f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def message_count(self) -> int:
        """Return total message count for the active chat."""
        self._require_active_chat()
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM messages WHERE chat_id = ?",
            (self._active_chat_id,),
        ).fetchone()
        return row["cnt"]

    # ─────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────

    def _require_active_chat(self) -> None:
        if self._active_chat_id is None:
            raise RuntimeError(
                "No active chat. Call create_chat() or load_chat() first."
            )

    @property
    def active_chat_id(self) -> Optional[int]:
        return self._active_chat_id


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
