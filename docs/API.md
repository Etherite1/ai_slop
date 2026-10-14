# JSON Lines API

Each nonblank input line is a JSON object. Each produces one result. Invalid input produces `{"error":"..."}` and the next line is still processed. Extra fields are ignored, except the requested quote freshness flag, which must be a boolean.

| Operation | Fields | Result |
|---|---|---|
| `ingest` | `source`, `payload` | `{"accepted":true}` for a first/newer event, false for older/tied events |
| `quote` | `instrument`, optional `include_freshness` | A present or missing quote as described below |
| `watchlist_create` | `watchlist_id`, `instruments` | ID, revision 1, ordered distinct canonical `instrument_ids` |
| `watchlist_replace` | `watchlist_id`, `instruments` | ID, incremented revision, ordered distinct canonical `instrument_ids` |
| `watchlist_delete` | `watchlist_id` | `{"deleted":"the-id"}` |
| `snapshot` | `watchlist_id` | `watchlist_id`, `revision`, ordered `quotes` |
| `cache_stats` | none | `hits`, `misses`, `entries` |
| `clock_set` | `now_ms` | `{"now_ms":1500}`; CLI manual-clock mode only |

## Feed inputs

```json
{"op":"ingest","source":"alpha","payload":{"ticker":"AAPL","last":"10.00","event_ms":1000}}
{"op":"ingest","source":"beta","payload":{"instrument":"APPLE","price":"11","event_seconds":2}}
```

Alpha time is milliseconds; Beta time is seconds converted to milliseconds. Prices must be finite, positive decimal strings; timestamps must be nonnegative integers, not booleans. Resolve references by trimming and uppercasing. Fully validate every event before deciding whether its time is newer. Tied timestamps preserve the existing quote in full.

## Quote lookup and requested extension

```json
{"op":"quote","instrument":"APPLE"}
```

Present response:

```json
{"instrument_id":"EQ:AAPL","symbol":"AAPL","price":"10.00","timestamp_ms":1000,"source":"alpha"}
```

Missing response for a known instrument:

```json
{"instrument_id":"EQ:MSFT","symbol":"MSFT","status":"missing"}
```

Unknown references are errors. The requested optional `include_freshness` flag defaults to false. False/omitted preserves these exact shapes. True adds `age_ms` and `status` (`fresh` or `stale`) to present quotes only. Compute age as `max(0, now_ms - timestamp_ms)` using one clock read. Stale means age strictly exceeds configured `max_age_ms`. Missing responses stay unchanged with no clock read. Reject nonboolean flags before accessing the clock. No `evaluated_at_ms` field is required.

Python signature to implement: `quote(reference: str, include_freshness: bool = False)`.

## Watchlists and snapshots

```json
{"op":"watchlist_create","watchlist_id":"tech","instruments":["AAPL","APPLE","MSFT"]}
{"op":"snapshot","watchlist_id":"tech"}
```

Create/replace deduplicates resolved canonical IDs preserving first-occurrence order. Capacity counts distinct IDs. Validate the full input before mutating a watchlist. Empty lists are allowed. IDs are trimmed and case-sensitive. Create requires an unused ID; replace/delete require an existing ID.

Snapshot rows follow membership order and include missing instruments. Present rows have the normal five quote fields; missing rows have ID, symbol, and `status: "missing"`. Snapshots reflect accepted updates and return independent nested values. Bounded LRU cache eviction affects performance only. Snapshot freshness is outside this assignment.
