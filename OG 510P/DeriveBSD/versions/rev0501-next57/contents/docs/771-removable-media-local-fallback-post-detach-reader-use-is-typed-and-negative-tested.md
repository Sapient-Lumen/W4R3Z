# Removable-media local fallback post-detach reader use is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed revocation tombstones, r510 closed denial receipts, r511 closed fresh-authority reissue, r512 closed one-shot consumption, r513 closed atomic cutover, r514 closed checkpointing, and r515 closed reader admission. r516 closes the next seam: admission proves a broker observed the checkpoint, but every actual reader use still needs its own budget debit, sequence number, result projection, redaction proof, and receipt-before-result ordering.

See also:
- ADR: `adrs/ADR-0360-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.reader.use.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.use.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-use-receipt/`
- reader admission: `docs/770-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-use-positive-and-negative-fixture-guarded`
- `sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6`
- `known-bad-post-detach-reader-use-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.use.receipt` is required after the r515 reader-admission receipt and before any admitted reader result becomes visible. The receipt records `post-detach-reader-use-budgeted-sequenced-and-redacted` and `admitted-reader-use-receipted-before-observation-result`. It binds the admission digest `sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`, checkpoint sequence 44, one successor subject digest, one reader lease digest, a nonce, an idempotency key, reader-use sequence 45, a budget debit, a redacted projection digest, and a result digest.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.use.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins reader use to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 tombstone, r510 denial receipt, r511 fresh-authority receipt, r512 consumption receipt, r513 cutover receipt, r514 checkpoint receipt, r515 reader-admission receipt, and canonical import receipt;
- `admission_binding`: proves the use is derived from one exact admission receipt and that admission is not reusable as a use receipt;
- `use_request`: records the exact broker action, subject digest, lease digest, nonce, idempotency key, use sequence, and single-digest scope;
- `use_budget`: records budget units, before/after counts, debit-before-result ordering, exhausted-after-use state, no double spend, no replay window, and rate-limit posture;
- `observation_projection`: records the redacted field shape and keeps raw locators, untrusted filenames, host identity, full text, body text, recipient text, raw receipt payloads, and secrets out of the result;
- `result_sealing`: records the result digest and projection digest while denying result visibility before receipt visibility, live locators, persistent caches, replay tokens, stale-result acceptance, and read-side index mutation;
- `failure_policy`: fails closed on missing admission, admission replay, budget failure, double spend, broad scope, live subscription, export/rehydration request, raw locator/filename/body/full-text return, host identity, secret material, or offline-erasure overclaim.

## Red corpus

The reader-use red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-use-receipt/` with:

- `missing-reader-admission-receipt.json`
- `admission-reused-as-use-receipt.json`
- `budget-not-debited-before-result.json`
- `budget-exhausted-before-use-accepted.json`
- `double-spend-allowed.json`
- `replay-token-present.json`
- `broad-reader-scope.json`
- `live-subscription-requested.json`
- `export-granted-by-read.json`
- `raw-locator-returned.json`
- `filename-returned.json`
- `body-text-returned.json`
- `host-identity-leaked.json`
- `secret-material-present.json`
- `result-visible-before-receipt.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps reader admission from becoming a silent, replayable observation token.

## What this changes in implementation terms

The first launcher/indexer prototype now has thirteen separate artifacts in this lane:

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
12. the r515 reader-admission receipt proves a broker observed the checkpointed root before it used successor authority;
13. the r516 reader-use receipt proves each admitted observation was budgeted, sequenced, redacted, and receipted before result visibility.

The behavioral change is "no admitted read without a use receipt," not merely "no broker use without admission." Admission opens a narrow door; reader use consumes a narrow budgeted action.

## Notes for backend implementers

The first implementation can emit one reader-use receipt per broker result. Later batching is allowed only if each result still has exact admission digest, use sequence, nonce/idempotency key, budget debit, projection digest, result digest, and redaction evidence. A cached admission flag or a last-seen checkpoint counter is not enough.

## Hygiene

`tools/check_removable_media_local_post_detach_reader_use_receipt.py` validates the positive reader-use fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-use-positive-and-negative-fixture-guarded`, `sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6`, and `known-bad-post-detach-reader-use-shapes-must-fail-validation` wired through the r515 reader-admission receipt, r514 checkpoint receipt, r513 cutover receipt, r512 consumption receipt, fresh-authority receipt, denial receipt, revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.

## r517 reader-use ledger follow-up

r517 adds `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded` (`sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7`) so the r516 reader-use receipt is not the final durable state transition. `removable.media.local.post_detach.reader.use.ledger.receipt` records `post-detach-reader-use-ledger-root-monotonic-and-committed` and `reader-use-ledger-committed-before-result-release`: the debit must be committed to a monotonic compare-and-swap ledger root before the result release is considered durable. This closes double-spend, forked-root, rollback, stale-root, live-subscription, raw-locator, filename, body/full-text, host-identity, and secret-bearing ledger shapes.

Last updated: 2026-05-25r517
