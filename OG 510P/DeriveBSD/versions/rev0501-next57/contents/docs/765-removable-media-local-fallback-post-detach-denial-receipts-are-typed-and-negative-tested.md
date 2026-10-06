# Removable-media local fallback post-detach denial receipts are typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, and r509 closed revocation tombstones. r510 closes the next audit seam: after a tombstone is visible, stale query, export, rehydration, remote-locator, or managed-copy attempts must not merely disappear as generic failures. They must produce a redacted denial receipt that proves the denial happened without reintroducing the raw handle, path, filename, host identity, recipient text, or receipt payload.

See also:
- ADR: `adrs/ADR-0354-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.denial.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.denial.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-denial-receipt/`
- revocation tombstone: `docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`
- export bundle: `docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded`
- `sha256:6868686868686868686868686868686868686868686868686868686868686868`
- `known-bad-post-detach-denial-receipt-shapes-must-fail-validation`

A `removable.media.local.post_detach.denial.receipt` is required whenever a stale query handle, export approval, digest rehydration request, remote locator, or managed-copy handle is rejected because a revocation tombstone is visible. The receipt is exact-digest-subject-only, redacted, and causally bound to the tombstone. It records denial, not erasure.

## Evidence object shape

`spec/removable.media.local.post_detach.denial.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: binds the denial receipt to the r504 contract, r505 launch evidence, r506 recovery evidence, r507 query projection, r508 export bundle, r509 revocation tombstone, and canonical import receipt;
- `triggering_attempt`: records the attempt class, time, caller digest, and handle digest while keeping raw handles, locators, and ambient reauthentication absent;
- `denied_subjects`: uses exact digest subjects only and excludes raw locators, untrusted filenames, and host identity;
- `denial_decision`: records `deny-fail-closed-stale-authority`, a reason code, fresh-lease requirement, no successor authority, and no offline-copy erasure claim;
- `evidence_state`: records tombstone observation, monotonic denial sequence, broker receipts, index update receipt, and redaction/secret absence;
- `observability`: makes a redacted denial summary visible to query/support surfaces without exposing raw handle material;
- `failure_policy`: fails closed if stale authority is allowed, if raw handle/path/name/identity data appears, if retry is unbounded, or if a successor authority appears without a fresh lease.

## Red corpus

The denial-receipt red corpus starts under `spec/examples/invalid/removable-media/post-detach-denial-receipt/` with:

- `query-denial-without-tombstone.json`
- `export-denial-allows-success.json`
- `rehydration-denial-allows-success.json`
- `raw-handle-included.json`
- `raw-locator-included.json`
- `host-identity-leaked.json`
- `untrusted-filename-included.json`
- `missing-monotonic-sequence.json`
- `retry-not-rate-limited.json`
- `successor-without-fresh-lease.json`

Each fixture is intentionally close to the canonical object and must fail validation. This keeps the deny-after-revocation path from becoming either an invisible black hole or a new metadata leak.

## What this changes in implementation terms

The first launcher/indexer prototype now has seven separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter support/incident handoff;
6. the r509 revocation tombstone says when old query/export/rehydration handles must stop working;
7. the r510 denial receipt proves a stale use was denied after the tombstone, without leaking raw stale authority material.

The important behavioral change is not only “deny.” It is “deny, causally join to the tombstone, emit redacted evidence, and require a fresh lease for future authority.”

## Notes for backend implementers

Do not treat a stale-handle denial as a generic authorization error. The query broker, export broker, rehydration broker, remote-object adapter, and managed-copy adapter must emit the same denial posture when the tombstone is the cause. The denial receipt should be small enough for UX/support surfaces to show by digest and reason code, but it must not include raw handles, raw paths, original filenames, recipient text, host identity, receipt payloads, or secret material.

The receipt is not a retry token. If a user wants access again, the correct successor is a fresh lease and a new policy decision, not replay of the stale handle. The UI copy should keep the r509 honesty rule: future DeriveBSD-mediated authority is denied, while unmanaged offline copies are not claimed erased.

## Hygiene

`tools/check_removable_media_local_post_detach_denial_receipt.py` validates the positive denial receipt fixture, proves the red corpus fails, and keeps `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded`, `sha256:6868686868686868686868686868686868686868686868686868686868686868`, and `known-bad-post-detach-denial-receipt-shapes-must-fail-validation` wired through the revocation tombstone, export bundle, query projection, recovery evidence, contract, content import plan/receipt, and preopen map.


## r511 fresh-authority successor note

r511 adds `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` so a denial receipt remains a denial receipt, not a renewal token. Any later successor authority must bind this denial receipt and the r509 tombstone through `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json`, mint `sha256:7171717171717171717171717171717171717171717171717171717171717171`, and carry `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` so stale handles cannot be replayed as fresh access.

Last updated: 2026-05-22r512
