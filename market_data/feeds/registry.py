from typing import Any

from ..catalog import InstrumentCatalog
from ..models import QuoteEvent
from .alpha import AlphaAdapter
from .beta import BetaAdapter


class FeedRegistry:
    def __init__(self, catalog: InstrumentCatalog) -> None:
        self._adapters = {"alpha": AlphaAdapter(catalog), "beta": BetaAdapter(catalog)}

    def decode(self, source: str, payload: Any) -> QuoteEvent:
        try:
            adapter = self._adapters[source]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"unsupported feed source: {source}") from exc
        return adapter.decode(payload)
