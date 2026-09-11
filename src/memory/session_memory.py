"""
In-memory session/conversation memory store.
Har user_id ke liye last N exchanges (Config.MAX_HISTORY) yaad rakhta hai.

NOTE: Yeh sirf process ki memory mein rehta hai — server restart ya
multiple workers (gunicorn/uvicorn --workers > 1) ke sath yeh consistent
nahi rahega. Production ke liye Redis ya DB-based store use karo.
"""

from config.settings import Config

# user_id -> list of {"query": ..., "reply": ...}
_session_store: dict = {}


def get_context(user_id: str) -> str:
    """
    User ki last exchanges ko ek readable string mein return karta hai,
    taake LLM ko conversation history context ke tor par di ja sake.
    """
    history = _session_store.get(user_id, [])
    if not history:
        return ""

    lines = []
    for turn in history:
        lines.append(f"User: {turn['query']}")
        lines.append(f"Bot: {turn['reply']}")
    return "\n".join(lines)


def add_to_memory(user_id: str, query: str, reply: str) -> None:
    """Naya exchange add karta hai aur sirf last MAX_HISTORY exchanges rakhta hai."""
    if user_id not in _session_store:
        _session_store[user_id] = []

    _session_store[user_id].append({"query": query, "reply": reply})

    max_history = getattr(Config, "MAX_HISTORY", 4)
    _session_store[user_id] = _session_store[user_id][-max_history:]


def clear_memory(user_id: str) -> None:
    """User ki memory clear karne ke liye (optional helper, e.g. '/reset' command)."""
    _session_store.pop(user_id, None)