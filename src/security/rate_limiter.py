"""
Simple in-memory sliding-window rate limiter (per user_id).
Production mein multi-worker setups ke liye Redis-based limiter use karo,
kyunke yeh dict sirf ek process ki memory mein hota hai.
"""

import time
from collections import defaultdict, deque

MAX_REQUESTS = 10      # window ke andar max allowed requests
WINDOW_SECONDS = 60    # 1 minute window

_requests: dict = defaultdict(deque)


def is_rate_limited(user_id: str) -> bool:
    """True agar user ne WINDOW_SECONDS ke andar MAX_REQUESTS se zyada bheji hain."""
    now = time.time()
    q = _requests[user_id]

    while q and now - q[0] > WINDOW_SECONDS:
        q.popleft()

    if len(q) >= MAX_REQUESTS:
        return True

    q.append(now)
    return False