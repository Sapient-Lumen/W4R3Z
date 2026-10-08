# ROOM-SERVER-STATE-01 maintainer hardening skeleton

## Summary

Room/list aggregate count arrays should be rejected when their lengths do not match the primary room/user arrays. Current behavior can either raise parser exceptions or create partial state with `None` counts/fields.

## Current-behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q   maintainer_artifacts/room-server-state-01/test_room_server_state_reproducer.py
```

Expected current result in the archived lanes:

```text
7 passed
```

## Proposed fixed behavior

- `RoomList`: reject sections where the user-count array length differs from room-name array length.
- `JoinRoom`: reject user-list responses where status/stats/slots/country counts differ from user count.
- Do not create partial `UserData` objects from malformed full-list messages.
- Do not pass `None` user counts into room-list UI formatting.

## Compatibility note

Empty lists and empty private-room sections should remain valid. The fix should target mismatched aggregate counts, not legitimate zero-count rooms.
