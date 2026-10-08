# FileSearchResponse series cover note — rev0047

Use this note as the current wrapper for the five production-gated search-response packets. Some individual report drafts were written before later companion packets were promoted; rev0047 addenda now mark that historical language.

## Series A — source admission in `pynicotine/search.py`

```text
SEARCH-RESP-01A: direct user searches admit responses only from the requested user set.
SEARCH-RESP-01B-BUDDY: buddy searches snapshot the request-time buddy set.
SEARCH-RESP-01C-ROOM: room searches snapshot joined-room users when a local non-empty snapshot exists; no-snapshot room searches remain broad-source compatible.
```

Current stacked patch: the rev0043 room-source patch contains the rev0039 user guard and rev0040 buddy snapshot guard.

## Series B — parser budgets in `pynicotine/slskmessages.py`

```text
SEARCH-RESP-PARSE-BUDGET-A: cap implausible compressed username prefixes before inflating enough bytes to reach the token.
SEARCH-RESP-PARSE-BUDGET-B: cap accepted public+private result-row materialization after token validation.
```

Current stacked patch: the rev0042 result-count patch contains the rev0041 username-prefix cap.

## Recommended commit split

```text
commit 1: direct user-source guard
commit 2: buddy request-time source snapshot
commit 3: room snapshot guard with no-snapshot compatibility carve-out
commit 4: compressed username-prefix cap
commit 5: accepted result-row count budget
```
