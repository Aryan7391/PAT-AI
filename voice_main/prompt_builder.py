# ── Request type keyword map ───────────────────────────────────────────────
# Checked in order — first match wins.
# If no match, falls back to LLM classification.

KEYWORD_MAP = {
    "coding": [
        "code", "script", "function", "class", "debug", "error",
        "fix", "build", "program", "implement", "write a", "python",
        "javascript", "java", "c++", "sql", "api", "module", "loop",
        "algorithm", "compile", "syntax", "import", "library"
    ],
    "analysis": [
        "analyse", "analyze", "analysis", "dataset", "data", "csv",
        "trend", "pattern", "anomaly", "compare", "chart", "graph",
        "statistics", "metric", "report", "insight", "revenue",
        "performance", "evaluate", "correlation"
    ],
    "explanation": [
        "explain", "what is", "what are", "how does", "how do",
        "tell me about", "describe", "definition", "meaning",
        "difference between", "why is", "why does"
    ],
    "planning": [
        "plan", "design", "architecture", "structure", "roadmap",
        "strategy", "approach", "steps", "how to", "guide",
        "checklist", "outline", "organise", "organize"
    ],
    "general": []   # fallback — always matches last
}

# ── Prompt templates per request type ─────────────────────────────────────

TEMPLATES = {
    "coding": """You are PAT_7, a Jarvis-like AI assistant. The user has given you a coding request.

Request: {prompt}

Respond in this exact format:

SPOKEN: <One sentence. Say what you built or what the code does. Natural, spoken English.>
FULL:
<Complete working code with brief inline comments. Add a short explanation after the code block if needed.>
""",

    "analysis": """You are PAT_7, a Jarvis-like AI assistant. The user has given you a data analysis request.

Request: {prompt}

Respond in this exact format:

SPOKEN: <One sentence. Give the single most important finding. Direct and clear.>
FULL:
<Full analysis with key findings, observations, and recommendations clearly structured.>
""",

    "explanation": """You are PAT_7, a Jarvis-like AI assistant. The user wants something explained.

Request: {prompt}

Respond in this exact format:

SPOKEN: <One sentence. The core idea in plain English.>
FULL:
<Clear, well-structured explanation. Use examples where helpful.>
""",

    "planning": """You are PAT_7, a Jarvis-like AI assistant. The user wants help planning or designing something.

Request: {prompt}

Respond in this exact format:

SPOKEN: <One sentence. Summarise the approach or key recommendation.>
FULL:
<Detailed plan, steps, or architecture. Structured and actionable.>
""",

    "general": """You are PAT_7, a Jarvis-like AI assistant. Answer the user's request.

Request: {prompt}

Respond in this exact format:

SPOKEN: <One sentence. The most useful thing to say out loud.>
FULL:
<Complete, helpful response.>
"""
}

# ── Classification prompt (used when keyword match fails) ──────────────────

CLASSIFICATION_PROMPT = """Classify the following request into exactly one of these categories:
coding, analysis, explanation, planning, general

Request: {prompt}

Reply with only the category name. Nothing else."""


def detect_type_by_keywords(prompt: str) -> str | None:
    """
    Try to detect request type using keyword matching.

    Returns:
        Request type string, or None if no match found
    """
    lower = prompt.lower()

    for request_type, keywords in KEYWORD_MAP.items():
        if request_type == "general":
            continue
        for keyword in keywords:
            if keyword in lower:
                return request_type

    return None


def detect_type_by_llm(prompt: str, ollama_query_fn) -> str:
    """Phase 2 — LLM-based request classification.

    Called by build_prompt when keyword matching returns no match.
    Not yet active: build_prompt currently defaults to 'general' on keyword miss.

    Args:
        prompt:          The user's optimized prompt
        ollama_query_fn: The query_ollama function from ollama_client

    Returns:
        Request type string — always returns a valid type
    """
    classification_prompt = CLASSIFICATION_PROMPT.format(prompt=prompt)

    print("[PAT_7] Classifying request type via LLM...")
    response = ollama_query_fn(classification_prompt, timeout=15)

    detected = response.strip().lower()

    # Validate — must be one of the known types
    if detected in TEMPLATES:
        print(f"[PAT_7] Request type (LLM): {detected}")
        return detected

    print(f"[PAT_7] LLM returned unknown type '{detected}' — defaulting to general.")
    return "general"


def build_prompt(optimized_text: str, ollama_query_fn=None) -> tuple[str, str]:
    """Build a structured LLM prompt from the optimized voice input.

    Steps:
        1. Try keyword detection first (fast, no model overhead)
        2. Phase 2: call detect_type_by_llm when ollama_query_fn is provided
        3. Default to 'general' if no keyword match and LLM unavailable

    Args:
        optimized_text:  Clean prompt from the Voice Module optimizer
        ollama_query_fn: Reserved for Phase 2 LLM classification fallback

    Returns:
        Tuple of (request_type, built_prompt)
    """
    if not optimized_text or not optimized_text.strip():
        return "general", ""

    # Keyword detection — default to general if no match
    request_type = detect_type_by_keywords(optimized_text) or "general"
    print(f"[PAT_7] Request type: {request_type}")

    template     = TEMPLATES.get(request_type, TEMPLATES["general"])
    built_prompt = template.format(prompt=optimized_text)

    return request_type, built_prompt


if __name__ == "__main__":
    # Test keyword detection only
    tests = [
        "Write a Python function to read a CSV file.",
        "Analyse the revenue trends in the dataset.",
        "Explain what a decorator is in Python.",
        "Plan the architecture for a REST API.",
        "What is the weather like today?",
    ]

    print("=" * 60)
    print("PAT_7 — Prompt Builder Test (keyword detection only)")
    print("=" * 60)

    for test in tests:
        detected = detect_type_by_keywords(test)
        print(f"\nInput:   {test}")
        print(f"Type:    {detected or 'no match → LLM fallback'}")