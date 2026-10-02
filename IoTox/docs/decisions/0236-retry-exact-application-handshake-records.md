# ADR 0236: Retry exact application-handshake records

Status: accepted through the ADR 0235 direct-UDP and forced-TCP gates, 2026-08-29.

## Context

Tox accepting a lossless packet into its local send queue is not an end-to-end application
acknowledgement. During asymmetric auxiliary-worker recovery, one process can receive its Tox
friend-online event and enqueue HELLO while the other process still classifies that friendship in
the preceding offline application epoch. The receiver correctly rejects the early frame. Before
this decision, the sender recorded successful enqueue as `hello_sent` and never transmitted that
record again. The same race could strand CAPABILITIES confirmation.

The fourth three-loss range calibration, diagnostic root `pair.ge_y8h28`, made this visible after
two successful carrier recoveries. Both publisher bulk transports were running at online epoch two,
but both remained `application-ready=0`, `local-binding-sent=0`, and
`remote-binding-authenticated=0`. The content-free publisher watchdog did not change while the
subscriber's sixth attempt remained at byte zero. Another range request could not repair an
application session that had never reconfirmed.

## Decision

- While an auxiliary Tox friendship is connected but its IoTox transcript is incomplete, retry the
  canonical HELLO once per second. Once both compatible HELLOs exist, retry canonical CAPABILITIES
  at the same cadence until the application session is confirmed.
- Rebuild each retry through `PeerSessionRegistry`. It reuses the first message identifier, nonce,
  transcript, correlation identifier, and canonical payload for that online epoch. No new record,
  capability, framing version, or authority fact is introduced.
- Stop retrying immediately when the application session becomes ready or enters an incompatible,
  malformed, or conflicting terminal state. Offline peers receive no attempts.
- Expose HELLO/confirmation sent, received, and attempt counters in the content-free auxiliary route
  projection so a transport-ready/application-stalled route is diagnosable without packet content.
- Exercise the edge in the owned mock provider by silently discarding the first locally accepted
  HELLO and confirmation. The worker must become application-ready through bounded retransmission;
  both attempt counters must prove more than one attempt without a hot loop.

## Consequences

An auxiliary route can now recover from the gap between local toxcore enqueue acceptance and the
peer's application-epoch admission. Frozen framing and transcript conflict detection remain the
idempotence boundary; retransmission does not authorize a peer, authenticate a route binding, or
replay later application effects.

This deterministic result is not by itself the three-loss range acceptance claim. ADR 0235's later
direct-UDP `pair.3iufekzy` and forced-TCP `pair.zleebk2k` proofs exercise the recovered transcript
through three carrier deaths. This decision does not claim delivery through an indefinitely
disconnected peer, alter Tox's reliability contract, or add timeout-based fallback.
