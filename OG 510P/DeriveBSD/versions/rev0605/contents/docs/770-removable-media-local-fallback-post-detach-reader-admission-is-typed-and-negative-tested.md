# Removable-media local fallback post-detach reader admission is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, r510 closed denial receipts, r511 closed fresh-authority reissue, r512 closed one-shot consumption, r513 closed atomic successor-index cutover, and r514 closed monotonic checkpointing. r515 closes the next seam: a checkpoint is not trusted merely because it exists; every reader broker must prove it observed the checkpointed root before using query, export, rehydration, remote-locator, or managed-copy authority.

See also:
- ADR: `adrs/ADR-0359-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.admission.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-admission-receipt/`
- checkpoint receipt: `docs/769-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded`
- `sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`
- `known-bad-post-detach-reader-admission-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.admission.receipt` is required after the r514 successor-index checkpoint and before any post-checkpoint reader broker uses the successor index. The admission receipt records `post-detach-reader-admission-checkpoint-observed-and-stale-roots-denied` and `checkpoint-observed-before-reader-broker-use`. It binds sequence 44, the checkpoint digest, checkpoint marker, index-root digest, successor-root digest, reader lease digest, and a single successor subject digest. The reader does not get to use a stale backup root, restored old-handle root, dual-active snapshot, broad prefix, live subscription, or raw locator request and call that a normal query.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins reader admission to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, r511 fresh-authority receipt, r512 consumption receipt, r513 cutover receipt, r514 checkpoint receipt, and canonical import receipt;
- `checkpoint_binding`: records the checkpoint digest, marker, sequence, minimum accepted sequence, index/tombstone/denial/successor roots, checkpoint outcome, observation bit, and immutability bit;
- `reader_request`: records the exact broker, purpose, successor subject digest, reader lease digest, single-successor scope, no pattern/prefix subject, no live subscription, no raw locator request, and no untrusted filename request;
- `admission_state`: proves the reader observed the checkpoint sequence and accepted root, applied the reader fence, and rejected stale roots, old-handle roots, dual-active snapshots, rollback, and use-before-admission;
- `admitted_authority`: keeps the canonical fixture narrow by admitting only query projection for one successor digest and denying export, rehydration, remote-locator, and managed-copy broadening;
- `redaction`: keeps raw locators, untrusted filenames, host identity, full text, body text, recipient text, raw receipt payloads, and secret material out of the admission projection;
- `failure_policy`: fails closed on missing checkpoint receipts, missing observation, below-floor roots, stale roots, old-handle restoration, dual-active snapshots, broad scopes, live subscriptions, use-before-admission, raw locator/filename indexing, host identity, secret material, or offline-erasure overclaim.

## Red corpus

The reader-admission red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-admission-receipt/` with:

- `missing-checkpoint-receipt.json`
- `checkpoint-not-observed.json`
- `below-checkpoint-sequence.json`
- `stale-index-root-accepted.json`
- `old-handle-root-accepted.json`
- `dual-active-snapshot-accepted.json`
- `broad-reader-scope.json`
- `live-subscription-requested.json`
- `broker-use-before-admission.json`
- `raw-locator-included.json`
- `filename-indexed.json`
- `secret-material-present.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps the r514 checkpoint from becoming a passive note that brokers can bypass.

## What this changes in implementation terms

The first launcher/indexer prototype now has twelve separate artifacts in this lane:

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
11. the r514 checkpoint receipt proves readers cannot accept stale or restored index roots after that cutover;
12. the r515 reader-admission receipt proves a broker observed the checkpointed root before it used successor authority.

The behavioral change is "no broker use without checkpoint observation," not merely "the index has a checkpoint somewhere." If a reader cannot prove it saw the fenced root, it fails closed and emits denial/recovery evidence instead of silently accepting stale state.

## Notes for backend implementers

The first implementation can emit one admission receipt per broker attempt. Later batching is allowed only if each admitted subject still has exact checkpoint sequence, root digest, reader lease, subject digest, broker purpose, and redaction evidence. A cache of "last observed checkpoint" is not enough unless the admission receipt binds that cache state to the exact broker action.

## Hygiene

`tools/check_removable_media_local_post_detach_reader_admission_receipt.py` validates the positive admission fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded`, `sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`, and `known-bad-post-detach-reader-admission-shapes-must-fail-validation` wired through the r514 checkpoint receipt, r513 cutover receipt, r512 consumption receipt, fresh-authority receipt, denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

Last updated: 2026-05-24r516
## r516 follow-on reader use

`typed-post-detach-reader-use-positive-and-negative-fixture-guarded` (`sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6`) follows this admission receipt. Reader admission proves the broker observed the checkpoint; reader use proves each admitted observation was budgeted, sequenced, redacted, and receipted before result visibility. `post-detach-reader-use-budgeted-sequenced-and-redacted` keeps admission from becoming a replayable or unmetered observation token.
