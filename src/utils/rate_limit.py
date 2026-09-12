"""Dependency-free in-memory sliding-window rate limiting.

Suitable for the single-container deployment (see Dockerfile): state is
per-process, resets on restart, and is not shared across replicas. A
deployment scaled to multiple instances needs a shared store (e.g. Redis).
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

# Keys are client IPs; if far too many accumulate (IP spoofing via
# X-Forwarded-For on a directly exposed instance), prune expired queues.
_MAX_TRACKED_KEYS = 10_000


def client_ip(request: Request) -> str:
    """Best-effort client IP. Trusts the first X-Forwarded-For hop, which is
    correct behind a trusted proxy (Vercel/reverse proxy) and spoofable on a
    directly exposed instance."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class SlidingWindowLimiter:
    """Tracks event timestamps per key inside a sliding window."""

    def __init__(self, max_events: int, window_seconds: float):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, q: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while q and q[0] <= cutoff:
            q.popleft()

    def count(self, key: str) -> int:
        now = time.monotonic()
        with self._lock:
            q = self._events.get(key)
            if not q:
                return 0
            self._prune(q, now)
            return len(q)

    def record(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._events) > _MAX_TRACKED_KEYS:
                for k in [k for k, v in self._events.items() if not v]:
                    del self._events[k]
            q = self._events[key]
            self._prune(q, now)
            q.append(now)

    def check(self, key: str) -> None:
        """Record a hit; raise 429 when the key is over its limit."""
        now = time.monotonic()
        with self._lock:
            q = self._events[key]
            self._prune(q, now)
            if len(q) >= self.max_events:
                raise HTTPException(
                    status_code=429, detail="Too many requests. Please try again later."
                )
            q.append(now)

    def blocked(self, key: str) -> bool:
        """True when the key is at/over its limit (without recording)."""
        return self.count(key) >= self.max_events

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)


# Public contact form: low volume expected; each submission costs SMTP quota.
contact_limiter = SlidingWindowLimiter(max_events=5, window_seconds=3600)

# Failed ops-token attempts: slows brute-forcing of OPS_TOKEN per IP.
ops_failure_limiter = SlidingWindowLimiter(max_events=10, window_seconds=300)
