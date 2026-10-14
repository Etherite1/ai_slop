from typing import Any

from .application import MarketDataApplication


def dispatch(app: MarketDataApplication, command: Any) -> Any:
    if not isinstance(command, dict):
        raise ValueError("command must be an object")
    op = command.get("op")
    if op == "ingest":
        return app.ingest(command.get("source"), command.get("payload"))
    if op == "quote":
        return app.quote(command.get("instrument"))
    if op == "watchlist_create":
        return app.watchlist_create(command.get("watchlist_id"), command.get("instruments"))
    if op == "watchlist_replace":
        return app.watchlist_replace(command.get("watchlist_id"), command.get("instruments"))
    if op == "watchlist_delete":
        return app.watchlist_delete(command.get("watchlist_id"))
    if op == "snapshot":
        return app.snapshot(command.get("watchlist_id"))
    if op == "cache_stats":
        return app.cache_stats()
    raise ValueError(f"unsupported operation: {op}")
