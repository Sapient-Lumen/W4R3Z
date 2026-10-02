# ADR 0175: Qualify loss before cancellation and terminal recovery

Status: accepted for one loss→reassignment→replacement-progress→cancellation order over direct UDP
and forced TCP, 2026-08-25.

## Context

ADR 0169 proved convergence after a live auxiliary loss. ADR 0172 proved local cancellation on a
healthy auxiliary route, and ADR 0174 proved four concurrent healthy-route withdrawals. None proved
what happens when an affected pull is cancelled after it has been fenced and reassigned.

The qualification recovery seam also required an affected auxiliary pull to reach `complete` before
restarting its deliberately stopped worker. A correctly cancelled reassigned pull could therefore
release all work yet leave the stopped qualification worker unrecovered. That was an incomplete test
state machine rather than authority to introduce automatic production restarts.

## Decision

Add `sync-tree-route-loss-cancel`. It uses the existing two-bulk-route signed topology, adaptive
selection, 4,194,601-byte artifact, 4 Mbit shaped client TAP, and exact
`--qualify-route-stop-after-bytes 65536` fault. The test may cancel only after all of the following
are simultaneously visible:

- the qualification fault fired after at least 65,536 artifact bytes;
- exactly one carrier loss and one reassignment occurred;
- the job names a carrier distinct from the stopped canonical first bulk route; and
- that replacement carrier owns an active receive with positive position below the object size.

The ordinary cancellation must reach terminal `cancelled` in at most 5,000 ms, retain the
replacement carrier and worker, add no reassignment, release route work two-to-zero, and leave no
accepted HEAD, activation, incoming transfer, or staging. The stopped identity must then spend one
restart-budget unit, return with a fresh incarnation, authenticate, and restore two ready bulk routes
before the existing protected Ratox probe.

The qualification recovery predicate is broadened from an auxiliary `complete` pull to an auxiliary
`complete` or `cancelled` pull. The injected fault, one reassignment, stale-terminal observation,
stopped bulk worker, and coordinator restart budget remain mandatory. Failed and nonterminal pulls
remain ineligible.

Direct UDP `pair._0jwjfe6` and forced TCP `pair.o0ozmdw1` pass raw and compact verification against
one exact binary. Both cancellation tails are 80 ms; their fault positions are 116,535 and 174,117
bytes. Both reject two stale terminals, restore both routes, and complete 40 protected Ratox samples
below 250 ms.

## Consequences

- A cancellation after mandatory reassignment is a terminal local withdrawal, not a request to
  migrate again or accept partial revision state.
- The replacement carrier identity remains stable across the cancellation effect.
- Cancellation no longer strands the explicit qualification worker recovery state machine.
- This does not enable automatic production restart or claim arbitrary race resolution.
- The opposite order, simultaneous loss/cancel, randomized startup/fault timing, repeated budget
  exhaustion, common-link QoS, larger-object sharing, and relay diversity remain open.

## Verification

The guest, host runner, strict verifier, and compact exporter recognize one exact scenario. The
verifier requires both roles to agree on cancellation fields, binds client-only loss evidence to the
manifest and two-role ready inventory, cross-checks replacement/final/stopped carrier order, and
rejects a mutated old-carrier cancellation claim in its self-test. Raw roots were verified, exported,
and reverified before deletion; both compact proofs reverified afterward.
