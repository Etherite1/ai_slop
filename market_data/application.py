from typing import Any

from .catalog import InstrumentCatalog
from .clock import SystemClock
from .feeds import FeedRegistry
from .quote_store import QuoteStore
from .snapshot_cache import SnapshotCache
from .snapshots import SnapshotBuilder
from .validation import integer
from .watchlists import WatchlistStore


class MarketDataApplication:
    def __init__(self, catalog_rows: list[dict[str, Any]], settings: dict[str, int], clock: Any | None = None) -> None:
        if not isinstance(settings, dict):
            raise ValueError("settings must be an object")
        settings = {
            "max_age_ms": integer(settings.get("max_age_ms"), "max_age_ms"),
            "snapshot_capacity": integer(settings.get("snapshot_capacity"), "snapshot_capacity", minimum=1),
            "max_watchlists": integer(settings.get("max_watchlists"), "max_watchlists", minimum=1),
            "max_instruments_per_watchlist": integer(
                settings.get("max_instruments_per_watchlist"), "max_instruments_per_watchlist", minimum=1
            ),
        }
        self.catalog = InstrumentCatalog(catalog_rows)
        self.settings = settings
        self.clock = clock or SystemClock()
        self.feeds = FeedRegistry(self.catalog)
        self.quotes = QuoteStore(self.catalog)
        self.watchlists = WatchlistStore(
            self.catalog, settings["max_watchlists"], settings["max_instruments_per_watchlist"]
        )
        self.cache = SnapshotCache(settings["snapshot_capacity"])
        self.snapshots = SnapshotBuilder(self.catalog, self.quotes, self.cache)

    def ingest(self, source: str, payload: Any) -> dict[str, bool]:
        event = self.feeds.decode(source, payload)
        changed = self.quotes.apply(event)
        if changed:
            self.cache.invalidate_instrument(event.instrument_id)
        return {"accepted": changed}

    def quote(self, reference: str) -> dict[str, Any]:
        instrument = self.catalog.resolve(reference)
        quote = self.quotes.get(instrument.instrument_id)
        if quote is None:
            return {"instrument_id": instrument.instrument_id, "symbol": instrument.symbol,
                    "status": "missing"}
        return quote.to_dict()

    def watchlist_create(self, watchlist_id: str, instruments: list[str]) -> dict[str, Any]:
        item = self.watchlists.create(watchlist_id, instruments)
        return {"watchlist_id": item.watchlist_id, "revision": item.revision,
                "instrument_ids": list(item.instrument_ids)}

    def watchlist_replace(self, watchlist_id: str, instruments: list[str]) -> dict[str, Any]:
        item = self.watchlists.replace(watchlist_id, instruments)
        self.cache.invalidate_watchlist(item.watchlist_id)
        return {"watchlist_id": item.watchlist_id, "revision": item.revision,
                "instrument_ids": list(item.instrument_ids)}

    def watchlist_delete(self, watchlist_id: str) -> dict[str, Any]:
        item = self.watchlists.delete(watchlist_id)
        self.cache.invalidate_watchlist(item.watchlist_id)
        return {"deleted": item.watchlist_id}

    def snapshot(self, watchlist_id: str) -> dict[str, Any]:
        item = self.watchlists.get(watchlist_id)
        return self.snapshots.build(item)

    def cache_stats(self) -> dict[str, int]:
        return self.cache.stats()
