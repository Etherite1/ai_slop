import unittest

from market_data.application import MarketDataApplication
from market_data.clock import ManualClock

ROWS = [{"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": ["APPLE"]},
        {"instrument_id": "EQ:MSFT", "symbol": "MSFT", "aliases": []}]
SETTINGS = {"max_age_ms": 500, "snapshot_capacity": 2, "max_watchlists": 2,
            "max_instruments_per_watchlist": 2}


class WatchlistTests(unittest.TestCase):
    def setUp(self):
        self.app = MarketDataApplication(ROWS, SETTINGS, ManualClock(1000))

    def test_create_deduplicates_canonical_ids_in_order(self):
        self.app = MarketDataApplication(ROWS, {**SETTINGS, "max_instruments_per_watchlist": 3})
        result = self.app.watchlist_create("w", ["APPLE", "MSFT", "AAPL"])
        self.assertEqual(result["instrument_ids"], ["EQ:AAPL", "EQ:MSFT"])
        self.assertEqual(result["revision"], 1)

    def test_replace_increments_revision_even_when_unchanged(self):
        self.app.watchlist_create("w", ["AAPL"])
        self.assertEqual(self.app.watchlist_replace("w", ["AAPL"])["revision"], 2)

    def test_invalid_replacement_is_atomic(self):
        self.app.watchlist_create("w", ["AAPL"])
        with self.assertRaises(ValueError):
            self.app.watchlist_replace("w", ["MSFT", "unknown"])
        self.assertEqual(self.app.watchlists.get("w").instrument_ids, ("EQ:AAPL",))

    def test_duplicate_and_absent_operations_rejected(self):
        with self.assertRaises(ValueError):
            self.app.watchlist_replace("absent", [])
        self.app.watchlist_create("w", [])
        with self.assertRaises(ValueError):
            self.app.watchlist_create("w", [])

    def test_delete_and_recreate_starts_at_revision_one(self):
        self.app.watchlist_create("w", ["AAPL"])
        self.app.watchlist_delete("w")
        self.assertEqual(self.app.watchlist_create("w", ["MSFT"])["revision"], 1)


if __name__ == "__main__":
    unittest.main()
