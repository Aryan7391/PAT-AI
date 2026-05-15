import re

# ── Filler words — ordered longest first to avoid partial matches ──────────
# Multi-word fillers must be handled on the full string (regex),
# single-word fillers are also handled the same way for consistency.
FILLER_PATTERNS = [
    # Multi-word (must come first)
    r'\byou\s+know\b',
    r'\bi\s+mean\b',
    r'\bsort\s+of\b',
    r'\bkind\s+of\b',
    r'\bokay\s+so\b',
    r'\bso\s+yeah\b',
    r'\byeah\s+so\b',
    r'\byou\s+see\b',
    r'\bi\s+guess\b',
    r'\bi\s+think\s+maybe\b',
    # Single-word
    r'\buh+\b',
    r'\bum+\b',
    r'\bhmm+\b',
    r'\bhm\b',
    r'\blike\b',
    r'\bbasically\b',
    r'\bactually\b',
    r'\bliterally\b',
    r'\bright\b',
]

# ── Informal speech → formal equivalents ──────────────────────────────────
CORRECTIONS = {
    # Contractions
    "gonna":   "going to",
    "wanna":   "want to",
    "gotta":   "got to",
    "gimme":   "give me",
    "lemme":   "let me",
    "kinda":   "kind of",
    "sorta":   "sort of",
    "dunno":   "do not know",
    "ain't":   "is not",
    "can't":   "cannot",
    "won't":   "will not",
    "doesn't": "does not",
    "didn't":  "did not",
    "isn't":   "is not",
    "aren't":  "are not",
    # Tech terms — always capitalize correctly
    "python":  "Python",
    "csv":     "CSV",
    "iot":     "IoT",
    "api":     "API",
    "llm":     "LLM",
    "ai":      "AI",
    "ml":      "ML",
    "sql":     "SQL",
    "html":    "HTML",
    "css":     "CSS",
    "json":    "JSON",
    "yaar":    "",           # informal filler (common in Indian English)
    "bro":     "",
}

# Phase 2 — Hinglish tokens that Whisper sometimes mishears.
# Currently unused: flagging logic for low-confidence passthrough is not yet implemented.
# Expand this list as real transcription errors are observed in testing.
KNOWN_HINGLISH = ["yaar", "matlab", "bas", "theek", "haan", "nahi"]


def remove_fillers(text: str) -> str:
    """Remove all filler patterns from text using full-string regex."""
    for pattern in FILLER_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text


def apply_corrections(text: str) -> str:
    """
    Replace informal words with proper equivalents.
    Works word-by-word but preserves attached punctuation.
    """
    words  = text.split()
    result = []
    for word in words:
        stripped = word.strip('.,!?;:')
        punct    = word[len(stripped):]
        lower    = stripped.lower()
        if lower in CORRECTIONS:
            replacement = CORRECTIONS[lower]
            if replacement:                         # empty string = drop the word
                result.append(replacement + punct)
        else:
            result.append(word)
    return ' '.join(result)


def clean_whitespace(text: str) -> str:
    """Remove extra spaces and fix punctuation spacing."""
    text = re.sub(r' +', ' ', text)                # collapse multiple spaces
    text = re.sub(r' ([.,!?;:])', r'\1', text)     # no space before punctuation
    return text.strip()


def fix_pronoun_i(text: str) -> str:
    """Ensure standalone 'i' is always capitalized."""
    return re.sub(r'\bi\b', 'I', text)


def capitalize_sentences(text: str) -> str:
    """Ensure each sentence starts with a capital letter."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(s.capitalize() for s in sentences)


def ensure_punctuation(text: str) -> str:
    """Add a period at the end if no terminal punctuation exists."""
    if text and text[-1] not in '.!?':
        text += '.'
    return text


def optimize(raw_text: str) -> str:
    """
    Layer 1 — Rule-based prompt optimizer.
    Transforms raw Whisper output into a clean, accurate prompt.

    Pipeline:
        remove_fillers → clean_whitespace → capitalize_sentences
        → fix_pronoun_i → apply_corrections → clean_whitespace
        → ensure_punctuation

    Args:
        raw_text: Raw transcription from Whisper

    Returns:
        Cleaned, optimized prompt string
    """
    if not raw_text or not raw_text.strip():
        return ""

    print(f"[PAT_7] Raw input:  '{raw_text}'")

    text = raw_text
    text = remove_fillers(text)         # remove fillers first (full-string regex)
    text = clean_whitespace(text)       # collapse gaps left by filler removal
    text = capitalize_sentences(text)   # capitalize after cleaning
    text = fix_pronoun_i(text)          # fix standalone 'i'
    text = apply_corrections(text)      # apply word-level corrections last
    text = clean_whitespace(text)       # final cleanup
    text = ensure_punctuation(text)     # terminal punctuation

    print(f"[PAT_7] Optimized:  '{text}'")
    return text


if __name__ == "__main__":
    test_inputs = [
        "uh can you like analyse this dataset and tell me what is wrong",
        "i wanna build a python script that gonna read csv files",
        "hmm so basically i need you to uh check the architecture design",
        "okay so can you like help me understand the iot connection setup",
        "you know i kind of want to sort of check the api response yaar",
        "i think maybe we should uh look at the json output bro",
    ]

    print("=" * 60)
    print("PAT_7 — Prompt Optimizer Layer 1 Test")
    print("=" * 60)

    for test in test_inputs:
        print()
        optimize(test)
        print("-" * 60)