# ADR 0195: Bind the configured target to authenticated Tor control

Status: accepted and publicly qualified, 2026-08-27.

## Context

ADR 0194 deliberately makes `route-target-health` ignorant of Tor control credentials. A successful
SOCKS CONNECT is useful route evidence, but by itself cannot identify the proxy implementation,
circuit, or process that carried the stream. The operator gate already authenticates a private Tor
control socket and inspects Linux process-owned sockets, so it is the correct place to join these
facts without expanding the ordinary Agent's secret boundary.

Tor STREAM events expose `SOURCE_ADDR` on `NEW`, not necessarily on `SUCCEEDED`. Current Tor can
attach ordinary exit traffic to either a legacy `GENERAL` circuit or a linked Conflux application
circuit. Treating only `GENERAL` as valid rejects Tor's modern multipath implementation; accepting
every purpose would admit internal, onion-service, testing, or controller circuits.

## Decision

For both initial and recovered phases, the opt-in operator-Tor gate must:

1. snapshot the Agent's existing source ports to the exact loopback SOCKS endpoint;
2. authenticate Tor control and subscribe to extended STREAM events;
3. invoke `route-target-health` with no caller-supplied target;
4. require one successful complete CONNECT to configured numeric TCP relay zero;
5. capture one new Agent-owned SOCKS source from `NEW`, then correlate the same stream ID through
   `SUCCEEDED` to the exact configured target and circuit ID;
6. require that circuit to be built, contain at least three hops, and have exactly one purpose in
   `{GENERAL, CONFLUX_LINKED}`; and
7. retain only content-free/digested evidence in the canonical receipt: target source and result,
   RTT, SOCKS reply, circuit purpose/hop count/path digest, stream-ID digest, authenticated-control
   truth, and new-source-port truth.

`CONFLUX_UNLINKED` is not accepted: a successful application stream must name a completed linked
bundle or a general circuit. The producer and independent verifier share the allowed vocabulary but
implement separate strict schema checks. Failure roots retain private raw stream/circuit projections
for diagnosis; successful roots are removed.

This evidence remains auxiliary. It cannot relabel c-toxcore's carrier, advance an online/session
epoch, detach or resume Ratox, prove a Tox handshake, or assert anonymity.

## Consequences

- The ordinary Agent still receives no Tor control credential and remains usable with any strict
  numeric SOCKS5 provider.
- One configured-target observation can now be attributed to the exact Tor process, lifecycle,
  configured relay, and a qualifying circuit without exposing relay/circuit paths in retained
  evidence.
- The circuit-purpose vocabulary explicitly follows Tor's general application route, including its
  integrated Conflux traffic splitting, while failing closed on unrelated purposes and unknown
  classifications.
- This closes the single-host/single-relay configured-target circuit-binding row. It does not close
  multi-relay/time sampling or two-IoTox application behavior under actual Tor impairment.

## Qualification

Clean commit `715e1c823b4dabaf7b7a7a9b967a6a8c4b1420a0` passed the public gate against configured relay
`144.217.167.73:33445` through Tor 0.4.8.11. Initial and recovered one-shot target observations
completed in 266,385 us and 237,701 us with SOCKS reply 0. Authenticated control correlated each to
a new Agent source and a distinct built three-hop `CONFLUX_LINKED` circuit. After Tor termination,
the same operation failed at proxy connect in 67 us while carrier truth still read TCP; local route
loss appeared in 35 ms, authoritative offline in 74,602 ms, and exact-endpoint recovery in 3,913 ms
after a 30,290 ms held outage.

The independent verifier accepts the canonical receipt at
`artifacts/rev0045/tox-operator-tor-smoke.json`. The evidence scope and exact nonclaims remain those
of ADR 0191 and `docs/evidence/2026-08-27-operator-tor-public-route.md`.
