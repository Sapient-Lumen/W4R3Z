# Current removable-media post-detach query-projection access

This is the r527 current-view surface for `removable.media.local.post_detach.query.projection.access.receipt`.

## Purpose

The r507 query projection says what a safe projection looks like. The r527 access receipt says what a specific query did before projection visibility: which lease authorized it, which fields were requested and returned, whether the tombstone gate was checked first, and which access-ledger root advanced.

## Executable surface

- Schema: `spec/removable.media.local.post_detach.query.projection.access.receipt.schema.json`
- Example: `spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json`
- Red corpus: `spec/examples/invalid/removable-media/post-detach-query-projection-access-receipt/`
- Checker: `tools/check_removable_media_local_post_detach_query_projection_access_receipt.py`
- Runtime query-projection schema: `spec/removable.media.local.post_detach.query.projection.schema.json`
- Exact query-projection fixture schema: `spec/removable.media.local.post_detach.query.projection.fixture.schema.json`

## Current invariants

Every projection access is lease-bound, single-query scoped, tombstone-checked before visibility, and limited to allowlisted fields. It is not an ambient index read. It cannot enable live subscriptions or aggregate counts in the first lane.

The support/debug projection remains digest-only. Raw payloads, body text, file paths, filenames, device identifiers, host identity, raw idempotency keys, and raw ledger roots are not visible through the access receipt.

Failures route to the r525 denial-selection receipt and the r526 rate-limit debit ledger receipt. A denied projection access must be receipted; silent failure or silent success is not the current contract.

The access ledger is CAS-rooted: expected root equals prior root, the new root advances, and rollback/fork/stale-root acceptance remains false.

## Audit/refactor tie-in

The same cut completes `post-detach-query-projection-generic-runtime-schema-plus-exact-fixture-split`. The historical r507 fixture remains exact; new broker outputs use the runtime-shaped schema.

Last updated: 2026-05-30r527
