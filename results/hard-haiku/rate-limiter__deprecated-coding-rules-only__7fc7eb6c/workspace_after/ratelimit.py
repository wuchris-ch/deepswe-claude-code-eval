"""Sliding-window rate limiter.

Spec (this docstring is the agreed contract)
--------------------------------------------
``RateLimiter(limit, window, clock=time.monotonic)``

- ``allow(key) -> bool``: allow the call iff the key has had fewer than
  ``limit`` *allowed* calls whose age is strictly less than ``window``
  seconds. An allowed call is recorded; a denied call must NOT be
  recorded and must not push future calls over the limit.
- Window boundary is half-open: a previous allowed call made exactly
  ``window`` seconds ago has expired (age < window counts, age >= window
  does not).
- Keys are fully independent of each other.
- ``remaining(key) -> int``: how many more calls would currently be
  allowed for the key. Never negative.
- Thread safety: ``allow`` may be called concurrently from many threads.
  With a window long enough that nothing expires, the total number of
  allowed calls for one key across all threads must never exceed
  ``limit`` — the check and the recording must be atomic with respect
  to other callers.
"""

import time
import threading


class RateLimiter:
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit = limit
        self.window = window
        self.clock = clock
        self._calls = {}
        self._lock = threading.Lock()

    def allow(self, key):
        now = self.clock()
        with self._lock:
            timestamps = self._calls.get(key, [])
            recent = [t for t in timestamps if now - t < self.window]
            if len(recent) < self.limit:
                recent.append(now)
                self._calls[key] = recent
                return True
            else:
                self._calls[key] = recent
                return False

    def remaining(self, key):
        now = self.clock()
        with self._lock:
            recent = [t for t in self._calls.get(key, []) if now - t < self.window]
            return max(0, self.limit - len(recent))
