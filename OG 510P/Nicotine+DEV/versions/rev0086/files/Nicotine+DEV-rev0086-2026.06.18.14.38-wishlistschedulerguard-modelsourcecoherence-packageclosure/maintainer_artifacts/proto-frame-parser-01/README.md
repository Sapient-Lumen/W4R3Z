# PROTO-FRAME-PARSER-01 maintainer artifact

Current-behavior pytest witness for U-137 and U-175.

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_protocol_frame_and_truncated_field_reproducer.py
```

The assertions intentionally pass on current 3.3.10, 3.3.x, and master. A hardened parser would invert or replace these assertions with desired fail-closed behavior:

- length-prefixed string/bytes helpers should reject short payloads before returning a value;
- framed server/peer/distributed messages should reject `msg_size` values smaller than the mandatory code field before advancing the input buffer;
- fixes should be centralized so server, peer, distributed, embedded distributed, and fixed-width F-message paths do not drift apart.
