from decimal import Decimal, InvalidOperation
from typing import Any


def normalize_reference(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("instrument reference must be a string")
    result = value.strip().upper()
    if not result:
        raise ValueError("instrument reference must not be empty")
    return result


def integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def decimal_price(value: Any) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("price must be a decimal string")
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("price must be a valid decimal") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("price must be finite and positive")
    return result


def required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value.strip()
