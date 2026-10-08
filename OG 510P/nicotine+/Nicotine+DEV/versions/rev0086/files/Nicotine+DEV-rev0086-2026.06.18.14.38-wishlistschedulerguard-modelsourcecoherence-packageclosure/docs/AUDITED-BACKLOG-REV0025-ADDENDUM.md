# Audited backlog addendum — rev0025

## New verified audited-backlog packet

### PROTO-FRAME-PARSER-01 / U-137 + U-175

**Status:** verified across 3.3.10, 3.3.x, and master; **not strict-promoted**.

The maintainer-style witness confirms two related malformed-message parser gaps:

```text
U-137:
  final length-prefixed server/peer/distributed string fields can parse short payloads;
  the low-level bytes helper likewise returns the available bytes and an offset beyond the buffer.

U-175:
  server/peer frames with msg_size 0..3 are not rejected as shorter than the 4-byte code;
  distributed frames with msg_size 0 are not rejected as shorter than the 1-byte code.
```

The packet belongs in the audited backlog because the immediate consequence is protocol/parser robustness and fail-closed behavior. It should not displace U-123, PB-01, or SEARCH-RESP-01 in the strict/front lane.

## Updated next target

Next narrow target: **ROOM-SERVER-STATE-01 / U-111 + U-92**.

Reason: now that the generic short-field/frame behavior has been proven and pruned, the next risky parser-family question is whether concrete list/count mismatches in server room/list messages still produce user-visible crashes or state corruption. U-111 and U-92 should be tested as structured-count invariants, not as another broad parser manifesto.
