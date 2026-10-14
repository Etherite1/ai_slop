import unittest

from market_data.application import MarketDataApplication
from market_data.clock import ManualClock

ROWS = [
    {"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": ["AAPL US", "APPLE"]},
    {"instrument_id": "EQ:MSFT", "symbol": "MSFT", "aliases": ["MSFT US"]},
]
SETTINGS = {"max_age_ms": 500, "snapshot_capacity": 4, "max_watchlists": 3,
            "max_instruments_per_watchlist": 3}


class QuoteTests(unittest.TestCase):
    def setUp(self):
        self.app = MarketDataApplication(ROWS, SETTINGS, ManualClock(1000))

    def test_alpha_quote_lookup_by_alias(self):
        result = self.app.ingest("alpha", {"ticker": "AAPL", "last": "189.250", "event_ms": 10})
        self.assertEqual(result, {"accepted": True})
        self.assertEqual(self.app.quote("APPLE")["price"], "189.250")

    def test_beta_quote_unit(self):
        self.app.ingest("beta", {"instrument": "MSFT US", "price": "415", "event_seconds": 2})
        self.assertEqual(self.app.quote("MSFT")["timestamp_ms"], 2000)

    def test_unknown_feed_and_instrument_rejected(self):
        with self.assertRaises(ValueError):
            self.app.ingest("gamma", {})
        with self.assertRaises(ValueError):
            self.app.ingest("alpha", {"ticker": "NOPE", "last": "1", "event_ms": 1})

    def test_invalid_event_does_not_add_quote(self):
        with self.assertRaises(ValueError):
            self.app.ingest("alpha", {"ticker": "AAPL", "last": "0", "event_ms": 1})
        self.assertEqual(self.app.quote("AAPL")["status"], "missing")

    def test_duplicate_event_is_ignored(self):
        event = {"ticker": "AAPL", "last": "10", "event_ms": 10}
        self.assertTrue(self.app.ingest("alpha", event)["accepted"])
        self.assertFalse(self.app.ingest("alpha", event)["accepted"])


if __name__ == "__main__":
    unittest.main()
