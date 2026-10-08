# rev0043 SEARCH-RESP-01C room scope source trace

## Packet

`SEARCH-RESP-01C-ROOM` covers room-mode `FileSearchResponse` source admission. It is intentionally separate from:

- `SEARCH-RESP-01A`: direct `UserSearch` source binding;
- `SEARCH-RESP-01B-BUDDY`: local buddy fan-out snapshot binding;
- `SEARCH-RESP-PARSE-BUDGET-A/B`: parser materialization limits in `slskmessages.py`.

## Protocol/source anchors

Public protocol context and the archived source agree on the high-level room flow: `RoomSearch` is sent to the server with a client token and a room name; room users receive the request as `FileSearch`; `FileSearchResponse` carries the original search token back from a peer.

Archived source anchors:

| lane | room search sender | response handler | room membership state | protocol classes |
|---|---:|---:|---:|---:|
| github-tag-3.3.10 | `pynicotine/search.py:268-347` | `pynicotine/search.py:452-474` | `pynicotine/chatrooms.py:41-48`, `316-333`, `531-554` | `slskmessages.py:2301-2324`, `3234-3288` |
| github-branch-3.3.x | `pynicotine/search.py:268-347` | `pynicotine/search.py:452-474` | `pynicotine/chatrooms.py:41-48`, `316-333`, `531-554` | `slskmessages.py:2324-2347`, `3262-3316` |
| github-branch-master | `pynicotine/search.py:469-508` | `pynicotine/search.py:615-642` | `pynicotine/chatrooms.py:27-34`, `310-327`, `612-635` | `slskmessages.py:2413-2437`, `3435-3492` |

## Current behavior

The legacy and master handlers validate token existence, search object existence, ignored-user policy, and ignored-IP policy. They do not bind a room-mode result to a known room membership source set.

That means a `SearchRequest(mode="rooms", room="room-alpha")` accepts `FileSearchResponse` messages from a username that is not known in the requested room, as long as the message carries an allowed token and passes ignore filters. The old rev0013 witness keeps this broad behavior visible.

## Selected rev0043 model

Room search is not locally fan-out like buddy search. The local member list can be stale, incomplete, or absent when the server mediates `RoomSearch`. Rev0043 therefore rejects only when the client had a non-empty joined-room member snapshot at request time.

Selected invariant:

```text
if search.mode == "rooms" and search.users is not None:
    accept only msg.username in search.users
else:
    preserve broad-source compatibility for room searches without a usable snapshot
```

The patch stores the snapshot in the existing `SearchRequest.users` field, which the source already uses for user-mode targets and rev0040 uses for buddy-mode snapshots. Room sending still uses a single `RoomSearch(room, token, term)` server message; the snapshot is only a local admission guard for subsequent peer results.

## Verification evidence

See `evidence/rev0043-search-resp-room-scope-rerun-matrix.txt`:

```text
current witness on archived source:                         6 passed on all 3 lanes
current source + rev0043 room fixed regression:             3 failed / 5 passed on all 3 lanes
selected source-set patch + rev0043 room fixed regression:  8 passed on all 3 lanes
selected source-set patch + old current witness:            1 failed / 5 passed on all 3 lanes
```

The old-witness inversion is expected: the old direct-user broad-source assertion inverts because the selected patch stacks the prior rev0039 direct-user source guard. The old room assertion remains broad-compatible because it has no room membership snapshot.
