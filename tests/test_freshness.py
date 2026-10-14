import unittest

from market_data.application import MarketDataApplication
from market_data.clock import ManualClock
from market_data.transport import dispatch

ROWS = [{"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": ["APPLE"]}]
SETTINGS = {"max_age_ms": 500, "snapshot_capacity": 2, "max_watchlists": 2,
            "max_instruments_per_watchlist": 2}


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.clock = ManualClock(1500)
        self.app = MarketDataApplication(ROWS, SETTINGS, self.clock)
        self.app.ingest("alpha", {"ticker": "AAPL", "last": "10", "event_ms": 1000})

    def test_quote_freshness_boundary(self):
        result = self.app.quote("AAPL", include_freshness=True)
        self.assertEqual(result, {"instrument_id": "EQ:AAPL", "symbol": "AAPL",
                                  "price": "10", "timestamp_ms": 1000, "source": "alpha",
                                  "age_ms": 500, "status": "fresh"})
        self.clock.set(1501)
        result = self.app.quote("AAPL", include_freshness=True)
        self.assertEqual((result["age_ms"], result["status"]), (501, "stale"))

    def test_quote_dispatch_forwards_flag(self):
        result = dispatch(self.app, {"op": "quote", "instrument": "APPLE",
                                     "include_freshness": True})
        self.assertEqual(result.get("age_ms"), 500)
        self.assertEqual(result.get("status"), "fresh")


if __name__ == "__main__":
    unittest.main()
