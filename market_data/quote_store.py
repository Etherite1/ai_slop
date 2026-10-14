from .catalog import InstrumentCatalog
from .models import Quote, QuoteEvent


class QuoteStore:
    def __init__(self, catalog: InstrumentCatalog) -> None:
        self._catalog = catalog
        self._quotes: dict[str, Quote] = {}

    def apply(self, event: QuoteEvent) -> bool:
        instrument = self._catalog.get(event.instrument_id)
        quote = Quote(instrument.instrument_id, instrument.symbol, event.price,
                      event.timestamp_ms, event.source)
        previous = self._quotes.get(event.instrument_id)
        if previous == quote:
            return False
        self._quotes[event.instrument_id] = quote
        return True

    def get(self, instrument_id: str) -> Quote | None:
        return self._quotes.get(instrument_id)
