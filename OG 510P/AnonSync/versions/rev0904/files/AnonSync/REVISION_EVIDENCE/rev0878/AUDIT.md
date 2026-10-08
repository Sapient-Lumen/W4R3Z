# rev0878 compact audit record

## Load-bearing correction

The merged effect-terminal path originally checked causal projection in a loose
snapshot, released it, and then performed filesystem publication. A second SQLite
owner could supersede the operation in that check/use gap. Rev0878 adds a
nontransferable `SyncReplicaSqliteProjectionGuard` backed by `BEGIN IMMEDIATE`. It
requires the exact receipt generation/digest and sole active File primary, then
retains writer serialization through independently idempotent effect
materialization and terminal receipt construction.

This is not a cross-database/filesystem transaction. Correctness comes from one
stable causal authorization cutpoint plus immutable create-new publication, exact
file/directory reconciliation, and retry-safe receiver evidence.

## Additional correction and refactor

The causal owner now checks the selected operation's wire model, exact File kind,
and committed payload size before lease mutation. Declaratively unsendable work
can no longer consume repeated claim/expiry cycles. Receipt disposition was
refactored to an explicit optional total state so a future invalid enum path fails
closed rather than reaching uninitialized authority.

The file-delivery source audit is explicitly lexical hygiene, not semantic proof.
Its 23 checks complement the 41-check causal-owner audit, 18-check live-channel
audit, runtime concurrency/restart tests, compiler diagnostics, sanitizers, and
complete CTest registry.

## Remaining severe boundaries

The shipped `anonsync_core` executable still does not use the new owners. The
effect root is persisted as normalized path text rather than a stable directory
capability. Staging-before-admission is bounded but lacks per-peer fairness,
expiry, and reclaim authority. The first effect is immutable create-new only;
update, rename, tombstone, compaction, signed receipts, membership lifecycle, and
a defensible anonymity model remain open.
