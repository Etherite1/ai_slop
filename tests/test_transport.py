import io
import json
import unittest

from market_data.application import MarketDataApplication
from market_data.cli import run_lines
from market_data.clock import ManualClock


class TransportTests(unittest.TestCase):
    def test_command_sequence_and_recovery(self):
        app = MarketDataApplication(
            [{"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": []}],
            {"max_age_ms": 500, "snapshot_capacity": 2, "max_watchlists": 2,
             "max_instruments_per_watchlist": 2}, ManualClock(1000))
        lines = [
            '{"op":"watchlist_create","watchlist_id":"w","instruments":["AAPL"]}',
            '{"op":"ingest","source":"alpha","payload":{"ticker":"AAPL","last":"3.14","event_ms":999}}',
            '{"op":"snapshot","watchlist_id":"w"}',
            '{"op":"unknown"}',
            '{"op":"quote","instrument":"AAPL"}',
        ]
        output = io.StringIO()
        run_lines(lines, output, app)
        values = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(values[2]["quotes"][0]["price"], "3.14")
        self.assertIn("error", values[3])
        self.assertEqual(values[4]["price"], "3.14")


if __name__ == "__main__":
    unittest.main()
