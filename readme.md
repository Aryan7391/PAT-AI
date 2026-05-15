# PAT_7

Persistent Local AI Assistant with Memory, Voice, and Browser Interface.

PAT_7 is a modular local AI system designed around:

* persistent conversational memory
* multi-chat architecture
* voice interaction
* local LLM orchestration
* browser-based UI
* offline-first design

Unlike traditional chatbots, PAT_7 is designed as a long-term cognition system where conversations persist across sessions and memory becomes part of the reasoning pipeline.

---

# Features

## Persistent Memory

* SQLite-based memory engine
* Multi-chat conversation storage
* Context retrieval system
* Memory-aware prompting

## Browser Interface

* ChatGPT / Claude style UI
* Sidebar chat navigation
* Persistent conversations
* Modern dark theme

## Voice Pipeline

* Push-to-talk recording
* Whisper transcription
* Voice → memory → LLM loop
* Integrated into browser runtime

## Local LLM Runtime

* Ollama integration
* Fully local execution
* Dynamic model selection
* Memory-aware prompting

## Modular Architecture

* Flask backend
* Memory abstraction layer
* Session orchestration
* Separate frontend/backend

---

# Architecture

```text
Browser UI
    ↓
Flask API Server
    ↓
Session Manager
    ↓
Memory Engine
    ↓
Prompt Pipeline
    ↓
Ollama
```

---

# Project Structure

```text
PAT_7/
│
├── memory/
│   ├── manager.py
│   ├── context.py
│   ├── init.py
│   ├── schema.sql
│   └── memory.db
│
├── server/
│   ├── server.py
│   └── session_manager.py
│
├── web/
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── style.css
│       └── app.js
│
├── recorder.py
├── transcriber.py
├── prompt_builder.py
├── prompt_optimizer.py
├── response_handler.py
├── ollama_client.py
│
└── README.md
```

---

# Requirements

## Software

* Python 3.11+
* Ollama
* Git

## Recommended Models

* `qwen2.5:3b`
* `llama3:8b`

---

# Installation Guide

---

# 1. Clone Repository

```bash
git clone <your-repo-url>
cd PAT_7
```

---

# 2. Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Python Dependencies

```bash
pip install flask flask-cors requests
```

Additional packages depending on your voice pipeline:

```bash
pip install openai-whisper sounddevice scipy numpy
```

---

# 4. Install Ollama

Download:

https://ollama.com/download

Verify installation:

```bash
ollama list
```

---

# 5. Pull a Model

Recommended lightweight model:

```bash
ollama pull qwen2.5:3b
```

Alternative:

```bash
ollama pull llama3:8b
```

---

# 6. Initialize Memory Database

Run:

```bash
python memory/init.py
```

You will be asked:

```text
Your name
Preferred language
Timezone
Default Ollama model
```

Example:

```text
Aryan
en
Asia/Kolkata
qwen2.5:3b
```

This creates:

* SQLite memory database
* user profile
* initial PAT_7 identity

---

# 7. Start Ollama

```bash
ollama serve
```

If you get:

```text
Only one usage of each socket address...
```

Ollama is already running.

---

# 8. Start PAT_7 Backend

From project root:

```bash
python server/server.py
```

You should see:

```text
Running on http://127.0.0.1:5000
```

---

# 9. Open Browser Interface

Open:

```text
http://127.0.0.1:5000
```

PAT_7 browser UI should load.

---

# First Usage

## Create Chat

* Click `+ New Chat`
* Enter chat name

## Send Message

* Type message
* Press Enter or Send

## Voice Input

* Press microphone button
* Speak
* Whisper transcribes automatically

---

# Memory System

PAT_7 stores:

| Memory Type     | Purpose                       |
| --------------- | ----------------------------- |
| User Profile    | Identity & preferences        |
| Chats           | Persistent conversations      |
| Messages        | Conversation history          |
| Context Builder | Memory injection into prompts |

Memory is loaded only for the active chat to avoid context contamination.

---

# Current Capabilities

* Persistent conversations
* Multi-chat architecture
* Local LLM execution
* Browser UI
* Voice interaction
* SQLite memory system
* Context injection
* Memory-aware prompting

---

# Planned Features

* Streaming responses
* Markdown rendering
* Semantic retrieval
* Vector search
* Long-term memory consolidation
* Autonomous planning
* Tool execution
* Voice streaming
* WebSocket realtime updates
* Multi-model routing

---

# Development Notes

## Current Backend Stack

| Layer       | Technology  |
| ----------- | ----------- |
| Frontend    | HTML/CSS/JS |
| Backend     | Flask       |
| Memory      | SQLite      |
| LLM Runtime | Ollama      |
| Voice STT   | Whisper     |

---

# Important Notes

## SQLite

Current implementation uses:

```python
check_same_thread=False
```

for Flask compatibility.

## Flask Debug

Use:

```python
debug=False
```

during runtime testing to avoid request interruption.

## Model Recommendation

Use smaller models during development:

* faster iteration
* lower latency
* easier debugging

Recommended:

```text
qwen2.5:3b
```

---

# Git Ignore

Recommended `.gitignore` includes:

* `*.db`
* recordings
* logs
* `__pycache__`
* virtual environments

---

# Vision

PAT_7 is intended to evolve beyond a chatbot into a persistent cognition system with:

* layered memory
* contextual reasoning
* adaptive behavior
* long-term conversational continuity

The focus is:

> memory-centric AI architecture
> rather than simple stateless chat interaction.
