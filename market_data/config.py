import json
from pathlib import Path
from typing import Any

from .validation import integer


def load_json(path: str | Path) -> Any:
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def load_settings(path: str | Path) -> dict[str, int]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("settings must be an object")
    return {
        "max_age_ms": integer(data.get("max_age_ms"), "max_age_ms"),
        "snapshot_capacity": integer(data.get("snapshot_capacity"), "snapshot_capacity", minimum=1),
        "max_watchlists": integer(data.get("max_watchlists"), "max_watchlists", minimum=1),
        "max_instruments_per_watchlist": integer(
            data.get("max_instruments_per_watchlist"), "max_instruments_per_watchlist", minimum=1
        ),
    }
