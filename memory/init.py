"""
PAT_7 Memory V1 — init.py
Run once on first install. Safe to re-run — won't overwrite existing data.

What it does:
  1. Creates the SQLite database file
  2. Runs schema.sql to create all tables and indexes
  3. If no user exists, prompts for profile and writes the users row
"""

import sqlite3
import os

# ─────────────────────────────────────────
# Paths
# ─────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "memory.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_connection() -> sqlite3.Connection:
    """Return a connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def run_schema(conn: sqlite3.Connection) -> None:
    """Create tables and indexes from schema.sql."""
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn.executescript(schema)
    print("  [ok] Schema applied.")


def user_exists(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT id FROM users WHERE id = 1").fetchone()
    return row is not None


def prompt_user_profile() -> dict:
    """Interactive first-run CLI. All fields have sensible defaults."""
    print("\n  PAT_7 first run — let's set up your profile.")
    print("  Press Enter to accept the default shown in brackets.\n")

    name = input("  Your name: ").strip()
    while not name:
        name = input("  Name cannot be empty. Your name: ").strip()

    language = input("  Preferred language [en]: ").strip() or "en"
    timezone = input("  Your timezone [UTC]: ").strip() or "UTC"
    model    = input("  Default Ollama model [qwen2.5:3b]: ").strip() or "qwen2.5:3b"

    return {
        "name":         name,
        "language":     language,
        "timezone":     timezone,
        "ollama_model": model,
    }


def create_user(conn: sqlite3.Connection, profile: dict) -> None:
    conn.execute(
        """
        INSERT INTO users (id, name, language, timezone, ollama_model)
        VALUES (1, :name, :language, :timezone, :ollama_model)
        """,
        profile,
    )
    conn.commit()
    print(f"\n  [ok] User profile saved — welcome, {profile['name']}.")


def main() -> None:
    print("\nPAT_7 Memory — initialising...")

    # 1. Connect (creates the .db file if it doesn't exist)
    conn = get_connection()
    print(f"  [ok] Database: {DB_PATH}")

    # 2. Apply schema
    run_schema(conn)

    # 3. First-run user setup
    if user_exists(conn):
        row = conn.execute("SELECT name FROM users WHERE id = 1").fetchone()
        print(f"  [ok] User already exists: {row['name']}. Nothing changed.")
    else:
        profile = prompt_user_profile()
        create_user(conn, profile)

    conn.close()
    print("\nDone. Run manager.py next.\n")


if __name__ == "__main__":
    main()
