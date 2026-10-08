# Rev0957 implementation and adjacent audit

## Mission checkpoint

The reviewed spine remains the shipping one:

`anonsync_sync` → retained peer service → folder process → folder scan owner →
SQLite catalog/replica owners → rooted payload store and shared-folder effects →
authenticated direct/Tor/I2P sessions.

No parallel daemon, recovery engine, catalog, or synchronization algorithm was
introduced. The change removes repeated work from the exact path that keeps the
service alive after payload corruption.

## Primary finding: a complete proof was discarded

`payload_integrity_reproof_step_or_throw()` in rev0956 obtained a complete
`SyncReplicaFilePayloadStoreSnapshot`, discarded the value, and then invoked
ordinary convergence. The convergence owner could immediately call
`snapshot_or_throw()` again. This was not a correctness failure, but it was a
large-tree recovery tax and obscured whether current-byte reproof was actually
reused.

## Implemented correction

- `SyncReplicaFolderProcessOwner` and `SyncReplicaFolderScanOwner` accept a
  move-only snapshot handoff.
- Both ordinary and handoff entry points call one
  `run_convergence_pass_impl_or_throw()` body.
- The peer service moves its just-completed reproof into that body.
- The body validates exact origin before any catalog/replica/rooted shared-tree
  work.
- Existing snapshot epoch/thread/root/path checks remain active.
- All convergence-owned complete snapshots pass through one accounting lambda.
- Service accounting records handoffs, new snapshot observations, and fallback
  mutation full scans separately.

## Authority audit: same durable store is not same owner

A second store handle may open the same root with the same folder identity,
attestation, and limits but has an independent process verification cache and
integrity epoch. Accepting its snapshot could bypass the retained owner's
fail-closed witness. The exact-origin fence therefore compares the shared cache
object by identity in addition to durable structural fields and invokes the
snapshot's ordinary current-state validator.

The candidate snapshot keeps its cache alive, preventing address reuse by a
later cache during that candidate's lifetime. Both root authorities are re-
verified. Rejection occurs before catalog or replica access.

## Mechanical regression

The focused folder-owner test:

- takes the complete handoff snapshot;
- acquires an exclusive payload mutation batch;
- proves a direct new snapshot is lease-busy;
- completes idle convergence from the moved snapshot while exclusion remains;
- requires one handoff, zero new snapshot observations, zero mutation batches,
  and zero mutation full scans;
- opens a foreign same-root store owner and proves rejection; and
- compares catalog and replica snapshots before and after rejection.

This is a stronger proof than checking only a report field: a hidden second
snapshot would mechanically fail.

## Adjacent defect: stale durable-witness attribution

Rev0956 merged repeated faults by expected digest and ORed
`failure_persisted`. If corrupt bytes changed, durable publication for the old
observed digest could be shown for the new one. Rev0957 extracts exact-pair merge
semantics into a small testable header:

- exact pair repetition may accumulate persistence;
- changed observed digest resets persistence to the new exception's result;
- changed expected digest starts a new alarm;
- detection and observed-change counters saturate; and
- status exposes observed byte-image transitions.

`anonsync.peer-service.status.v4` marks the semantic change.

The same review removed a smaller but repeated waste: the initial merger copied
both digest strings by value and cloned the active evidence before discovering
that an alarm was an exact repetition. The final helper accepts string views,
merges directly into retained evidence, performs no digest-storage replacement
for an exact pair, and constructs transition strings before mutating counters or
the pair-scoped persistence flag. The focused test uses non-SSO strings and
proves their backing pointers remain stable across an exact repeat.

## Adjacent asynchronous-state audit

Native I2P ingress publication can change on its capability-free worker during a
long integrity reproof. The owner now refreshes that worker while faulted and at
the recovery cutpoint before clearing the alarm. The refresh cannot preempt the
reproof state machine with an ingress event, but readiness is no longer restored
from a stale pre-fault worker snapshot.

## Structural-audit refactor

Moving the implementation behind a thin ordinary wrapper initially caused eight
older lexical checks to inspect only that wrapper. The audit was corrected to
inspect `run_convergence_pass_impl_or_throw()` for all historical convergence
invariants, while separate rev0957 checks inspect both wrappers and their shared
delegation. This prevents the refactor itself from making old checks vacuous.

The audit review also found one stale oracle in its remote-apply freshness
check: it still searched for the obsolete inserted-payload counter even though
an `AlreadyPresent` mutation attempt is sufficient to invalidate the frozen
payload cutpoint. The check now binds to `payload_mutation_put_count`, matching
the shipping algorithm and its same-pass regression. A separate check binds the
exact-pair evidence merger to direct retained-state operation without repeated
digest cloning.

Final structural result: 127/127 checks passed on the sealed active source.
The audit explicitly remains lexical hygiene, not semantic proof.

## Nonclaims

The handoff is process-local and immediate. It is not a durable remote index,
sequence protocol, restart capability, retention pin, or garbage-collection
root. It does not remove rooted shared-folder work or path-local mutation costs.
Status counters are not throughput or latency guarantees. Product gaps remain:
rename identity, directories, conflict/restore UX, bounded history and GC,
selective sync, many-share supervision, cross-platform behavior, and a measured
first Resilio uninstall workload.
