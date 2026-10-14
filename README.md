# Market-data service: debugging and a small feature

This Python 3.11+ project combines two simulated price feeds, an instrument catalog, watchlists, and snapshots. It uses only the standard library. No finance knowledge or installation is needed.

## Your assignment

Fix the following **three known bugs**, then add **one feature**. The starter intentionally fails tests for these tasks. Some tests report errors because the new API argument is not supported yet.

### 1. Convert Beta timestamps correctly

Alpha supplies integer milliseconds in `event_ms`. Beta supplies integer seconds in `event_seconds`. Both must be stored and returned in milliseconds.

Example: ingest Beta `{"instrument":"AAPL","price":"10","event_seconds":3}`, then look up AAPL. Its `timestamp_ms` must be `3000`, not `3`.

Start with `market_data/feeds/beta.py`. Visible tests: `test_feeds.py` and `test_quotes.py`.

### 2. Keep the newest quote

For each instrument, accept the first valid event and then only events whose timestamp is strictly greater than the stored timestamp. Feed source and arrival order provide no priority. Older or equal-time events return `{"accepted":false}` and leave the entire quote unchanged. Fully validate even an event that will be ignored.

Example: ingest Alpha price `"10"` at `2000`, then price `"9"` at `1000`. The second result must be `{"accepted":false}` and quote lookup must still return price `"10"` at `2000`.

Start with `market_data/quote_store.py`. Visible test: `test_quotes.py`.

### 3. Remove duplicate watchlist instruments

Create and replace must resolve references to canonical IDs, remove duplicates, and preserve first-occurrence order. Capacity applies to the number of distinct instruments, not the raw input length. Validate all references before changing state.

Example: `{"op":"watchlist_create","watchlist_id":"tech","instruments":["AAPL","APPLE","MSFT"]}` must return `{"watchlist_id":"tech","revision":1,"instrument_ids":["EQ:AAPL","EQ:MSFT"]}`.

Start with `market_data/watchlists.py`. Visible test: `test_watchlists.py`.

### 4. Add optional freshness to direct quote lookup

Add `include_freshness: bool = False` to `MarketDataApplication.quote` and forward the optional JSON field through `transport.dispatch`:

```json
{"op":"quote","instrument":"AAPL","include_freshness":true}
```

- Omitted or `false`: return the existing response unchanged.
- `true`, when a quote exists: add `age_ms` and `status` to the normal quote fields.
- Read the configured clock once for a present quote when freshness is enabled. Read it zero times otherwise, including missing quotes.
- `age_ms = max(0, now_ms - timestamp_ms)`.
- `status` is `"stale"` if `age_ms > max_age_ms`, otherwise `"fresh"`.
- Missing quotes keep the existing missing response, without `age_ms`.
- Any explicitly supplied non-boolean flag, including `null`, `0`, and `"true"`, is an error.
- Do not add `evaluated_at_ms` or change the snapshot API.

Example: for price `"10"` at timestamp `1000`, clock `1500`, and `max_age_ms=500`, return:

```json
{"instrument_id":"EQ:AAPL","symbol":"AAPL","price":"10","timestamp_ms":1000,"source":"alpha","age_ms":500,"status":"fresh"}
```

At clock `1501`, age is `501` and status is `"stale"`. Future timestamps have age zero. Compute freshness on every lookup.

Start with `market_data/application.py` and `market_data/transport.py`. Visible test: `test_freshness.py`.

## Completion criteria

All visible tests should pass after the three fixes and feature are complete. Add your own regression tests, particularly for ties, watchlist replacement, and freshness boundaries. Preserve existing validation, response shapes, and cache behavior. Explain your changes and how you verified them. You may use an AI assistant; review its output yourself.

## Architecture and existing behavior

`feeds/` decodes source payloads. `catalog.py` resolves trimmed, case-insensitive references. `quote_store.py` stores quotes; `watchlists.py` stores ordered membership. The application coordinates these components. Snapshots use a bounded LRU cache with targeted invalidation and detached responses. Cache invalidation and response isolation are already implemented correctly.

Prices are finite, positive decimal strings. Times are nonnegative integers, excluding booleans. Unknown references are errors. Invalid input does not mutate service state. Watchlist IDs are trimmed, case-sensitive nonempty strings. Create requires an unused ID; replace/delete require an existing ID. Creation starts at revision 1; every successful replace increments it. Empty watchlists are allowed.

See `docs/API.md` for command shapes. Catalog and limits are in `config/`. `ManualClock` lets tests control time without sleeping.

## Run

Run from this directory:

```sh
python3 -m unittest discover -s tests -v
python3 -m market_data.cli --clock manual --start-ms 1500 --input fixtures/routine_session.jsonl
python3 -m market_data.cli --clock manual --start-ms 1500 --input fixtures/customer_session.jsonl
```

Omit `--input` to read stdin. Each nonblank JSON line produces one JSON result. Invalid input yields an `error` object and processing continues.
