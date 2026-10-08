# SEARCH-RESP-PARSE-BUDGET-A — prefix cap production gate — rev0041

## Packet

`SEARCH-RESP-PARSE-BUDGET-A` isolates the pre-token username-prefix materialization behavior in `FileSearchResponse` parsing.

The source-traced parser path reads the first decompressed `uint32` as `username_len`, then requests `username_len + 4` more decompressed bytes to reach the token. Token rejection therefore happens after the advertised prefix body is materialized.

The selected invariant is deliberately small:

> Reject implausible `FileSearchResponse` username prefixes before inflating the peer-advertised prefix body needed to reach the token.

## Why this is separate from earlier packets

Rev0039 and rev0040 handled source binding after a response has a token and search object:

```text
SEARCH-RESP-01A: direct user-search response must come from the requested user set.
SEARCH-RESP-01B-BUDDY: buddy search must accept only the request-time buddy snapshot.
```

Rev0041 is earlier in the parser. It acts before token validation and before the response is admitted to any search result set.

## Regression evidence

The fixed-behavior regression has four cases:

```text
invalid token + overlong username prefix: reject before materializing prefix
valid token + overlong username prefix: reject before materializing prefix
normal valid empty-result response: still parses
30-byte login-name response: still parses
```

Matrix summary:

```text
current source + fixed regression:       2 failed / 2 passed on all three source lanes
selected patch + fixed regression:       4 passed on all three source lanes
selected patch + old current witness:    1 failed / 5 passed on all three source lanes
```

The old witness failure is the expected inversion of the former pre-token materialization assertion.

## Selected fix shape

The selected patch adds a parser-local cap:

```python
MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255
```

After reading the compressed `uint32 username_len`, the parser rejects lengths above this cap before asking zlib for `username_len + 4` output.

The cap is intentionally above Nicotine+'s normal login username length while still small enough to prevent a peer-controlled inflated prefix from being used as a pre-token budget bypass. Maintainers can replace it with an existing project constant if one is preferred.

## Production-gate result

Promoted in rev0041 as a production-gated maintainer-ready packet.

The report text, fixed regression, selected patch diffs, source trace, public-overlap note, and coherence split are included in this package.
