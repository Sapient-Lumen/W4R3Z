# ADR 0154: Bound cumulative Ratox output-ack replay in constant space

Date: 2026-08-24

Status: accepted

## Context

The first two-guest 1,000-sample Ratox cell completed every direct-UDP input and render, then could
not close its session. A corrected repetition had the same outcome even with a 30-second local
packet deadline. The frozen session engine retained every `OUTPUT_ACK` in the never-evicted exact
control replay cache. That cache deliberately holds 128 entries, so a long-lived interactive
session exhausted it before `CLOSE` could reserve its own pre-effect replay entry.

Raising the cache bound only moves the failure. `OUTPUT_ACK` differs from resize, ping, detach, and
close: it carries one cumulative output coordinate, and acknowledging an already released prefix is
already an idempotent success. Attachment generation and ordered lossless delivery fence the route.
The per-session byte stream therefore has enough structure to bound acknowledgement replay without
retaining one record forever per rendered output.

## Decision

- Keep the Ratox v1 frame type, encoding, lossless carrier, attachment identity, and byte-sequence
  rules unchanged.
- Keep `OPEN`, `ATTACH`, `RESUME`, `RESIZE`, `PING`, `DETACH`, and `CLOSE` on their exact,
  never-evicted pre-effect replay paths.
- Treat `OUTPUT_ACK` as cumulative stream-coordinate state, like `INPUT`, rather than a permanent
  side-effect replay entry. Each active attachment retains only its newest acknowledged coordinate
  and message ID.
- Accept an exact repeat of that newest pair. Reject reuse of that message ID with different bytes,
  a lower message ID, a fresh acknowledgement that does not advance the coordinate, collision with
  a retained exact-control message ID, an invalid attachment, or an acknowledgement beyond produced
  output.
- Reset the acknowledgement fence on a new attachment generation. Do not carry it across route or
  generation replacement.
- Qualify the boundary with a deterministic 1,001-ack session while the exact-control replay cache
  is limited to one entry. The session must reject conflict/backward probes and still reserve and
  complete `CLOSE`.

## Consequences

Ratox sessions no longer have a hidden lifetime of 128 rendered acknowledgements. Memory remains
constant in session duration, and side-effecting controls retain the stronger exact-result replay
contract. The wire framing remains frozen at Ratox 1.0; this decision narrows receiver state for an
existing cumulative field rather than adding a packet or capability.

This does not make arbitrary control replay evictable, make lossy output safe, prove daemon-surviving
PTYs, or complete R7. The two diagnostic 1,000-sample failures are not evidence. A clean committed
build must still pass the complete two-guest matrix and the frozen latency thresholds.
