# Removable-media local fallback post-detach successor index checkpoint is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, r510 closed denial receipts, r511 closed fresh-authority reissue, r512 closed one-shot consumption, and r513 closed atomic successor-index cutover. r514 closes the next seam: brokers no longer accept whichever successor-index root they happen to read after cutover. They require a typed, monotonic checkpoint that fences readers against rollback, restored old roots, and dual-active snapshots.

See also:
- ADR: `adrs/ADR-0358-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-successor-index-checkpoint-receipt/`
- cutover receipt: `docs/768-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded`
- `sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8`
- `known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation`

A `removable.media.local.post_detach.successor.index.checkpoint.receipt` is required after the r513 successor-index cutover receipt and before successor query/export/rehydration/remote-locator/managed-copy brokers treat the new index root as acceptable. The checkpoint records `successor-index-checkpoint-cutover-root-anchored-and-rollback-denied` and `successor-index-checkpoint-cutover-root-anchored-before-broker-use`. It binds the cutover receipt, cutover marker, successor index snapshot, tombstone root, denial-root, and successor-root digests to monotonic sequence 44, then requires every reader to reject pre-checkpoint roots.

## Evidence object shape

`spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json` is now the generic runtime contract; `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json` preserves the exact r514 canonical digest/id/sequence literals. The runtime schema requires these closed-world sections:

- `contract_binding`: joins the checkpoint to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, r511 fresh-authority receipt, r512 consumption receipt, r513 cutover receipt, and canonical import receipt;
- `cutover_binding`: records the r513 cutover digest, cutover marker, successor-index snapshot, cutover sequence, exact cutover outcome, terminal old-handle state, no rollback, and no raw handle values;
- `checkpoint_state`: records checkpoint sequence 44, prior sequence floor 43, monotonic sequencing, index-root/tombstone-root/denial-root/successor-root digests, append-only log digest, checkpoint marker, anchor mode, and immutability;
- `reader_fence`: requires query, export, rehydration, remote-locator, and managed-copy readers to reject roots below sequence 44 and to reject stale roots, old-handle restorations, or dual-active snapshots;
- `redaction`: keeps raw locators, untrusted filenames, host identity, full text, body text, recipient text, raw receipt payloads, and secret material out of the checkpoint projection;
- `failure_policy`: fails closed on missing cutover evidence, non-monotonic sequence, stale root acceptance, restored old roots, dual-active snapshots, unanchored/mutable checkpoints, missing reader fences, raw locator/filename indexing, full-text indexing, secret material, or offline-erasure overclaim.

## Red corpus

The checkpoint red corpus starts under `spec/examples/invalid/removable-media/post-detach-successor-index-checkpoint-receipt/` with:

- `missing-cutover-receipt.json`
- `checkpoint-sequence-not-monotonic.json`
- `stale-index-root-accepted.json`
- `old-handle-root-restored.json`
- `dual-active-snapshot-accepted.json`
- `unanchored-checkpoint.json`
- `mutable-checkpoint.json`
- `missing-reader-fence.json`
- `raw-locator-included.json`
- `filename-indexed.json`
- `secret-material-present.json`
- `full-text-indexed.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps the r513 cutover from becoming rollbackable index state.

## What this changes in implementation terms

The first launcher/indexer prototype now has eleven separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles stop working;
7. the r510 denial receipt proves stale use was denied after the tombstone;
8. the r511 fresh-authority receipt proves later successor authority came from a fresh lease and policy decision;
9. the r512 consumption receipt proves that fresh authority was applied once to exact successor artifacts;
10. the r513 cutover receipt proves old handles became terminal and exact successors became live;
11. the r514 checkpoint receipt proves readers cannot accept stale or restored index roots after that cutover.

The behavioral change is "post-cutover readers have a minimum acceptable index root," not merely "the cutover receipt says rollback is not allowed." If a broker sees an older index root, a restored old-handle root, or a dual-active snapshot below the checkpoint, it fails closed and emits denial/recovery evidence rather than treating the state as ordinary absence.

## Notes for backend implementers

The checkpoint can initially be local and append-only; it does not require a global transparency service. What matters for this lane is that the reader fence is typed, redacted, monotonic, and visible to the brokers that would otherwise turn a stale index root into live authority. Future witness/quorum work can strengthen this without changing the digest-only projection model.


## r515 reader admission follow-through

`typed-post-detach-reader-admission-positive-and-negative-fixture-guarded` (`sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`) turns the checkpoint from a passive reader fence into an active broker admission requirement. Query, export, rehydration, remote-locator, and managed-copy readers must now emit `removable.media.local.post_detach.reader.admission.receipt` evidence recording `post-detach-reader-admission-checkpoint-observed-and-stale-roots-denied` before broker use; stale roots, restored old-handle roots, dual-active snapshots, broad reader scopes, live subscriptions, raw locators, filenames, host identity, and secret material fail closed.

## Hygiene

`tools/check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py` validates the positive checkpoint fixture against both the runtime schema and exact fixture schema, proves the red corpus fails, and keeps `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded`, `sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8`, and `known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation` wired through the r513 cutover receipt, r512 consumption receipt, fresh-authority receipt, denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

Last updated: 2026-06-10r558
