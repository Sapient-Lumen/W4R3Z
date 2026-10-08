# SEARCH-RESP-01A selected fix skeleton — rev0039

## Invariant

A `SearchRequest` with `mode == "user"` has an explicit requested-user set. A `FileSearchResponse` for that token should be admitted only when `msg.username` is in that set.

## Minimal code shape

```python
username = msg.username

if search.mode == "user":
    expected_users = search.users or ()

    if username not in expected_users:
        msg.token = None
        return
```

## Placement

- 3.3.10 / 3.3.x: after token/search lookup and `search.is_ignored` handling, before network-filter checks.
- master: after `search is None`, before wishlist ignore/network-filter checks.

## Regression coverage

```text
reject unexpected peer for user search
allow requested peer for user search
allow any of several requested peers
fail closed when a user-mode request has no expected users
preserve broad-source global compatibility
preserve broad-source room compatibility
preserve broad-source buddy compatibility in this narrow patch
```

## Deliberate non-goals

- No room-membership source-set enforcement in this revision.
- No parser-budget or decompression-budget changes in this revision.
- No token-generation redesign in this revision.
