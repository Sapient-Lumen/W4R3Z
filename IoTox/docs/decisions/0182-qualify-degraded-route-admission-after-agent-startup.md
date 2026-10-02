# ADR 0182: Qualify degraded-route admission after Agent startup

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0176 proved that either exact auxiliary identity can become the sole ready route after a clean
same-state Agent restart. ADR 0181 proved that genuinely new work can be admitted after an active
route loss and reassignment. Neither result joined startup state to live admission: the scheduler
could still wait for the complete route set before accepting work, or move healthy work when a
delayed route joined.

The laboratory has one physical computer and two Sandwurm guests. Its existing default-off
readiness-order seam can deterministically hold one authenticated auxiliary route without changing
the signed route set, framing, production defaults, or transport authority. That is sufficient to
qualify controlled degraded readiness after an Agent restart, but it is not equivalent to a route
being physically absent at host boot.

## Decision

Add `sync-tree-route-startup-admission`. Both peers first establish the ordinary signed base tree
and two ready bulk routes. The subscriber then cleanly restarts the same Agent identity under
adaptive selection, naming the first exact auxiliary worker and holding the other for 20,000 ms.
Acceptance requires confirmed application authority and exactly that one bulk route ready for ten
consecutive samples.

While the inventory has one ready bulk route, start two independent signed tree pulls. Each tree
contains one 16,777,216-byte payload and produces a 16,777,283-byte artifact plus its manifest, so
both two-object jobs consume four signed work units and remain live through the delayed-route edge
under the laboratory's 4 Mbit/s client shaping. Both initial selections must name the sole ready
carrier. When the second route joins, both jobs must still be live and must retain their original
carrier. Acceptance then requires both complete-object commits, two explicit exact-HEAD
activations, zero reassignment, exactly two adaptive selections, and signed route work four-to-zero.

Retain a process-incarnation-fenced client resource interval and run 40 protected Ratox probes only
after convergence. Strict raw and compact verification bind the scenario fields, resource digest,
carrier shape, both guest receipts, connection class, and exact binary.

## Consequences

- The scheduler no longer needs the complete signed route set to be ready before admitting valid
  work; one authenticated eligible member is sufficient within its signed capacity.
- A later healthy route affects only future adaptive decisions. Existing healthy jobs do not move
  merely because a lower-utilization candidate appears.
- Large-object work now has one topology/liveness observation on both native carrier classes, but
  the single-cell durations are not throughput benchmarks or fairness distributions.
- Sync framing, authority, signed route membership, HEAD-last acceptance, manual activation, and
  production defaults are unchanged.
- This does not prove physical route absence at machine boot, operating-system or full-guest cold
  boot, a route fault during daemon initialization, randomized startup delays, more than two bulk
  routes, independent relay paths, common-link QoS, or production automatic recovery.

## Qualification

Binary `db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`
passes strict raw and compact verification in both two-Sandwurm-guest cells.

- Direct UDP `pair.46f6td4j`: 103,748 ms, ready bulk 1→2, ten stable samples, two live jobs and two
  preserved carriers at join, two activations, work 4→0, and protected Ratox p50/p95/max
  14.875/22.673/23.540 ms.
- Forced TCP `pair.2gvkqs6b`: 126,919 ms with the same exact logical counts and protected Ratox
  p50/p95/max 92.317/102.257/129.184 ms.

Each compact proof allocates 249,856 bytes and excludes guest disks, private identities, bootstrap
secrets, payload content, and mutable runtime state. Exact proof hashes and the rejected fixture
observation live in
`evidence/2026-08-26-sandwurm-sync-route-startup-admission.md`.
