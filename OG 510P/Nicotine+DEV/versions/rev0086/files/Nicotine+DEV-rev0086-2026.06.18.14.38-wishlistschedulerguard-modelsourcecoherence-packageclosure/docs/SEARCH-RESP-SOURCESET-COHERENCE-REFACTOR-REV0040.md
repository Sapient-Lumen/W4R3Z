# SEARCH-RESP source-set coherence refactor — rev0040

## Refactor decision

Rev0039 split SEARCH-RESP-01 into user-source binding, room/buddy source modeling, and parser-budget materialization rows. Rev0040 refines the middle row again:

```text
SEARCH-RESP-01A / U-163A: direct user-source binding — production-gated in rev0039
SEARCH-RESP-01B-BUDDY / U-163B: buddy-source snapshot binding — production-gated in rev0040
SEARCH-RESP-01C-ROOM: room membership/freshness model — held
SEARCH-RESP-PARSE-BUDGET: invalid-token/list/private-result materialization budgets — held
```

## Why buddy mode is promotable now

Buddy-mode search is locally fan-out based. The client already iterates the local buddy list and sends one `UserSearch` per buddy. That means a request-time source set can be captured in the same `SearchRequest` that owns the token, and responses outside that snapshot can be rejected without touching global, wishlist, or room behavior.

## Why room mode remains held

Room-mode search uses a server `RoomSearch` request. The client’s local room user list can be stale, incomplete, or not meaningful for all compatibility cases at the instant a peer response arrives. A room hardening pass should model membership freshness explicitly before selecting a rejection or degraded-trust behavior.

## Why parser budgets remain held

The parser witnesses concern compressed-prefix handling, invalid-token parsing, public/private list materialization, and UI cap ordering. Those are availability/policy hardening problems in and around `FileSearchResponse` parsing, not source-set binding in `pynicotine/search.py`.

## Refactor effect on strict lane

The strict/front lane now has four production-gated packets:

```text
U-123: complete in rev0037
PB-01: complete in rev0038
SEARCH-RESP-01A: complete in rev0039
SEARCH-RESP-01B-BUDDY: complete in rev0040
```
