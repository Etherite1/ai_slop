import unittest

from market_data.catalog import InstrumentCatalog

ROWS = [{"instrument_id": "EQ:AAPL", "symbol": "AAPL", "aliases": ["AAPL US", "APPLE"]}]


class CatalogTests(unittest.TestCase):
    def test_resolves_id_symbol_and_alias(self):
        catalog = InstrumentCatalog(ROWS)
        for ref in ("EQ:AAPL", "aapl", " Apple ", "AAPL US"):
            self.assertEqual(catalog.resolve(ref).instrument_id, "EQ:AAPL")

    def test_rejects_ambiguous_alias(self):
        with self.assertRaises(ValueError):
            InstrumentCatalog(ROWS + [{"instrument_id": "EQ:OTHER", "symbol": "OTHER", "aliases": ["APPLE"]}])

    def test_rejects_empty_alias(self):
        with self.assertRaises(ValueError):
            InstrumentCatalog([{"instrument_id": "X", "symbol": "X", "aliases": [" "]}])


if __name__ == "__main__":
    unittest.main()
