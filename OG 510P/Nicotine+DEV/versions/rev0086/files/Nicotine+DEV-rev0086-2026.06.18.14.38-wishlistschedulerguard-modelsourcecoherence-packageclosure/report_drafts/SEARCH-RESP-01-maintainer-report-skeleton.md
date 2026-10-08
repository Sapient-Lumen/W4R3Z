# SEARCH-RESP-01 maintainer report skeleton

## Summary

FileSearchResponse acceptance is currently centered on an allowed search token. For user-scoped and room-scoped searches, the main-thread handler does not bind the response to the expected requester scope, target user, room membership/source, socket, or request generation. Search tokens start in a reduced initial range and then increment linearly. Supporting parser-ordering checks also show that private result rows and full accepted result lists are materialized before later UI/display policy has a chance to drop them, and invalid-token rejection still decompresses the peer-controlled username prefix far enough to read the token.

## Affected source lanes checked

```text
github-tag-3.3.10: reproduced
github-branch-3.3.x: reproduced
github-branch-master: reproduced
```

## Boundaries

- Peer-driven search-result integrity and availability hardening.
- Not code execution.
- Not standalone file disclosure.
- Strongest integrity story requires token knowledge or prediction; token shape and parser-budget behavior are supporting factors, not proof of trivial exploitation.

## Current-behavior witness

```text
maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py
```

Observed current result:

```text
github-tag-3.3.10: 6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Fix-shape sketch

- Represent accepted search responses as `(token, mode, generation, expected source constraints)` rather than token-only.
- For user search, accept a response only from the expected requested user/source/generation.
- For room and buddy searches, either encode the expected source set/generation or document why broad peer responses are protocol-compatible and downgrade the UI trust accordingly.
- Keep global/wishlist compatibility: global search genuinely expects broad responses, but still should obey token generation and bounded parse budgets.
- Move cheap, scope-aware rejection before expensive private/full-list materialization where message shape allows it.
- Add parser budgets for prefix fields that must be decompressed before token validation.

## Public-overlap status

Public search-result performance and private-result display discussions exist. No direct public issue was found for the combined user-scoped/room-scoped token-only response acceptance invariant during the rev0013 pass. Treat novelty as candidate/no-direct-public-found, public-adjacent.
