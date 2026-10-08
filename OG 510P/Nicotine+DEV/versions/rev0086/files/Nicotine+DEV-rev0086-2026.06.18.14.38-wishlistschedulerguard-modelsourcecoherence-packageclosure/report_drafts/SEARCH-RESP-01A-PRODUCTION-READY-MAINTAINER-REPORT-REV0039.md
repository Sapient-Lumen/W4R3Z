# SEARCH-RESP-01A maintainer report — user-scoped search-result source binding

## Summary

For direct user searches, Nicotine+ tracks the search by token but does not currently reject a `FileSearchResponse` whose connection username is outside the original requested user set. A response from `unexpected_peer` with an otherwise accepted token is admitted for a search that targeted `expected_peer`.

The proposed narrow fix is to bind user-scoped search responses to `search.users` in `Search._file_search_response()`. Broad modes are intentionally not changed by this report.

## Affected lanes checked

```text
github-tag-3.3.10: reproduced and fixed by selected guard
github-branch-3.3.x: reproduced and fixed by selected guard
github-branch-master: reproduced and fixed by selected guard
```

## Current behavior

The current-behavior witness from rev0013 still passes on all three archived lanes. The new fixed-behavior regression fails on current source in the two expected user-mode cases:

```text
current source + fixed regression:
  2 failed / 5 passed on each lane
```

## Fixed behavior

The selected patch passes the fixed regression on all three lanes:

```text
selected patch + fixed regression:
  7 passed on each lane
```

The old current-behavior witness then has exactly one expected inversion:

```text
selected patch + old current witness:
  1 failed / 5 passed on each lane
```

The failing old assertion is the one that previously expected an unrequested peer's user-scoped response to remain accepted.

## Suggested patch

For a direct user search, reject if the response source username is not in the originally requested user list:

```python
if search.mode == "user":
    expected_users = search.users or ()

    if username not in expected_users:
        msg.token = None
        return
```

Patch diffs for 3.3.10/3.3.x and master are included in this packet.

## Compatibility boundary

This report deliberately does not reject room, global, wishlist, or buddy-mode responses. Room/buddy source-set modeling and parser-budget/materialization hardening are split out as separate backlog items.

## Regression test

```text
maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py
```

## Rev0047 filing addendum

The paragraph above that says buddy/room source-set modeling and parser-budget hardening are backlog items is historical rev0039 language. As of rev0047, those companion rows are production-gated in the cube as SEARCH-RESP-01B-BUDDY, SEARCH-RESP-01C-ROOM, SEARCH-RESP-PARSE-BUDGET-A, and SEARCH-RESP-PARSE-BUDGET-B. This report's invariant remains direct user-search source binding only. Use `report_drafts/SEARCH-RESP-SERIES-MAINTAINER-COVER-REV0047.md` for the current series context.
