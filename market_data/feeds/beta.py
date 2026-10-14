from typing import Any

from ..catalog import InstrumentCatalog
from ..models import QuoteEvent
from ..validation import decimal_price, integer


class BetaAdapter:
    def __init__(self, catalog: InstrumentCatalog) -> None:
        self._catalog = catalog

    def decode(self, payload: Any) -> QuoteEvent:
        if not isinstance(payload, dict):
            raise ValueError("beta payload must be an object")
        instrument = self._catalog.resolve(payload.get("instrument"))
        price = decimal_price(payload.get("price"))
        timestamp = integer(payload.get("event_seconds"), "event_seconds")
        return QuoteEvent(instrument.instrument_id, price, timestamp, "beta")
