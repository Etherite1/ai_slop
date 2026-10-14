import unittest

from market_data.application import MarketDataApplication
from market_data.clock import ManualClock

ROWS = [{"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": []},
        {"instrument_id": "EQ:MSFT", "symbol": "MSFT", "aliases": []}]
SETTINGS = {"max_age_ms": 500, "snapshot_capacity": 2, "max_watchlists": 3,
            "max_instruments_per_watchlist": 3}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.app = MarketDataApplication(ROWS, SETTINGS, ManualClock(1000))
        self.app.watchlist_create("w", ["AAPL", "MSFT"])

    def test_missing_rows_preserve_membership_order(self):
        result = self.app.snapshot("w")
        self.assertEqual([r["symbol"] for r in result["quotes"]], ["AAPL", "MSFT"])
        self.assertTrue(all(r["status"] == "missing" for r in result["quotes"]))

    def test_snapshot_contains_quote_fields_after_ingest(self):
        self.app.ingest("alpha", {"ticker": "AAPL", "last": "12.5", "event_ms": 900})
        result = self.app.snapshot("w")
        self.assertEqual(result["quotes"][0]["price"], "12.5")
        self.assertEqual(result["quotes"][1]["status"], "missing")

    def test_canonical_update_invalidates_snapshot(self):
        self.app.snapshot("w")
        self.app.ingest("alpha", {"ticker": "EQ:AAPL", "last": "12.5", "event_ms": 900})
        self.assertEqual(self.app.snapshot("w")["quotes"][0]["price"], "12.5")

    def test_membership_change_invalidates_snapshot(self):
        self.app.snapshot("w")
        self.app.watchlist_replace("w", ["MSFT"])
        self.assertEqual([q["symbol"] for q in self.app.snapshot("w")["quotes"]], ["MSFT"])

    def test_symbol_update_invalidates_snapshot(self):
        self.app.snapshot("w")
        self.app.ingest("alpha", {"ticker": "AAPL", "last": "12.5", "event_ms": 900})
        self.assertEqual(self.app.snapshot("w")["quotes"][0]["price"], "12.5")

    def test_snapshot_responses_are_detached_on_miss_and_hit(self):
        for _ in range(2):
            result = self.app.snapshot("w")
            result["quotes"][0]["symbol"] = "changed"
            result["quotes"].clear()
            self.assertEqual([q["symbol"] for q in self.app.snapshot("w")["quotes"]], ["AAPL", "MSFT"])

    def test_cache_is_bounded_and_reports_hits(self):
        self.app.snapshot("w")
        self.app.snapshot("w")
        self.assertEqual(self.app.cache_stats()["hits"], 1)
        self.assertEqual(self.app.cache_stats()["entries"], 1)


if __name__ == "__main__":
    unittest.main()
