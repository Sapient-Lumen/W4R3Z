# ADR 0179: Qualify both shared-arm linearizations

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0178 introduced one observable progress arm edge and accepted two authority-state outcomes for
independently scheduled exact-worker loss and ordinary cancellation. Its equal 500/500 ms cells both
observed cancel-first. The strict verifier modeled loss-first, but a synthetic record cannot prove
that the live Agent actually fences the old attempt, selects one fresh carrier, cancels the
replacement, and recovers route capacity without reviving the terminal pull.

ADR 0175 had already proved a deliberately staged loss→replacement-progress→cancellation sequence.
The missing claim is narrower: can the shared-arm mechanism itself produce and safely classify the
other branch when timing makes loss lead, without a host or test runner waiting for reassignment
before deciding to cancel?

## Decision

Add `sync-tree-route-cancel-race-loss-first` as the required-outcome companion to the ADR 0178 cell.
It uses the same one protected primary, two signed bulk workers, adaptive scheduler, 4 MiB tree,
65,536-byte arm threshold, ordinary local cancellation, route recovery, and protected Ratox probe.
Only the independent deadlines change:

```text
exact-worker stop: 250 ms after arm
ordinary cancel:  1000 ms after arm
required outcome: loss-first
```

The client does not poll for loss, reassignment, or replacement progress before issuing cancellation.
The Agent deadline and client sleep advance independently from the same observed armed state. Strict
acceptance requires exactly one carrier loss and one reassignment, two adaptive selections, a final
terminal carrier distinct from the stopped carrier, zero remaining signed work, no incoming or
staging state, no accepted HEAD or activation, one route recovery, two ready bulk identities, and 40
protected Ratox samples below 250 ms.

The typed cleanup-retry allowance remains available because it belongs to the shared race contract,
but neither accepted loss-first cell needs it: cancellation addresses the live replacement carrier
and succeeds on its first ordinary request.

Direct UDP `pair.5gvh__p1` and forced TCP `pair.rxb2dsge` pass raw and compact verification. Their
cancellation tails are 50 ms and 60 ms. Each reports one loss, one reassignment, two stale terminals,
one recovery, and zero cleanup retries against the same production binary as ADR 0178.

## Consequences

- Both terminal authority linearizations now have genuine two-VM evidence on both native carrier
  classes.
- Loss-first performs one fresh immutable-object assignment and cancellation terminates that exact
  replacement; it does not cancel only the stale worker handle.
- Cancel-first still forbids reassignment and may expose the typed already-fenced cleanup edge.
- The two outcomes use the same product state machine and strict evidence schema. Timing selects the
  branch; neither branch changes authority, HEAD-last ordering, or activation.
- No production option, protocol frame, signed route inventory, capability, or scheduler identity
  changes in this decision. It extends the qualification harness around ADR 0178's existing bounded
  delay seam.
- Four deterministic timing cells are not a randomized distribution. Boundary jitter, startup
  during faults, multiple affected pulls sharing one carrier, common-link QoS, relay diversity, and
  long-running production recovery policy remain open.

## Verification

The guest requires loss-first for the named scenario before writing its receipt. The runner and
offline verifier derive exact expected delays and any required outcome from a closed scenario table,
retain strict zero defaults elsewhere, and bind outcome to reassignment count plus final/stopped
carrier inequality. The verifier self-test now uses the exact 250/1000 ms loss-first shape in addition
to the 500/500 ms cancel-first shape and rejects an inconsistent record.

Both raw cells passed strict verification. Each 241,664-byte compact export then replayed with all
receipt, binary, carrier, cancellation, recovery, protected-Ratox, and compact-file digests bound.
Exact values live in `evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md`.
