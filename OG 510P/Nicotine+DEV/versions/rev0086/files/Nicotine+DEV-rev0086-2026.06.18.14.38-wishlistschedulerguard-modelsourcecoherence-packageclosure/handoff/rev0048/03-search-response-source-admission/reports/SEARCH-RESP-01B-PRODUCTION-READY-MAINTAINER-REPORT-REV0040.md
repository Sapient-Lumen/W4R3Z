# SEARCH-RESP-01B maintainer report — buddy-scoped search-result source binding

## Summary

For buddy searches, Nicotine+ sends `UserSearch` requests to the local buddy list but does not bind incoming `FileSearchResponse` messages back to the request-time buddy source set. A response from `not_a_buddy` with an otherwise accepted token is admitted for a search that should be scoped to `buddy_a` and `buddy_b`.

The proposed narrow fix is to snapshot the buddy usernames into the `SearchRequest`, send the buddy search from that snapshot, and reject `FileSearchResponse` messages whose `msg.username` is outside `search.users` for normal buddy-mode searches. The selected patch is stacked with the rev0039 direct-user guard; manual/legacy buddy `SearchRequest` objects with `users is None` remain broad-source compatible, while normal empty snapshots fail closed.

## Affected lanes checked

```text
github-tag-3.3.10: reproduced and fixed by selected guard
github-branch-3.3.x: reproduced and fixed by selected guard
github-branch-master: reproduced and fixed by selected guard
```

## Current behavior

The new fixed-behavior regression fails on current source in the expected buddy-mode cases:

```text
current source + rev0040 buddy fixed regression:
  4 failed / 4 passed on each lane
```

The failed cases show that current source accepts out-of-snapshot buddy responses, fails open without a snapshot, does not store a buddy snapshot during search creation, and treats a later-added buddy as in-scope for an earlier token.

## Fixed behavior

The selected patch passes the fixed regression on all three lanes:

```text
selected source-set patch + fixed regression:
  8 passed on each lane
```

The old current-behavior witness then has exactly one expected inversion:

```text
selected source-set patch + old current witness:
  1 failed / 5 passed on each lane
```

The failing old assertion is the direct user-source assertion already inverted by rev0039. Room-mode and parser-materialization witnesses remain separate backlog work.

## Suggested patch

```python
# capture source set
users = tuple(core.buddies.users)

# send from the captured source set
users = search.users if search.users is not None else tuple(core.buddies.users)
for username in users:
    core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))

# response admission
if search.mode == "user":
    expected_users = search.users or ()

    if username not in expected_users:
        msg.token = None
        return

elif search.mode == "buddies" and search.users is not None:
    if username not in search.users:
        msg.token = None
        return
```

Patch diffs for 3.3.10/3.3.x and master are included in this packet.

## Compatibility boundary

This report deliberately does not reject room, global, or wishlist-mode responses. Room membership/freshness modeling and parser-budget/materialization hardening are split out as separate backlog items.

## Regression test

```text
maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py
```

## Rev0047 filing addendum

The text above that calls room-mode and parser-materialization work separate backlog items is historical rev0040 language. As of rev0047, room source gating and parser-budget rows are production-gated companion packets. This report remains the buddy-snapshot packet only; the current filing context is the stacked source-admission/parser-budget series in `report_drafts/SEARCH-RESP-SERIES-MAINTAINER-COVER-REV0047.md`.
