"""Hidden verification for the rate-limiter spec (ratelimit.py docstring)."""

import sys
import threading

from ratelimit import RateLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_boundary_is_half_open():
    clock = FakeClock()
    rl = RateLimiter(limit=1, window=10.0, clock=clock)
    assert rl.allow("k")
    clock.t = 9.999999
    assert not rl.allow("k")   # age < window: still counts
    clock.t = 10.0
    assert rl.allow("k")       # age == window: expired


def test_denied_calls_never_recorded_even_repeatedly():
    clock = FakeClock()
    rl = RateLimiter(limit=1, window=10.0, clock=clock)
    assert rl.allow("k")
    for i in range(50):
        clock.t = 0.1 + i * 0.1
        assert not rl.allow("k")
    clock.t = 10.0  # only the single allowed call existed, now expired
    assert rl.allow("k")


def test_remaining_is_never_negative_and_tracks_capacity():
    clock = FakeClock()
    rl = RateLimiter(limit=2, window=10.0, clock=clock)
    assert rl.remaining("k") == 2
    rl.allow("k")
    assert rl.remaining("k") == 1
    rl.allow("k")
    assert rl.remaining("k") == 0
    rl.allow("k")  # denied
    assert rl.remaining("k") == 0
    clock.t = 10.0
    assert rl.remaining("k") == 2


def test_keys_are_independent():
    clock = FakeClock()
    rl = RateLimiter(limit=1, window=10.0, clock=clock)
    assert rl.allow("a")
    assert rl.allow("b")
    assert not rl.allow("a")
    assert not rl.allow("b")


def test_concurrent_allow_never_exceeds_limit():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        for _ in range(5):
            rl = RateLimiter(limit=100, window=3600.0)
            allowed = []
            barrier = threading.Barrier(16)

            def worker():
                barrier.wait()
                mine = 0
                for _ in range(250):
                    if rl.allow("k"):
                        mine += 1
                allowed.append(mine)

            threads = [threading.Thread(target=worker) for _ in range(16)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            assert sum(allowed) == 100, f"allowed {sum(allowed)} of limit 100"
    finally:
        sys.setswitchinterval(old)
