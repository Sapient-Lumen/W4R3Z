# ADR 0265: Qualify fresh Ratox admission after content backlog

Status: accepted, 2026-08-30.

## Context

ADR 0264 proved that one already-open Ratox attachment survives reliable content-v2 load, but its
first multi-session harness failed to open a new cap-4 terminal after earlier bulk phases. Persistent
attachment survival and fresh admission are different lifecycle claims. The failure could have been
remote admission starvation, stale harness readiness, or an artifact of repeatedly replacing the
terminal rather than the frozen Ratox framing.

## Decision

Add `sync-content-ratox-post-bulk-admission` as a separate source-linked Sandwurm gate. It retains one
Agent process, one authenticated Tox epoch, the deterministic 8 MiB content graph, 4 Mbit/s subscriber
shaping, and the signed `1,2,4,8` lane sequence. Immediately before cap 8 it requires three stable
authenticated terminal-readiness observations. After cap-8 content reaches reliable `complete`, it
performs no further session polling before launching a new local controller.

Extend `ratox-terminal-probe.py` with optional admission evidence. The probe records one monotonic
origin, local socket connection, canonical OPEN send, canonical OPENED receipt, authenticated carrier
and epoch, fresh session/incarnation/generation/sequence truth, capture digest, and sample count. The
gate requires:

- OPEN sent within 1 second of the content-completion origin;
- OPENED within 5 seconds of OPEN and 6 seconds of the origin;
- the exact pre-backlog carrier and online epoch after OPENED;
- fresh generation and input/output positions at one; and
- 40 exact echo/render/ACK samples under that one new session.

The guest receipt commits the readiness, capture, and admission digests. The compact exporter retains
all three, and the standalone verifier reconstructs timestamps, sequence positions, session hash,
capture hash, carrier, epoch, and receipt joins.

## Consequences

Direct UDP and forced TCP pass the unchanged bounds. Fresh Ratox admission after this reliable cap-8
backlog is therefore qualified on the controlled two-VM construction topology. The rejected early
multi-session attempt does not justify a framing change: it mixed repeated session replacement with
phase transitions and did not retain exact OPEN timing.

This does not prove admission during an unfinished transfer, arbitrary queue depth, repeated OPEN
distribution, public-network behavior, or physical-host latency. It does not select a default content
lane count. Counterbalanced lane/load repetition and any pacing/reservation experiment remain
separate gates, and Ratox v1 framing remains frozen.
