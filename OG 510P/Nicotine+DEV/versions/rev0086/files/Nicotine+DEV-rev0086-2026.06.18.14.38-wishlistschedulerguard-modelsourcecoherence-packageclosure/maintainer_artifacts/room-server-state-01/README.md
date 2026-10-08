# ROOM-SERVER-STATE-01 maintainer artifact

Current-behavior pytest witness for ROOM-SERVER-STATE-01 / U-111 + U-92.

Run against an archived or live Nicotine+ source lane:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_room_server_state_reproducer.py
```

The assertions describe current behavior, not desired fixed behavior. They keep the finding narrow:

- count arrays larger than the room/user array can raise parser `IndexError`;
- incoming framed server messages hit the network parser exception path and are logged/ignored, not necessarily fatal;
- count arrays smaller than the room/user array can leave `None` in room/user state;
- the surviving `None` room-count path reaches the same count-formatting helper used by the room-list UI and raises `TypeError` in the witness.

Expected fixed-behavior tests should invert the malformed-count assertions: reject aggregate count mismatches at parse/admission time and never pass `None` counts into room-list UI state.
