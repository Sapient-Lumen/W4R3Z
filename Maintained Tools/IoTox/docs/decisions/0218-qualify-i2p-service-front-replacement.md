# ADR 0218: Qualify I2P service-front replacement

Status: accepted construction evidence, 2026-08-28.

## Context

ADR 0217 proved recovery when the client i2pd router and its SAM listener disappear. That did not
exercise the opposite boundary: both routers and the client adapter can remain healthy while the
server-side persistent Destinations vanish. A production service manager must be able to recreate
those fronts without changing their identities, and IoTox must derive interruption and recovery
from c-toxcore/application truth rather than from router or SAM availability.

The construction also needed content-free evidence that the two i2pd processes, rather than the
bridge adapter or guest, own actual public-network sockets. A listening SAM endpoint alone is not
evidence that an I2P router is attached to the public network.

## Decision

- Add the Sandwurm `i2p-service-restart` scenario to `tox-i2p-construction`. It keeps the same two
  source-pinned i2pd routers, strict client adapter, three exact-target egress shims, route-scoped
  reusable guest identities, and three address-preserving public Tox records.
- Require both guests to reach a transcript-confirmed session before fault injection. Stop all
  three server-side SAM forward processes while leaving both routers, both SAM listeners, the
  bridge adapter listener, and all egress shims alive.
- Require both guests to report c-toxcore-authoritative offline before recovery. Router/SAM/listener
  readiness is not allowed to stand in for transport or application state.
- Restart three distinct forward processes from the exact same mode-0600 Destination-key files.
  Every returned canonical b32 Destination must equal its original value, every PID must change,
  and neither router nor the adapter may be restarted.
- Require both guests to advance from authenticated online epoch 1 to epoch 2 and receive fresh
  text from the other guest before either can finish. The adapter remains on SAM generation one;
  this gate must not be accidentally satisfied by the router-restart path.
- Attribute each initial router to its exact PID/start tick, ownership of its loopback SAM listener,
  and at least one established public TCP socket. Retain only the count and a domain-separated hash
  of the public remote set; raw public remote endpoints are not exported.
- Extend compact evidence with the three replacement-front audits. Initial fronts must record
  `created -> ready`; replacements must record `loaded -> ready`. The compact verifier requires the
  exact seven-audit inventory and rejects undeclared files.

Accepted compact proof `pair.6rrdsdc_` runs source commit `d390272`, replaces front PIDs 1843085,
1843288, and 1843300 with 1856071, 1856111, and 1856147, and preserves all three Destination keys.
The server and client router PIDs remain 1843043 and 1843044; their attributed public TCP remote-set
counts are 33 and 32. The front-replacement interval is 68.615 seconds. Both guests observe offline,
advance online epoch 1 to 2, and exchange fresh bilateral text.

The adapter records one continuously ready SAM generation and 19 admitted exact-Destination
connections with all three commitments represented before and after recovery. No denial or unknown
Destination appears. Both TAP captures remain TCP-only to `10.0.0.1:39053`, with zero UDP, direct
bootstrap, direct peer, or alternate IPv4 destination traffic. Raw and compact strict verification
both pass.

## Consequences

- Server-front process replacement, stable private Destination reuse, authoritative application
  recovery, initial exact-router public-socket attribution, and no-fallback containment are now
  closed for this bounded laboratory construction.
- A ready router, SAM listener, or client adapter does not imply that a persistent server
  Destination exists. Deployment health must preserve these as separate layers.
- Stable service identity resides in the owner-private Destination-key file, not in a forward
  process lifetime. The compact proof exports only commitments and key lifecycle outcomes.
- Production `tox/i2p` remains reserved. A private route-member proof carrying an exact Ratox or
  sync payload, repetition over later record/time windows, independent router administration,
  product policy, and anonymity remain open.

ADR 0219 later closes the first item only for one exact 131,369-byte sync tree with zero
reassignment. Its rejected larger-object attempts make auxiliary chunk/range framing and signed
privacy-class failover policy explicit prerequisites rather than widening this ADR's route claim.

See `docs/evidence/2026-08-28-sandwurm-i2p-service-front-recovery.md` and
`docs/i2p-route-construction.md`.
