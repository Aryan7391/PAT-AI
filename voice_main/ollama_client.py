import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:3b"


def query_ollama(payload: dict, timeout: int = 120) -> str:
    """
    Send a memory-aware chat request to Ollama.

    Expected payload:
    {
        "model": "qwen2.5:3b",
        "system": "...",
        "messages": [
            {"role": "user", "content": "..."}
        ]
    }

    Returns:
        Assistant response string
    """

    model = payload.get("model", DEFAULT_MODEL)

    print(f"[PAT_7] Querying Ollama ({model})...")

    # Build final Ollama message list
    messages = []

    # Inject system prompt
    system_prompt = payload.get("system")
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    # Add conversation history
    messages.extend(payload.get("messages", []))

    request_payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=request_payload,
            timeout=timeout
        )

        response.raise_for_status()

        data = response.json()

        print("\n[PAT_7] Ollama raw response:")
        print(data)

        # Ollama /api/chat format
        message = data.get("message", {})
        content = message.get("content", "").strip()

        if not content:
            print("[PAT_7] Ollama returned empty content.")
            return ""

        print("[PAT_7] Response received.")
        return content

    except requests.exceptions.ConnectionError:
        print("[PAT_7] Cannot connect to Ollama.")
        print("[PAT_7] Run: ollama serve")
        return ""

    except requests.exceptions.Timeout:
        print(f"[PAT_7] Ollama timed out after {timeout}s.")
        return ""

    except requests.exceptions.RequestException as e:
        print(f"[PAT_7] Request error: {e}")
        return ""

    except Exception as e:
        print(f"[PAT_7] Unexpected error: {e}")
        return ""


if __name__ == "__main__":

    test_payload = {
        "model": "qwen2.5:3b",
        "system": "You are PAT_7.",
        "messages": [
            {
                "role": "user",
                "content": "Explain REST APIs briefly."
            }
        ]
    }

    result = query_ollama(test_payload)

    print("\n── Response ──")
    print(result)