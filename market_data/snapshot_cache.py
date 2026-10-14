from collections import OrderedDict
from typing import Any


class SnapshotCache:
    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._entries: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._dependencies: dict[str, frozenset[str]] = {}
        self._by_instrument: dict[str, set[str]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> dict[str, Any] | None:
        value = self._entries.get(key)
        if value is None:
            self.misses += 1
            return None
        self.hits += 1
        self._entries.move_to_end(key)
        return value

    def put(self, key: str, value: dict[str, Any], dependencies: tuple[str, ...]) -> None:
        self.remove(key)
        self._entries[key] = value
        dep_set = frozenset(dependencies)
        self._dependencies[key] = dep_set
        for instrument_id in dep_set:
            self._by_instrument.setdefault(instrument_id, set()).add(key)
        while len(self._entries) > self._capacity:
            oldest = next(iter(self._entries))
            self.remove(oldest)

    def remove(self, key: str) -> None:
        self._entries.pop(key, None)
        for instrument_id in self._dependencies.pop(key, frozenset()):
            keys = self._by_instrument.get(instrument_id)
            if keys is not None:
                keys.discard(key)
                if not keys:
                    del self._by_instrument[instrument_id]

    def invalidate_instrument(self, instrument_id: str) -> None:
        for key in tuple(self._by_instrument.get(instrument_id, ())):
            self.remove(key)

    def invalidate_watchlist(self, watchlist_id: str) -> None:
        self.remove(watchlist_id)

    def stats(self) -> dict[str, int]:
        return {"hits": self.hits, "misses": self.misses, "entries": len(self._entries)}
