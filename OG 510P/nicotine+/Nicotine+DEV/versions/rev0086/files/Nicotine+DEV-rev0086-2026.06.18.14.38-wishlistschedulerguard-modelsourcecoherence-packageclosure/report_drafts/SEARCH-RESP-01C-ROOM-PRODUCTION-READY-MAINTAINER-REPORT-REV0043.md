# Maintainer report draft — room search responses can be admitted outside a known room-membership source set

## Summary

Nicotine+ tracks outgoing room searches by token, but the room-mode `FileSearchResponse` handler does not bind an accepted response to the room membership source set when the client has one. A peer response from a username outside the request-time joined-room membership snapshot is accepted as long as it carries an allowed token and passes ignore filters.

A compatibility-preserving fix is to snapshot the joined room's current user set when sending a `RoomSearch`, but only when such a local non-empty snapshot exists. When a snapshot exists, accept responses for that token only from usernames in the snapshot. When no local room membership snapshot exists, preserve current broad-source room behavior.

## Affected paths

Archived source anchors:

```text
pynicotine/search.py
  room-mode search-term processing / RoomSearch send path
  _file_search_response() peer code 9 handler

pynicotine/chatrooms.py
  JoinedRoom.users membership state
  JoinRoom, user-joined-room, user-left-room updates

pynicotine/slskmessages.py
  RoomSearch protocol message
  FileSearchResponse token relationship
```

## Current behavior

The existing handler accepts a room-mode response from any username with an allowed token, unless ignored by username or IP. The response does not need to match a known local room membership snapshot.

The included fixed-behavior regression fails against current source on all three archived lanes:

```text
github-tag-3.3.10:    3 failed / 5 passed
github-branch-3.3.x:  3 failed / 5 passed
github-branch-master: 3 failed / 5 passed
```

## Desired behavior

For a room search token created while the client has a non-empty `core.chatrooms.joined_rooms[room].users` set:

```text
response username in request-time room snapshot       -> accept
response username outside request-time room snapshot  -> reject
```

For a room search token created without a usable local room snapshot:

```text
preserve current broad-source room compatibility
```

## Rationale for the compatibility carve-out

Room search is server-mediated. Unlike buddy mode, Nicotine+ does not locally send one request to each room user; it sends one `RoomSearch` to the server. The local room user list can be stale, absent, or not meaningful for every compatibility case. A blanket room-source rejection could silently drop legitimate responses. The proposed rule uses the snapshot only when the client actually has one.

## Regression included

```text
maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py
```

It verifies:

- non-snapshot users are rejected when a snapshot exists;
- snapshot users are preserved;
- no-snapshot room searches remain broad-source compatible;
- room search creation captures a request-time joined-room member snapshot;
- later membership drift does not expand the accepted source set for the already-issued token;
- global, requested user, and requested buddy positive paths remain compatible.

## Selected fix sketch

Use the existing `SearchRequest.users` field as a room-mode response-source snapshot:

```python
elif mode == "rooms":
    ...
    room_obj = getattr(getattr(core, "chatrooms", None), "joined_rooms", {}).get(room)
    if room_obj is not None and room_obj.users:
        users = tuple(room_obj.users)
```

Then in `_file_search_response()`:

```python
elif search.mode == "rooms" and search.users is not None:
    if msg.username not in search.users:
        msg.token = None
        return
```

Selected diffs are included for the archived 3.3.10, 3.3.x, and master source shapes.

## Verification

```text
current rev0013 witness on archived source:            6 passed on all 3 lanes
current source + rev0043 fixed regression:             3 failed / 5 passed on all 3 lanes
selected patch + rev0043 fixed regression:             8 passed on all 3 lanes
selected patch + old current witness:                  1 failed / 5 passed on all 3 lanes
selected patch + prior user/buddy fixed smoke tests:   passed on all 3 lanes
```

The old-witness inversion is expected because the selected patch stacks the already-promoted direct-user source guard.
