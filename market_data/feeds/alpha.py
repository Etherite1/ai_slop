from typing import Any

from ..catalog import InstrumentCatalog
from ..models import QuoteEvent
from ..validation import decimal_price, integer


class AlphaAdapter:
    def __init__(self, catalog: InstrumentCatalog) -> None:
        self._catalog = catalog

    def decode(self, payload: Any) -> QuoteEvent:
        if not isinstance(payload, dict):
            raise ValueError("alpha payload must be an object")
        instrument = self._catalog.resolve(payload.get("ticker"))
        price = decimal_price(payload.get("last"))
        timestamp = integer(payload.get("event_ms"), "event_ms")
        return QuoteEvent(instrument.instrument_id, price, timestamp, "alpha")
