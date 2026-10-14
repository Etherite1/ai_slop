from dataclasses import dataclass

from .catalog import InstrumentCatalog
from .validation import required_text


@dataclass(frozen=True)
class Watchlist:
    watchlist_id: str
    revision: int
    instrument_ids: tuple[str, ...]


class WatchlistStore:
    def __init__(self, catalog: InstrumentCatalog, max_watchlists: int,
                 max_instruments: int) -> None:
        self._catalog = catalog
        self._max_watchlists = max_watchlists
        self._max_instruments = max_instruments
        self._items: dict[str, Watchlist] = {}

    def _prepare(self, watchlist_id: str, references: list[str]) -> tuple[str, tuple[str, ...]]:
        key = required_text(watchlist_id, "watchlist_id")
        if not isinstance(references, list):
            raise ValueError("instruments must be a list")
        ids: list[str] = []
        for reference in references:
            instrument_id = self._catalog.resolve(reference).instrument_id
            ids.append(instrument_id)
        if len(ids) > self._max_instruments:
            raise ValueError("watchlist instrument capacity exceeded")
        return key, tuple(ids)

    def create(self, watchlist_id: str, references: list[str]) -> Watchlist:
        key, ids = self._prepare(watchlist_id, references)
        if key in self._items:
            raise ValueError("watchlist already exists")
        if len(self._items) >= self._max_watchlists:
            raise ValueError("watchlist capacity exceeded")
        item = Watchlist(key, 1, ids)
        self._items[key] = item
        return item

    def replace(self, watchlist_id: str, references: list[str]) -> Watchlist:
        key, ids = self._prepare(watchlist_id, references)
        previous = self._items.get(key)
        if previous is None:
            raise ValueError("watchlist does not exist")
        item = Watchlist(key, previous.revision + 1, ids)
        self._items[key] = item
        return item

    def get(self, watchlist_id: str) -> Watchlist:
        key = required_text(watchlist_id, "watchlist_id")
        try:
            return self._items[key]
        except KeyError as exc:
            raise ValueError("watchlist does not exist") from exc

    def delete(self, watchlist_id: str) -> Watchlist:
        item = self.get(watchlist_id)
        del self._items[item.watchlist_id]
        return item
