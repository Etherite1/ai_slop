# Service behavior

The JSON Lines adapter supports `ingest`, `quote`, `watchlist_create`, `watchlist_replace`, `watchlist_delete`, `snapshot`, and `cache_stats`. See the candidate README for examples and run commands.

Feed events use event time, not arrival time. Alpha uses `event_ms`; Beta uses `event_seconds` and is converted to milliseconds. Instrument references resolve to catalog IDs. Watchlists preserve first occurrence order after canonical-ID deduplication.

Snapshot output preserves membership order and includes missing rows. Repeated requests reflect accepted updates. The cache is bounded and eviction is semantically invisible. Returned dictionaries and nested lists are public response values.

An optional `include_freshness` snapshot argument is part of the requested extension. Existing callers omitting it must retain the existing response shape.
