from copy import deepcopy
from typing import Any

from .catalog import InstrumentCatalog
from .quote_store import QuoteStore
from .snapshot_cache import SnapshotCache
from .watchlists import Watchlist


class SnapshotBuilder:
    def __init__(self, catalog: InstrumentCatalog, quotes: QuoteStore,
                 cache: SnapshotCache) -> None:
        self._catalog = catalog
        self._quotes = quotes
        self._cache = cache

    def build(self, watchlist: Watchlist) -> dict[str, Any]:
        cached = self._cache.get(watchlist.watchlist_id)
        if cached is not None and cached["revision"] == watchlist.revision:
            return deepcopy(cached)
        rows: list[dict[str, Any]] = []
        for instrument_id in watchlist.instrument_ids:
            instrument = self._catalog.get(instrument_id)
            quote = self._quotes.get(instrument_id)
            if quote is None:
                rows.append({"instrument_id": instrument_id, "symbol": instrument.symbol,
                             "status": "missing"})
            else:
                rows.append(quote.to_dict())
        result = {"watchlist_id": watchlist.watchlist_id,
                  "revision": watchlist.revision, "quotes": rows}
        self._cache.put(watchlist.watchlist_id, result, watchlist.instrument_ids)
        return deepcopy(result)
