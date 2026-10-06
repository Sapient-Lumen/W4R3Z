# Removable-media local fallback post-detach successor index cutover is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, r510 closed denial receipts, r511 closed fresh-authority reissue, and r512 closed one-shot consumption. r513 closes the next seam: the successor index update is no longer just a digest mentioned by the consumption receipt. It is a typed receipt that proves old handles became terminal before exact successors became live.

See also:
- ADR: `adrs/ADR-0357-removable-media-local-fallback-post-detach-successor-index-cutover-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-successor-index-cutover-receipt/`
- consumption receipt: `docs/767-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded`
- `sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3`
- `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation`

A `removable.media.local.post_detach.successor.index.cutover.receipt` is required after a fresh-authority consumption receipt and before successor query/export/rehydration/remote-locator/managed-copy authority is usable. The receipt records `successor-index-cutover-old-handles-terminal-successors-exact`, joins to the r512 consumption receipt, makes old query/export/rehydration/managed-copy/remote-locator handles terminal, activates only exact successor digests minted by the consumption receipt, denies dual-active windows, denies rollback to the old index, and keeps raw locator, filename, host identity, full-text, body, recipient, receipt payload, and secret values out of the searchable projection.

## Evidence object shape

`spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins the cutover receipt to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, r511 fresh-authority receipt, r512 consumption receipt, and canonical import receipt;
- `consumed_authority`: records the fresh-authority consumption receipt, consumed marker, predecessor successor-index update digest, and absence of stale/raw handle reuse;
- `old_index_state`: records the old query/export/rehydration/managed-copy/remote-locator digests, tombstone and denial digests, old-handle terminal state, no dual-active window, and no raw locator indexing;
- `successor_index_state`: records exact new query/export/rehydration/managed-copy/remote-locator successor digests and rejects orphan successors, forked successors, broadening, pattern subjects, raw locators, filenames, host identity, and full-text indexing;
- `cutover_decision`: records `successor-index-cutover-old-handles-terminal-successors-exact`, atomic cutover, no rollback, monotonic append-only sequencing, redaction preservation, no secrets, and no offline-erasure overclaim;
- `evidence_state`: records the append-only log, cutover marker, predecessor update digest, successor index snapshot, rollback protection, no dual-active observation, and redaction state;
- `failure_policy`: fails closed on missing consumption, stale old handles, dual-active windows, orphan/forked successors, scope broadening, pattern subjects, raw locator/filename indexing, rollback, missing cutover markers, full-text indexing, secret material, or offline-erasure overclaim.

## Red corpus

The successor-index cutover red corpus starts under `spec/examples/invalid/removable-media/post-detach-successor-index-cutover-receipt/` with:

- `missing-consumption-receipt.json`
- `old-handle-still-live.json`
- `dual-active-window-allowed.json`
- `orphan-successor-allowed.json`
- `forked-successor-allowed.json`
- `pattern-successor-subject.json`
- `raw-locator-indexed.json`
- `filename-indexed.json`
- `rollback-allowed.json`
- `missing-cutover-marker.json`
- `secret-material-present.json`
- `full-text-indexed.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps the r512 successor-index update from becoming a silent dual-live, forked, or rollbackable state transition.

## What this changes in implementation terms

The first launcher/indexer prototype now has ten separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles stop working;
7. the r510 denial receipt proves stale use was denied after the tombstone;
8. the r511 fresh-authority receipt proves later successor authority came from a fresh lease and policy decision;
9. the r512 consumption receipt proves that fresh authority was applied once to exact successor artifacts;
10. the r513 cutover receipt proves that the searchable/usable index made the old handles terminal and activated only those exact successors.

The behavioral change is "successor index cutover is auditable and atomic," not "a consumption receipt contains a promising index-update hash." If a later query/export/rehydration broker sees both old and successor rows live, or sees a successor row without this cutover receipt, it fails closed.

## Notes for backend implementers

The query broker, export broker, rehydration broker, remote-object adapter, and managed-copy adapter should not mark successor rows live until the cutover receipt is written and the cutover marker appears in the append-only evidence log. The receipt may point to old tombstone, denial, fresh-authority, and consumption digests, but it must not include raw handles, raw paths, original filenames, recipient text, host identity, full receipt payloads, body text, or secret material.

A support operator should be able to answer: "Did the old handle become terminal before this successor went live?" without seeing the raw removable-media locator.

## r514 checkpoint receipt

The cutover receipt now feeds `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded` and `sha256:c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8` into a separate checkpoint artifact. r513 proves the old-to-successor transition; r514 records `successor-index-checkpoint-cutover-root-anchored-and-rollback-denied` and proves post-cutover readers reject stale index roots, restored old-handle roots, and dual-active snapshots before successor query/export/rehydration authority is used.

## Hygiene

`tools/check_removable_media_local_post_detach_successor_index_cutover_receipt.py` validates the positive cutover fixture, proves the red corpus fails, and keeps `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded`, `sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3`, and `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation` wired through the r512 consumption receipt, fresh-authority receipt, denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

Last updated: 2026-05-23r514
