# Market-data watchlist service

This self-contained service combines two simulated market-data feeds, an instrument catalog, watchlists, latest quotes, and cached snapshots. It uses Python 3.11+ and the standard library only.

## Interview task

Customers report that snapshots sometimes show an old price while direct instrument lookup shows the current price. Delayed feed messages also occasionally cause a price to revert. A caller reports that modifying one returned snapshot can affect a subsequent request.

Investigate and fix these inconsistencies. Extend the snapshot API with an optional `include_freshness` flag. When enabled, include freshness information for each instrument using the configured clock and age limit. Preserve the existing response shape when the flag is omitted. Add tests and be ready to explain the code paths, trade-offs, complexity, and validation. You may use the integrated AI agent and are responsible for reviewing its work.

## Architecture

`feeds/` decodes each source into normalized quote events. `catalog.py` maps display symbols and aliases to canonical IDs. The application coordinates quote ingestion, watchlists, snapshots, and cache invalidation. `SnapshotCache` is bounded and tracks which cached watchlists depend on each instrument. `ManualClock` makes time-dependent behavior testable without sleeping.

Instrument catalog and capacity defaults are in `config/`. JSON Lines examples are in `fixtures/`.

## Contract

- Instrument references are case-insensitive and trimmed. Canonical IDs are the identity used for quote storage and watchlist membership. Unknown references are errors.
- Alpha event time is integer milliseconds; Beta event time is integer seconds converted to milliseconds.
- Prices are finite, positive decimal strings. Times are nonnegative integers (booleans are not integers for this API). Invalid input does not mutate service state.
- Latest quote means greatest event timestamp across feeds. Equal timestamps preserve the existing quote. Source does not provide priority.
- Watchlist IDs are trimmed, case-sensitive nonempty strings. Create requires an unused ID; replace/delete require an existing ID. Creation starts at revision 1; each successful replace increments it. Watchlist items resolve to canonical IDs, are deduplicated preserving first-occurrence order, and may be empty.
- A snapshot contains `watchlist_id`, `revision`, and ordered `quotes`. Present rows contain canonical ID, display symbol, price string, timestamp, and source. Missing rows contain canonical ID, display symbol, and `status: "missing"`.
- Snapshots reflect accepted updates completed before the request. Cache eviction must not change results. Responses are caller-owned values; changing a returned object must not affect subsequent results.
- Cache capacity and watchlist/instrument limits are configured in settings. Cache invalidation should target affected content; retain the bounded cache and dependency bookkeeping.
- The freshness extension must add `evaluated_at_ms` to the top level and `status`/`age_ms` to present rows only when explicitly enabled. Use one clock read per request; age is `max(0, now - timestamp_ms)` and stale iff age exceeds `max_age_ms`. Missing rows remain missing. Time advancement alone can change freshness.

## Commands and run

Each nonblank line is one JSON command and produces one JSON result. Invalid input yields an `error` object and processing continues.

```json
{"op":"ingest","source":"alpha","payload":{"ticker":"AAPL","last":"189.25","event_ms":1000}}
{"op":"quote","instrument":"APPLE"}
{"op":"watchlist_create","watchlist_id":"tech","instruments":["AAPL","MSFT US"]}
{"op":"snapshot","watchlist_id":"tech"}
```

Other operations are `watchlist_replace`, `watchlist_delete`, and `cache_stats`. In manual clock mode, `clock_set` accepts `now_ms`.

```sh
python3 -m unittest discover -s tests -v
python3 -m market_data.cli --clock manual --start-ms 1000 --input fixtures/routine_session.jsonl
python3 -m market_data.cli --clock manual --start-ms 1000 --input fixtures/customer_session.jsonl
```

Omit `--input` to read stdin. CLI defaults for catalog/settings are relative to the candidate directory.
