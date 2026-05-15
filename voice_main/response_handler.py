import re

# Spoken fallbacks per request type — used if LLM response cannot be parsed.
# Each must be a single sentence: the spoken output is hard-capped to sentences[0],
# so a two-sentence fallback would silently drop the second sentence every time.
SPOKEN_FALLBACKS = {
    "coding":      "The code is ready — check the screen for details.",
    "analysis":    "Analysis complete — check the screen for findings.",
    "explanation": "Here is the explanation — check the screen for details.",
    "planning":    "Plan is ready — check the screen for the full breakdown.",
    "general":     "I have a response for you — check the screen.",
}


def parse_response(raw_response: str, request_type: str = "general") -> tuple[str, str]:
    """Split LLM response into spoken summary and full display text.

    Expected LLM format:
        SPOKEN: <short spoken line>
        FULL:
        <complete response>

    The SPOKEN line is hard-capped to one sentence — re.DOTALL means the regex
    may capture multiple lines before FULL:, but the sentence-split below clips it.

    Args:
        raw_response:  Raw text from Ollama
        request_type:  Detected request type for fallback selection

    Returns:
        Tuple of (spoken, full) — both plain strings
    """
    if not raw_response or not raw_response.strip():
        fallback = SPOKEN_FALLBACKS.get(request_type, SPOKEN_FALLBACKS["general"])
        return fallback, "No response received."

    # Extract SPOKEN
    spoken_match = re.search(
        r'SPOKEN\s*:\s*(.+?)(?=FULL\s*:|$)',
        raw_response,
        re.IGNORECASE | re.DOTALL
    )

    # Extract FULL
    full_match = re.search(
        r'FULL\s*:\s*(.+)',
        raw_response,
        re.IGNORECASE | re.DOTALL
    )

    fallback = SPOKEN_FALLBACKS.get(request_type, SPOKEN_FALLBACKS["general"])
    spoken   = spoken_match.group(1).strip() if spoken_match else fallback
    full     = full_match.group(1).strip()   if full_match   else raw_response.strip()

    # Hard limit — spoken must be one sentence max
    sentences = re.split(r'(?<=[.!?]) +', spoken)
    spoken    = sentences[0] if sentences else spoken

    return spoken, full


if __name__ == "__main__":
    test = """SPOKEN: Here's a Python function that reads a CSV file using the csv module.
FULL:
Here is the complete code:

    import csv

    def read_csv(filepath):
        with open(filepath, newline='') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

This returns a list of dictionaries where each key is a column header.
"""
    spoken, full = parse_response(test, request_type="coding")
    print("── SPOKEN ──")
    print(spoken)
    print("\n── FULL ──")
    print(full)