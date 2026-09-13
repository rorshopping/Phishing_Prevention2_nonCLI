"""Rate-limit backends: in-memory default, optional shared Redis backend.

The Redis limiter is tested against an in-file fake implementing the few
commands used (zadd/zremrangebyscore/zcard/expire/delete/pipeline) — no
live Redis server is needed.
"""
import time

import pytest

from src.utils import rate_limit
from src.utils.rate_limit import RedisSlidingWindowLimiter, SlidingWindowLimiter


class FakeRedis:
    """Minimal sorted-set store with redis-py call shapes used by the limiter."""

    def __init__(self):
        self.zsets: dict[str, dict[str, float]] = {}
        self.fail = False

    def _raise_if_failing(self):
        if self.fail:
            raise ConnectionError("redis down")

    def delete(self, name):
        self.zsets.pop(name, None)

    def pipeline(self):
        return FakePipe(self)


class FakePipe:
    def __init__(self, store):
        self.store = store
        self.ops = []

    def zremrangebyscore(self, name, lo, hi):
        self.ops.append(("zrem", name, hi))
        return self

    def zadd(self, name, mapping):
        self.ops.append(("zadd", name, mapping))
        return self

    def zcard(self, name):
        self.ops.append(("zcard", name))
        return self

    def expire(self, name, seconds):
        return self

    def execute(self):
        out = []
        for op in self.ops:
            if op[0] == "zrem":
                z = self.store.zsets.setdefault(op[1], {})
                for member, score in list(z.items()):
                    if score <= op[2]:
                        del z[member]
                out.append(0)
            elif op[0] == "zadd":
                self.store.zsets.setdefault(op[1], {}).update(op[2])
                out.append(1)
            elif op[0] == "zcard":
                self.store._raise_if_failing()
                out.append(len(self.store.zsets.get(op[1], {})))
        self.ops = []
        return out


@pytest.fixture
def limiter():
    fake = FakeRedis()
    lim = RedisSlidingWindowLimiter(2, 60, "redis://localhost:6379/0")
    lim._redis = fake
    return lim


def test_redis_limiter_trips_at_max_events(limiter):
    limiter.check("1.2.3.4")
    limiter.check("1.2.3.4")
    with pytest.raises(Exception) as exc:
        limiter.check("1.2.3.4")
    assert getattr(exc.value, "status_code", None) == 429


def test_redis_limiter_window_expiry(limiter):
    limiter.record("k")
    limiter.record("k")
    assert limiter.count("k") == 2
    # age entries out of the window
    name = [n for n in limiter._redis.zsets][0]
    z = limiter._redis.zsets[name]
    for member in list(z):
        z[member] = time.time() - 999
    assert limiter.count("k") == 0
    limiter.check("k")  # allowed again


def test_redis_limiter_reset(limiter):
    limiter.record("k")
    limiter.reset("k")
    assert limiter.count("k") == 0


def test_redis_limiter_fails_open_on_outage(limiter):
    limiter.record("k")
    limiter.record("k")
    limiter._redis.fail = True
    assert limiter.count("k") == 0       # fail-open: reports zero
    limiter.check("k")                    # does not raise


def test_default_singletons_are_in_memory():
    assert isinstance(rate_limit.contact_limiter, SlidingWindowLimiter)
    assert not isinstance(rate_limit.contact_limiter, RedisSlidingWindowLimiter)


def test_builder_selects_redis_when_configured(monkeypatch):
    monkeypatch.setattr(rate_limit.settings, "redis_url", "redis://localhost:6379/0")
    lim = rate_limit._build_limiter(max_events=1, window_seconds=60)
    assert isinstance(lim, RedisSlidingWindowLimiter)


def test_builder_defaults_to_in_memory(monkeypatch):
    monkeypatch.setattr(rate_limit.settings, "redis_url", "")
    lim = rate_limit._build_limiter(max_events=1, window_seconds=60)
    assert type(lim) is SlidingWindowLimiter
