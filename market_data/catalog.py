from typing import Any

from .models import Instrument
from .validation import normalize_reference, required_text


class InstrumentCatalog:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._by_reference: dict[str, Instrument] = {}
        self._by_id: dict[str, Instrument] = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("instrument entries must be objects")
            instrument_id = required_text(row.get("instrument_id"), "instrument_id")
            symbol = required_text(row.get("symbol"), "symbol")
            aliases = row.get("aliases", [])
            if not isinstance(aliases, list):
                raise ValueError("aliases must be a list")
            clean_aliases = tuple(required_text(a, "alias") for a in aliases)
            if instrument_id in self._by_id:
                raise ValueError(f"duplicate instrument id: {instrument_id}")
            instrument = Instrument(instrument_id, symbol, clean_aliases)
            self._by_id[instrument_id] = instrument
            for reference in (instrument_id, symbol, *clean_aliases):
                key = normalize_reference(reference)
                previous = self._by_reference.get(key)
                if previous is not None and previous.instrument_id != instrument_id:
                    raise ValueError(f"ambiguous instrument reference: {reference}")
                self._by_reference[key] = instrument

    def resolve(self, reference: str) -> Instrument:
        key = normalize_reference(reference)
        try:
            return self._by_reference[key]
        except KeyError as exc:
            raise ValueError(f"unknown instrument: {reference}") from exc

    def get(self, instrument_id: str) -> Instrument:
        try:
            return self._by_id[instrument_id]
        except KeyError as exc:
            raise ValueError(f"unknown instrument id: {instrument_id}") from exc

    def __len__(self) -> int:
        return len(self._by_id)
