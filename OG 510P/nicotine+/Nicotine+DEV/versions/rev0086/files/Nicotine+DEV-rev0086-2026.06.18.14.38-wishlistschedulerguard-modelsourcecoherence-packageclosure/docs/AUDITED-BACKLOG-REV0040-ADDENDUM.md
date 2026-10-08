# Audited backlog addendum — rev0040

## Queue delta

Rev0040 promotes the buddy-source portion of the rev0039 held SEARCH-RESP-01B row and deliberately leaves room membership and parser-budget work separate.

```text
promoted: SEARCH-RESP-01B-BUDDY / U-163B
held:     SEARCH-RESP-01C-ROOM
held:     SEARCH-RESP-PARSE-BUDGET
held:     U-138
```

## Updated interpretation

The old phrase “room/buddy source-set compatibility model” was too coarse. Buddy source binding has a concrete local source set because buddy searches are sent as per-user `UserSearch` requests. Room searches require a separate server-mediated membership/freshness model.

## Next queue

1. External filing/review for U-123, PB-01, SEARCH-RESP-01A, SEARCH-RESP-01B-BUDDY.
2. If continuing cube-internal work, model SEARCH-RESP-01C-ROOM with explicit membership freshness and compatibility assumptions.
3. Then consider SEARCH-RESP-PARSE-BUDGET or return to deferred media-parser U-138.
