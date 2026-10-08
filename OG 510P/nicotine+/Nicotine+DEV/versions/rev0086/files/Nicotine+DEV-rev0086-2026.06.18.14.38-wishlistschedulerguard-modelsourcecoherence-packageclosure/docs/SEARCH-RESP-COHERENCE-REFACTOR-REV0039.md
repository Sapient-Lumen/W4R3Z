# SEARCH-RESP coherence refactor — rev0039

## Refactor decision

The old SEARCH-RESP-01 bundle mixed three different invariants:

1. direct user-search response source binding;
2. room/buddy response source-set or trust semantics;
3. parser-budget/materialization ordering for `FileSearchResponse` payloads.

Rev0039 promotes only the first invariant as SEARCH-RESP-01A because `UserSearch` has a clear expected user list at request time. The other two remain useful but require separate compatibility and budget models.

## Canonical split

```text
SEARCH-RESP-01A / U-163A: user-scoped FileSearchResponse source binding — production-gated in rev0039
SEARCH-RESP-01B: room/buddy source-set compatibility model — held
SEARCH-RESP-PARSE-BUDGET: invalid-token prefix and result-list materialization budgets — held
```

## Why not reject room responses in this patch?

The protocol-level room search flow intentionally asks the server to search users in a room. The local client may not have a complete, fresh, protocol-authenticated source set at the exact moment a result arrives. A room-source fix should either bind to a validated membership snapshot or explicitly downgrade trust without silently dropping compatible results. That is a separate design problem from direct user searches.

## Why not include parser budgets here?

The parser witnesses are real availability hardening evidence, but the fix surface is different: compressed prefix limits, accepted-list budgets, private-list policy ordering, and UI result caps. Those should not be bundled into a source-binding patch that lives in `pynicotine/search.py`.

## Refactor effect on the strict lane

The strict/front lane now has three production-gated packets:

```text
U-123: complete in rev0037
PB-01: complete in rev0038
SEARCH-RESP-01A: complete in rev0039
```

The next useful work is external filing/review of those packets or a separate held-backlog pass for SEARCH-RESP-01B / parser budgets.
