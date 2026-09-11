"""
User input ko clean aur safe banata hai:
- Empty / whitespace-only input reject
- Length limit lagata hai
- HTML/script tags strip karta hai
- Basic prompt-injection phrases detect kar ke reject karta hai
"""

import re

MAX_INPUT_LENGTH = 1000

_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"disregard (all )?(previous|above) instructions",
    r"reveal (your|the) (system )?prompt",
    r"you are now (a|an) ",
    r"jailbreak",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def sanitize_input(user_query: str) -> str:
    """
    Clean query string return karta hai, ya "" agar input invalid/unsafe hai.
    pipeline.py mein 'if not clean_query' se yeh check hota hai.
    """
    if not user_query or not isinstance(user_query, str):
        return ""

    text = user_query.strip()
    if not text:
        return ""

    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]

    text = _HTML_TAG_RE.sub("", text).strip()
    if not text:
        return ""

    if _INJECTION_RE.search(text):
        return ""

    return text