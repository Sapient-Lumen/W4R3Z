# Removable-media local fallback post-detach revocation tombstones are typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, and r508 closed redacted export bundles. r509 closes the lifetime seam: stale query handles, stale export approvals, and digest-rehydration handles must not remain usable just because a redacted bundle or projection existed once.

See also:
- ADR: `adrs/ADR-0353-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.revocation.tombstone.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.revocation.tombstone.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-revocation-tombstone/`
- export bundle: `docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
- metadata background: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded`
- `sha256:6666666666666666666666666666666666666666666666666666666666666666`
- `known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation`

A revocation tombstone is admitted only for exact digest-bound subjects. It denies stale query, stale export, and stale digest-rehydration authority after explicit revocation or expiry. It must not claim that unmanaged offline copies have been erased.

## Evidence object shape

`spec/removable.media.local.post_detach.revocation.tombstone.schema.json` requires these closed-world sections:

- `contract_binding`: binds the tombstone to the r504 contract digest, r505 launch evidence digest, r506 recovery evidence digest, r507 query projection digest, r508 export bundle digest, and content import receipt digest;
- `revocation_authority`: requires same-surface explicit revocation or expiry, a revocation receipt digest, original-lease-bound actor scope, a reason code, monotonic sequence, effective timestamp, idempotency key digest, and terminal tombstone semantics;
- `revoked_subjects`: uses exact digest subjects only and keeps raw locator values out of the tombstone;
- `effect`: denies stale query handles, stale export approvals, and stale digest joins; requires fresh authority for new access; records that offline copy erasure is not claimed;
- `evidence_state`: records the tombstone anchor, deletion/revoke receipt, index updates, redacted receipt visibility, and no raw receipt payloads;
- `propagation`: closes live subscriptions, updates query/export indexes, and tells the rehydration broker to deny stale joins;
- `tombstone_storage`: keeps retention bounded and indexability limited to digest/reason fields, with raw paths, host identity, recipient identity text, and secret material absent;
- `failure_policy`: fails closed on stale use after tombstone, prefix revocation, raw locators, false offline erasure, unbounded retention, secrets, or successor authority without a fresh lease.

## Red corpus

The revocation-tombstone red corpus starts under `spec/examples/invalid/removable-media/post-detach-revocation-tombstone/` with:

- `query-after-tombstone.json`
- `export-after-tombstone.json`
- `rehydration-after-tombstone.json`
- `pattern-prefix-revocation.json`
- `raw-locator-included.json`
- `offline-erasure-claimed.json`
- `missing-deletion-receipt.json`
- `unbounded-retention.json`
- `secret-material-present.json`
- `successor-without-fresh-lease.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps revocation honest: old handles stop working, but the system does not pretend to control copies that already left the host.

## What this changes in implementation terms

The first launcher/indexer prototype now has six separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles must stop working.

The tombstone is not a garbage collector and not a magical eraser. It is a terminal denial artifact for future authority over exact digest subjects.

## Notes for backend implementers

Do not implement revocation as “delete a file if found.” Deletion can be evidence when the object is managed, but revocation must also update the query projection index, export bundle index, and digest-rehydration broker. Do not accept pattern or prefix revocation in the first lane; use exact digest subjects. Do not write raw locator values, raw paths, host identity, recipient text, or secrets into the tombstone.

If an export bundle already left as an offline file, the correct claim is `not-claimed-erased-only-future-authority-denied`. The UI should say that future DeriveBSD-mediated access is revoked and any managed remote/local object was revoked or deleted if present; it should not say that every external copy disappeared.

## Hygiene

`tools/check_removable_media_local_post_detach_revocation_tombstone.py` validates the positive tombstone fixture, proves the red corpus fails, and keeps `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded`, `sha256:6666666666666666666666666666666666666666666666666666666666666666`, and `known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation` wired through the export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.


## r510 denial receipt addendum

r510 adds `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded` with digest `sha256:6868686868686868686868686868686868686868686868686868686868686868` and policy `known-bad-post-detach-denial-receipt-shapes-must-fail-validation`. The tombstone now requires a `removable.media.local.post_detach.denial.receipt` object when stale query, export, rehydration, remote-locator, or managed-copy attempts are denied after tombstone visibility. This keeps deny-after-revocation auditable without raw stale handles, locators, filenames, host identity, recipient text, or receipt payloads. Schema: `spec/removable.media.local.post_detach.denial.receipt.schema.json`.

## r511 fresh-authority successor note

r511 adds `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` / `sha256:7171717171717171717171717171717171717171717171717171717171717171` as the only ordinary successor path after tombstone-caused denial. `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` keeps stale-handle replay red-tested. The tombstone stays immutable audit evidence; a fresh-authority receipt points to it by digest, mints new exact digest subjects, and does not claim offline copies were erased.

Last updated: 2026-05-22r512
