# SEARCH-RESP-01 scope and parse-order proof — rev0013

## Lead decision

**Promote SEARCH-RESP-01 / U-163 as a strict report-candidate.** Do not promote U-262, U-267, or U-266 separately.

## Current-behavior witness

```text
maintainer_artifacts/search-resp-01/test_search_response_scope_and_parse_order_reproducer.py
```

Run result:

```text
github-tag-3.3.10: 6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Proven behavior

1. A user-scoped search response is accepted from an unexpected peer when the token is allowed.
2. A room-scoped search response is accepted from an unvetted peer when the token is allowed.
3. Search tokens start in a reduced initial range and then increment linearly.
4. Private result rows are materialized by the parser before the private-result display preference is applied by the GUI path.
5. Invalid-token rejection still decompresses the peer-controlled username prefix far enough to read the token.
6. Accepted responses can materialize large public result lists before visible-result caps are enforced.

## What this is not

- Not code execution.
- Not standalone file disclosure.
- Not proof that token guessing is trivial in every deployment.
- Not a reason to break global/wishlist compatibility, where broad result sources are expected.

## Fix-shape constraints

- User-scoped searches need a request-generation/source constraint: expected user, expected connection/source, and token.
- Room/buddy searches need either an expected source set or explicit degraded-trust handling if the protocol cannot provide a robust membership proof at response time.
- Global/wishlist searches should remain broad-source compatible, but still benefit from generation tracking and bounded parse budgets.
- Parser checks should reject invalid, stale, over-budget, or out-of-scope responses before private/full-list materialization where message shape allows it.
