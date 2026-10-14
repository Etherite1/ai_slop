import unittest
from decimal import Decimal

from market_data.catalog import InstrumentCatalog
from market_data.feeds import FeedRegistry


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.feeds = FeedRegistry(InstrumentCatalog([
            {"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": ["AAPL US"]}
        ]))

    def test_alpha_milliseconds_and_alias(self):
        event = self.feeds.decode("alpha", {"ticker": "AAPL US", "last": "10.125", "event_ms": 15})
        self.assertEqual((event.instrument_id, event.timestamp_ms, event.price),
                         ("EQ:AAPL", 15, Decimal("10.125")))

    def test_beta_seconds_conversion(self):
        event = self.feeds.decode("beta", {"instrument": "AAPL", "price": "11", "event_seconds": 2})
        self.assertEqual(event.timestamp_ms, 2000)

    def test_rejects_bad_values(self):
        for payload in ({"ticker": "AAPL", "last": "NaN", "event_ms": 1},
                        {"ticker": "AAPL", "last": "1", "event_ms": True}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.feeds.decode("alpha", payload)


if __name__ == "__main__":
    unittest.main()
