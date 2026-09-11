"""
LLM ke jawab ko validate karta hai (grounding check):
1. Reply khali ya internal error na ho.
2. "I don't know" wala fallback valid response hai, allow karo.
3. Halka word-overlap based groundedness check — agar reply context se
   bilkul hi mel nahi khati to False return karo.
"""

import re

_FALLBACK_PHRASES = [
    "iska specific jawab",
    "i don't know",
    "not available",
    "contact our team",
    "contact support",
]

MIN_OVERLAP_RATIO = 0.15  # loose threshold, false positives kam karne ke liye


def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", text.lower()))


def validate_output(bot_reply: str, context_text: str) -> bool:
    if not bot_reply or not bot_reply.strip():
        return False

    # llm_client.py exception hone par "⚠️ Error generating response..." return karta hai
    if bot_reply.strip().startswith("⚠️ Error"):
        return False

    lowered = bot_reply.lower()
    if any(phrase in lowered for phrase in _FALLBACK_PHRASES):
        return True  # yeh "I don't know" wala valid fallback hai

    reply_tokens = _tokenize(bot_reply)
    context_tokens = _tokenize(context_text)

    if not reply_tokens:
        return False

    overlap = reply_tokens & context_tokens
    overlap_ratio = len(overlap) / len(reply_tokens)

    return overlap_ratio >= MIN_OVERLAP_RATIO