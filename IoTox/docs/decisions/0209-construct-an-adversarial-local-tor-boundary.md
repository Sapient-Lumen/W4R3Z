# ADR 0209: Construct an adversarial local Tor boundary

Status: accepted bounded live route qualification, 2026-08-28.

## Context

ADRs 0207/0208 prove that Tor circuit and stream transitions do not determine the Ratox lifecycle.
The next M8 adversarial boundary must test the complementary local deception: a SOCKS listener and
its established TCP streams can remain reachable while upstream application bytes stop. Neither
`route-health`'s local-boundary observation nor a successful SOCKS CONNECT may be promoted into Tox
carrier, heartbeat, PTY, detach, or resume truth.

Changing the existing laboratory forwarder would change the tool digest expected by retained
generic-SOCKS proofs. The adversarial prerequisite therefore must be a distinct tool, leaving the
frozen forwarder and historical proof verification unchanged.

## Decision

Add `tools/run-socks5-adversary.py`, a bounded lab-only numeric SOCKS5-over-SOCKS interposer. It:

- accepts only explicitly allowlisted numeric CONNECT targets and refuses domain address types;
- connects each admitted target through one explicit numeric upstream SOCKS5 endpoint;
- records the client source, requested target, interposer upstream source, and exact upstream SOCKS
  destination in an append-only content-free audit;
- holds established relay bytes while one explicit host-owned file exists, without closing either
  TCP side or the listener, and resumes byte-exact forwarding when that file is removed; and
- has no authentication, DNS, UDP ASSOCIATE, BIND, wildcard target, production daemon, or policy
  integration.

The process test chains the interposer through the unchanged strict forwarder to an echo server. It
proves initial exact bytes, listener reachability during the hold, absence of held-byte delivery,
exact post-hold release, target/source/upstream attribution, audit ordering, and clean counters.

## Consequences

- The adapter process test remains only fault-injector evidence. The distinct live gate
  `ratox-route-actual-tor-adversary` places one interposer in front of each loopback-only Tor SOCKS
  endpoint, binds every audited upstream source port to authenticated Tor STREAM/CIRC evidence and
  process/socket ownership, and retains both TAP captures.
- Accepted raw and compact proof `pair.vx6z0csh` holds the client interposer after positive terminal
  progress. The listener remains reachable and a new exact-target SOCKS CONNECT succeeds, but the
  Ratox heartbeat misses after 2.578 seconds and c-toxcore reaches authoritative offline only after
  27.241 seconds. The device retains the detached PTY.
- Removing only the hold file recovers a higher authenticated epoch and exact generation-two resume.
  Tor, interposer, IoTox, guest, session, incarnation, PTY, and byte identities remain unchanged
  where the protocol requires. No auxiliary observation causes a session transition.
- Local listener reachability and target admission are deliberately operational signals, never
  carrier or session authority. Tor control evidence is attribution, never lifecycle authority.
- Historical forwarder-bound proofs keep their original executable digest and continue to verify.

The evidence and exact nonclaims are retained in
`docs/evidence/2026-08-28-sandwurm-actual-tor-adversarial-boundary.md`.
