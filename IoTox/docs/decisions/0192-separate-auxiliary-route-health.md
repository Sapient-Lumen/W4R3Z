# ADR 0192: Separate auxiliary route health from carrier truth

Status: accepted observational surface, 2026-08-27.

## Context

The rev0045 source-linked SOCKS and operator-Tor gates measured roughly 78 seconds between local
proxy death and c-toxcore's authoritative `offline` callback. That state is correct provider truth,
but it is too coarse to be the only future recovery signal for a latency-sensitive Ratox successor
or an Eternal/Mosh-style terminal.

Changing the carrier label early would be false, while treating a reachable SOCKS listener as proof
of a working upstream route would be equally false. Sending a diagnostic packet must also not
manufacture a new application epoch.

## Decision

Add local-control v1.36 operation 39 and the owner CLI:

```text
iotox route-health [FRIEND]
```

The daemon returns one content-free observation with three separate layers:

1. `carrier-connection` is copied exactly from c-toxcore's `offline|tcp|udp` self-connection state.
2. For `Tox/Tor`, `local-boundary` opens and closes one numeric nonblocking TCP connection to the
   configured SOCKS endpoint with a 250 ms bound. It sends no SOCKS request. `Tox/native` reports
   `not-applicable`.
3. When a friend is supplied, `application` uses the existing transcript-confirmed lossless custom
   packet echo and reports responsive, timed-out/unresponsive, or unavailable plus only a bounded
   error-code number.

The report includes no proxy address, friend selector, Tox key, nonce, packet body, or circuit
identity. `upstream=carrier-reported-online` means only that c-toxcore currently reports a carrier.
When it reports offline, a refused, timed-out, or unreachable local connection becomes
`blocked-by-local-boundary`; a reachable boundary, internal probe failure, or native route remains
`unresolved`. Local reachability is never upstream success.

The operation is observational. It does not write the runtime snapshot, relabel the carrier, call a
session online/offline transition, reset a transcript, or advance an online epoch. Application
failure is returned as a successful diagnostic report rather than changing session state.

## Consequences

- An operator can distinguish a dead local Tor/SOCKS listener from the provider's slower carrier
  callback without falsifying either fact.
- A confirmed peer heartbeat gives a faster application-path observation suitable for later
  recovery policy, but it is not itself a Ratox terminal heartbeat or permission to reconnect.
- A listening proxy may still have no circuit, no upstream connectivity, or a censored destination.
  SOCKS handshake/target and Tor-control measurements remain a separate M8 gate.
- On-demand observation does not itself define a persistent monitor, hysteresis, failure threshold,
  session migration policy, or terminal resumption policy. ADR 0193 later adds process-local
  observation hysteresis and warning-only terminal heartbeat semantics without changing this rule.

## Qualification

The owned network test opens a real loopback TCP listener, observes `reachable`, closes it, observes
`refused`, and proves that offline-plus-reachable remains `unresolved`. Agent integration traverses
the control operation and a confirmed lossless echo, then requires the complete rendered protocol
session to remain byte-identical. The separate whole-binary lifecycle fixture runs both
`route-health` CLI forms against the live mock-backed daemon and confirms a responsive peer.

Clean commit `715e1c823b4dabaf7b7a7a9b967a6a8c4b1420a0` repeated the actual operator-Tor gate.
Ordered observations were `tcp/reachable`, `tcp/refused` 35 ms after Tor loss,
`offline/refused/blocked-by-local-boundary` after 74.602 seconds, and recovered `tcp/reachable`.
The independent receipt verifier requires local refusal to precede authoritative offline while
retaining the two different carrier labels. This measures the observation seam, not a persistent
failure threshold or terminal recovery policy.

ADR 0193 qualifies the next construction layer: strict report parsing, bounded independent
process-local latches, and one exact Ratox heartbeat identity per attachment. It does not reinterpret
the retained operator-Tor evidence or turn either signal into automatic recovery authority.
