"""Visible tests. These encode part of the spec in ratelimit.py's docstring
and must not be weakened — the full spec is also exercised elsewhere."""

from ratelimit import RateLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_allows_up_to_limit_then_denies():
    clock = FakeClock()
    rl = RateLimiter(limit=3, window=10.0, clock=clock)
    assert rl.allow("k") and rl.allow("k") and rl.allow("k")
    assert not rl.allow("k")


def test_expired_calls_free_up_capacity():
    clock = FakeClock()
    rl = RateLimiter(limit=2, window=10.0, clock=clock)
    assert rl.allow("k") and rl.allow("k")
    clock.t = 10.5
    assert rl.allow("k")


def test_denied_calls_do_not_count_against_the_limit():
    clock = FakeClock()
    rl = RateLimiter(limit=2, window=10.0, clock=clock)
    assert rl.allow("k") and rl.allow("k")
    clock.t = 1.0
    assert not rl.allow("k")  # denied — must leave no trace
    clock.t = 10.5            # the two allowed calls (age 10.5) expired
    assert rl.allow("k")      # the denied call at t=1.0 must not block this
