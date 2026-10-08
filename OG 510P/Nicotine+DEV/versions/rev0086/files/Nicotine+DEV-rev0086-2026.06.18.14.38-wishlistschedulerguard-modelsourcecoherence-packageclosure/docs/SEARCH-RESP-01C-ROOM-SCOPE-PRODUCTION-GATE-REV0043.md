# SEARCH-RESP-01C-ROOM — room membership-snapshot production gate (rev0043)

## Promoted packet

`SEARCH-RESP-01C-ROOM` is promoted as a production-gated maintainer packet.

It covers one narrow source-admission invariant for room-mode search results: when a room search is created while the client has a non-empty joined-room member snapshot for the requested room, subsequent `FileSearchResponse` messages for that token should be accepted only from usernames in that request-time snapshot.

## Why this is not the same as buddy mode

Buddy mode is local fan-out: Nicotine+ iterates the local buddy list and sends one `UserSearch` per buddy. Room mode is server-mediated: Nicotine+ sends one `RoomSearch(room, token, term)` to the server, and room users receive a `FileSearch` request. The local client may or may not have a fresh room member list at the exact time the server relays the request.

Rev0043 therefore does **not** choose a blanket fail-closed room policy. It chooses a compatibility-preserving guard:

```text
- if a request-time joined-room user snapshot exists: bind responses to it;
- if no local snapshot exists: preserve current broad-source room compatibility.
```

## Current behavior witness

The current response handler accepts a room-mode response from any username that carries an allowed token and passes ignore filters. The old rev0013 witness still passes on all archived lanes.

The new fixed regression captures three desired room invariants:

1. a response from a username outside a request-time room snapshot is rejected;
2. a response from a snapshot member is preserved;
3. a room search without a usable local snapshot remains broad-source compatible.

It also verifies that the search object captures the room member snapshot when the client has one, and that the request-time snapshot, not later membership drift, controls response admission.

## Selected fix shape

The selected patch stacks the already-promoted source-set guards:

```text
- SEARCH-RESP-01A user source binding;
- SEARCH-RESP-01B-BUDDY request-time buddy snapshot binding;
- SEARCH-RESP-01C-ROOM request-time joined-room membership snapshot binding when available.
```

Room mode reuses `SearchRequest.users` as the local response-source snapshot. It does not change the outgoing protocol shape: the client still sends one `RoomSearch` to the server.

## Verification

```text
current rev0013 witness on archived source:
  github-tag-3.3.10:    6 passed
  github-branch-3.3.x:  6 passed
  github-branch-master: 6 passed

current source + rev0043 room fixed regression:
  github-tag-3.3.10:    3 failed / 5 passed
  github-branch-3.3.x:  3 failed / 5 passed
  github-branch-master: 3 failed / 5 passed

selected source-set patch + rev0043 room fixed regression:
  github-tag-3.3.10:    8 passed
  github-branch-3.3.x:  8 passed
  github-branch-master: 8 passed

selected source-set patch + old current witness:
  github-tag-3.3.10:    1 failed / 5 passed
  github-branch-3.3.x:  1 failed / 5 passed
  github-branch-master: 1 failed / 5 passed
```

A separate compatibility smoke file records that the selected source-set patch still passes the prior user and buddy fixed regressions on all three archived lanes.

## Production status

Production-gated maintainer packet: yes.
Production-ready report draft in cube: yes.
External filing status: not filed from this cube.
