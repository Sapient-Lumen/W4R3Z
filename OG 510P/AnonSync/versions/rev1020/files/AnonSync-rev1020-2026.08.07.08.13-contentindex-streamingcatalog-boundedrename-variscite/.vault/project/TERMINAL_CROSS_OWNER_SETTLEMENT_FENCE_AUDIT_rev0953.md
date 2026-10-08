# Terminal cross-owner settlement fence audit — rev0953

## Decision

A completed local scan and remote inspection sweep are not enough to declare one
`sync-once` cycle settled unless the scheduling publication is bound to the same
catalog and replica-visible state that the pass actually inspected. Rev0953 adds
a short writer-serialized terminal fence across the replica and catalog owners,
then requires the final process cutpoint to reproduce the pass's published
remote fairness cursor as well as its catalog and visible-state digests.

This is an exact-observation fence. It is not a distributed transaction and does
not make filesystem, payload-store, replica, and catalog effects atomic together.

## Defect corrected

The rev0952 sweep basis authenticated the catalog and replica visible-state
digests observed before remote rooted inspection. Effects were applied before
catalog scheduling progress, and catalog progress used exact old-state checks.
That prevented stale publication inside the catalog database, but one replica
writer could still advance visible state after the pass's replica snapshot and
before the catalog progress transaction. A sweep could then be published as
complete against an older remote projection.

The first rev0953 terminal fence closed that causal race by re-proving the
replica-visible digest under a retained replica `BEGIN IMMEDIATE` guard while the
catalog owner atomically re-proved its catalog, authenticated local-scan journal,
and remote-work head. A subsequent audit found one remaining classification
hole: after the pass returned, a second catalog process could move only the
durable remote fairness cursor before `sync-once` captured its final cutpoint.
Catalog content and replica-visible digests could remain equal, so a predicate
that compared only those digests could describe a different scheduling cutpoint
as settled.

The final predicate also requires
`pass.remote_apply_resume_after_path == cutpoint.remote_apply_resume_after_path`.
A scheduling-only movement now forces another cycle rather than being hidden
behind an otherwise equal content observation.

## Fence sequence

The terminal path is deliberately ordered:

1. complete every selected rooted apply owner; an exception withholds scheduling
   progress and settlement authority;
2. take a complete terminal catalog snapshot and derive a compact exact catalog
   head from it;
3. acquire `SyncReplicaSqliteProjectionGuard` with `BEGIN IMMEDIATE`, restore the
   complete replica state, and require its visible-state digest to equal the
   pass's pre-attested digest;
4. while that replica writer guard remains live, begin an immediate catalog
   transaction and exactly compare folder/root identity, catalog generation and
   digest, local-scan epoch/count/bytes/cursor/chain, and the full prior
   remote-work singleton;
5. publish the wanted remote cursor/sweep state only if every comparison matches,
   reload it exactly, and commit the catalog transaction;
6. commit the read-only replica guard; and
7. expose the exact terminal catalog digest, terminal visible-state digest, and
   published remote cursor in the pass report.

The expensive complete catalog and replica restorations do not occur while both
database writer slots are held. The overlap contains only compact catalog-head
reproof, one bounded singleton update/reload, and commit. All code paths acquire
replica before catalog, avoiding a new lock-order inversion in this composition.

## Miss and crash behavior

A replica digest mismatch or any catalog/scan/progress mismatch returns no
terminal publication. The pass reports `authority_cutpoint_changed`, clears its
completion claim, restores the previously durable cursor in diagnostics, and
leaves the next cycle to recompute work. Rooted effects that already completed
remain safe and idempotent; scheduling metadata is never promoted into content
authority.

The two SQLite databases are not committed atomically. The catalog scheduling
row can durably commit before the read-only replica guard is released. At that
moment the guard still prevents a competing replica writer, so the publication
was authorized by one real cross-owner observation. A later process failure may
cause conservative replay, but the cursor/sweep row cannot authorize a file,
payload, tombstone, predecessor, or visible replica operation by itself.

A process can move scheduling state after the guard is released and before the
outer `sync-once` final snapshot. The new exact cursor comparison detects that
movement. Other replica changes that do not alter visible state—such as eligible
outbox or clock bookkeeping—are deliberately outside this settlement fence.

## Idle path

The speculative idle path uses the same terminal publication helper. It first
re-proves the ordinary catalog, scan, remote-progress, payload, rooted namespace,
and replica observations needed by the idle proof. It can report idle settlement
only after the same replica-then-catalog writer fence succeeds. A retained partial
sweep, an over-budget projection, or any changed head bypasses the optimization
and returns to the ordinary bounded pass.

## Tests and structural checks

Runtime coverage includes:

- acquisition and rejection of the complete visible-projection guard, including
  empty/tombstone projections and unrelated non-visible state;
- catalog mutation, scan-journal movement, remote-progress movement, and replica
  visible-state movement between observation and terminal publication;
- successful terminal publication and exact pass diagnostics;
- `authority_cutpoint_changed` refusal without false sweep completion;
- matching and mismatching terminal catalog and visible-state digests; and
- the scheduling-only remote cursor mismatch added by the final audit.

The source audit binds guard-before-catalog ordering, exact old-head comparison,
publication after effects, terminal diagnostics, the centralized settlement
predicate, and the durable cursor equality. It is a lexical regression tripwire,
not a model checker or a proof against a hostile kernel, corrupt SQLite library,
or non-cooperating filesystem writer.

## Remaining boundary

A clean `sync-once` result is still an asynchronous convergence cutpoint, not a
snapshot of every external resource. Files may change after rooted observation;
payload and destination namespaces have their own descriptor and hash proofs;
watchers are acceleration only; and the two databases remain separate durable
owners. The product still needs an incremental catalog/remote-work/payload index,
rotating byte scrub, retention/restore/garbage-collection policy, and real
multi-process soak/fault injection around this lock order.
