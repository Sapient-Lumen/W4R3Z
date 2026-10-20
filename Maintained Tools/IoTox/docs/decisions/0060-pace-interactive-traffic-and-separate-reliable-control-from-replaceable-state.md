# ADR 0060: Pace interactive traffic and separate reliable control from replaceable state

Status: accepted
Date: 2026-08-15
Supersedes: the unconditional custom-lossless carrier preference in ADR 0059

## Context

ADR 0059 selected custom lossless from an uncontrolled zero-loss comparison. The controlled
namespace/netem matrix added delay, loss, duplication, reorder, rate, queue pressure, idle/bulk
states, direct UDP, and forced TCP. A 64-packet burst at 2 ms spacing also separated local toxcore
admission rejection from a post-admission deadline miss.

Under delayed/adverse UDP, lossless retained order but developed hundreds of milliseconds of queue
tail and local rejection. Lossy returned survivors faster but lost and reordered them. Under
adversity TCP plus bulk, lossless admitted only 3/64 and lossy admitted 34/64; every admitted reply
was ordered because both APIs shared the TCP relay stream.

## Decision

Do not define one universal Ratox carrier.

- Reliable control, attachment, input commitment/ACK, resize, close, exit, and resynchronization
  use custom lossless and remain sparse.
- Ordered terminal byte input remains lossless because at-most-once delivery cannot be reconstructed
  from an unacknowledged lossy datagram.
- A future custom-lossy output lane is permitted only for explicitly replaceable state carrying a
  sequence, snapshot identity, delta base, and a lossless resynchronization path.
- Every interactive sender must pace and coalesce. A toxcore send rejection is congestion evidence,
  not a packet that may be silently treated as sent. The initial 5 ms coalescing target remains a
  hypothesis to qualify, not a guaranteed safe emission interval.
- TCP relay mode assumes one ordered head-of-line domain regardless of custom API. Lossy framing is
  not latency isolation there. A dedicated authenticated Tox route may be evaluated after the PTY
  and 1/8/16/32/64 coexistence gate, but is not yet product behavior.
- Human Tox text remains chat/compatibility traffic and never terminal framing.

The unadvertised echo and burst operations remain local research instruments. They do not add an
IoTox protocol feature or terminal authority.

## Consequences

The first terminal protocol can be conservative and correct without foreclosing replaceable screen
state later. Pacing becomes part of correctness because the owner queue can be healthy while
toxcore rejects admission beneath it. Lossless protects semantics but cannot be allowed to grow an
unbounded reliable prefix. Lossy output must tolerate omission/reorder and cannot carry authority or
irreversible input.

Forced TCP cannot meet a low-latency budget merely by switching packet APIs. Route isolation,
smaller/coalesced state, and explicit degraded-mode telemetry are the available levers.

This ADR does not advertise a PTY, remote shell, screen-state protocol, or route bond. Those still
require versioned framing, authority, lifecycle, failure, fuzz, and genuine two-host gates.
