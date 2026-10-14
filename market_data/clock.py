import time

from .validation import integer


class SystemClock:
    def now_ms(self) -> int:
        return time.time_ns() // 1_000_000


class ManualClock:
    def __init__(self, start_ms: int = 0) -> None:
        self._now_ms = integer(start_ms, "start_ms")

    def now_ms(self) -> int:
        return self._now_ms

    def set(self, now_ms: int) -> None:
        self._now_ms = integer(now_ms, "now_ms")
