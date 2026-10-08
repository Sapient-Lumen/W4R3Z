# Audited backlog addendum — rev0041

## Promoted

`SEARCH-RESP-PARSE-BUDGET-A / U-267A` is promoted to production-gated status.

Rationale: the row now has a narrow fixed-behavior regression, a selected parser-local patch shape, source traces across all three archived lanes, and old-witness inversion evidence.

## Held

`SEARCH-RESP-PARSE-BUDGET-B` remains held. It covers materialization of accepted public/private result lists after token acceptance and should not be treated as fixed by the prefix cap.

`SEARCH-RESP-01C-ROOM` remains held. Room membership and freshness require a separate compatibility model.

`U-138` remains deferred as a lower-priority media-parser materialization row.
