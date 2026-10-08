# Maintainer report draft — SEARCH-RESP-PARSE-BUDGET-A — rev0041

## Summary

`FileSearchResponse` parsing currently reaches the search token by inflating a peer-advertised username prefix. The parser reads a compressed `uint32 username_len`, then asks zlib to materialize `username_len + 4` bytes so it can unpack the token. This happens before token validation, so an invalid or stale-token response can still cause large pre-token decompression.

## Expected behavior

The parser should reject implausible pre-token username prefixes before materializing the peer-advertised prefix body.

## Reproducer

Add and run:

```text
maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py
```

Current source fails the two overlong-prefix cases and passes the two normal response cases on all three archived lanes.

## Selected patch

The selected fix adds a local cap before the `username_len + 4` decompression step:

```python
MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255
if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
    self.token = None
    self.list = []
    return
```

Master uses the same guard but returns from the memoryview parser shape.

## Verification

```text
current source + fixed regression:    2 failed / 2 passed on all three lanes
selected patch + fixed regression:    4 passed on all three lanes
selected patch + old current witness: 1 failed / 5 passed on all three lanes
```

The old-witness failure is expected because the selected patch prevents the old invalid-token pre-token inflate.

## Scope boundaries

This packet does not claim to solve direct-user or buddy source admission; those were handled separately in rev0039 and rev0040. It also does not claim to cap accepted result-list/private-list materialization; that remains held as SEARCH-RESP-PARSE-BUDGET-B.

## Rev0047 filing addendum

The statement above that SEARCH-RESP-PARSE-BUDGET-B remains held is historical rev0041 language. As of rev0047, B is production-gated as the accepted public/private result-count budget. This A report remains the compressed username-prefix cap packet; the current parser-budget filing context is in `report_drafts/SEARCH-RESP-SERIES-MAINTAINER-COVER-REV0047.md`.
