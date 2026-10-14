from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Instrument:
    instrument_id: str
    symbol: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class QuoteEvent:
    instrument_id: str
    price: Decimal
    timestamp_ms: int
    source: str


@dataclass(frozen=True)
class Quote:
    instrument_id: str
    symbol: str
    price: Decimal
    timestamp_ms: int
    source: str

    def to_dict(self) -> dict[str, str | int]:
        return {"instrument_id": self.instrument_id, "symbol": self.symbol,
                "price": str(self.price), "timestamp_ms": self.timestamp_ms,
                "source": self.source}
