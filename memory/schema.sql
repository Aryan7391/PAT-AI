-- PAT_7 Memory V1 — Schema
-- SQLite only. Run once via init.py.
-- Do not edit manually after first run.

-- ─────────────────────────────────────────
-- TABLE 1: users
-- One row. Written on first run, updated on preference change.
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY CHECK (id = 1),  -- enforces single row
    name            TEXT    NOT NULL,
    language        TEXT    NOT NULL DEFAULT 'en',
    timezone        TEXT    NOT NULL DEFAULT 'UTC',
    ollama_model    TEXT    NOT NULL DEFAULT 'qwen2.5:3b',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────
-- TABLE 2: chats
-- One row per chat/project. Fully independent.
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    last_active     TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────
-- TABLE 3: messages
-- One row per message. Scoped to a chat.
-- role: 'user' or 'assistant'
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id         INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role            TEXT    NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Index for fast message retrieval by chat
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);

-- Index for keyword search on content
CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);
