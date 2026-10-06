# Removable-media local fallback post-detach export bundles are redacted and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, and r507 closed query projection. r508 closes the next seam: support, incident, and debug bundles must not become a raw export path for evidence that the first lane deliberately kept out of ambient queryability.

See also:
- ADR: `adrs/ADR-0352-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.export.bundle.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.export.bundle.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-export-bundle/`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
- metadata background: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded`
- `sha256:6262626262626262626262626262626262626262626262626262626262626262`
- `known-bad-post-detach-export-bundle-shapes-must-fail-validation`

A post-detach support or incident bundle is admitted only when it starts from the redacted r507 query projection, carries explicit approval and recipient binding, and excludes raw receipt payloads. A raw debug bundle is not a first-lane artifact.

## Evidence object shape

`spec/removable.media.local.post_detach.export.bundle.schema.json` requires these closed-world sections:

- `contract_binding`: binds the bundle to the r504 contract digest, r505 launch evidence digest, r506 recovery evidence digest, r507 query projection digest, and content import receipt digest;
- `export_authority`: requires `explicit-human-approved-export-no-ambient-debug-dump`, approval receipt digest, caller-bound single export, recipient digest, purpose scope, and revocation check;
- `source_projection`: proves that export starts from the redacted query projection and authoritative receipt digests, with no raw receipt payloads included;
- `bundle_contents`: admits only redacted query projection, authoritative receipt digests, schema digests/refs, validation summary, and export approval receipt digest;
- `redaction`: keeps raw media paths, observed hints, device labels/serials, host identity, original filenames, filename text, body text, environment values, fd paths, and mount paths out of the bundle;
- `transport_storage`: keeps transport local-file or approved-remote-object shaped, recipient-bound if it leaves the host, live-locator-free, retention-bounded, and deletion-receipt-shaped;
- `verifier_model`: keeps basic verification offline, schema-backed, digest-rehydrated, and explicit that the bundle is derived observation rather than authority;
- `failure_policy`: fails closed on export without approval, raw paths/hints, raw receipt payloads, host identity, filename/body text, unbound recipient, unbounded retention, live locator, or secret material.

## Red corpus

The export-bundle red corpus starts under `spec/examples/invalid/removable-media/post-detach-export-bundle/` with:

- `export-without-approval.json`
- `raw-media-path-included.json`
- `raw-receipt-payload-included.json`
- `host-identity-included.json`
- `untrusted-filename-included.json`
- `body-text-included.json`
- `recipient-unbound.json`
- `retention-unbounded.json`
- `live-locator-present.json`
- `secret-material-included.json`

Each fixture is intentionally close to the canonical object and must fail validation. This prevents incident pressure from turning the evidence system into a broad debug archive.

## What this changes in implementation terms

The first launcher/indexer prototype now has five separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what may be searched about the receipt;
5. the r508 export bundle says what may leave the host or enter a support/incident handoff.

The export bundle is not a substitute for the authoritative receipts. It is a portable, redacted observation envelope whose rehydration requires explicit digest joins.

## Notes for backend implementers

Do not implement “download debug bundle” as a tarball of receipt directories. Build the bundle from the validated query projection and explicit receipt digests. Keep raw receipt payloads, media paths, `/ingest` paths, mount paths, host names, user names, environment values, fd paths, device serials, labels, original filenames, and body text out of the first lane.

If a remote transport is used, record the remote-object upload receipt separately and keep the locator out of the first-lane bundle unless a later typed transport profile admits it. The first lane prefers offline-verifiable bundle contents and digest rehydration.

## Hygiene

`tools/check_removable_media_local_post_detach_export_bundle.py` validates the positive export-bundle fixture, proves the red corpus fails, and keeps `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded`, `sha256:6262626262626262626262626262626262626262626262626262626262626262`, and `known-bad-post-detach-export-bundle-shapes-must-fail-validation` wired through the query projection, recovery evidence, contract, content import plan/receipt, and preopen map.



## r509 revocation join

r509 adds `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded` and `known-bad-post-detach-revocation-tombstone-shapes-must-fail-validation` as the lifetime gate for this export bundle. The export bundle remains redacted, but any stale query handle, stale export approval, or digest-rehydration attempt must first check `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` and deny after `sha256:6666666666666666666666666666666666666666666666666666666666666666` is visible. The permitted claim is `not-claimed-erased-only-future-authority-denied`, not “every offline copy disappeared.”


## r510 denial receipt addendum

Export attempts after a visible tombstone now require `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded` and `sha256:6868686868686868686868686868686868686868686868686868686868686868`. A stale export approval must fail closed and produce a redacted denial receipt rather than silently succeeding, silently disappearing, or exporting raw debug context.

## r511 fresh-authority export note

r511 adds `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` / `sha256:7171717171717171717171717171717171717171717171717171717171717171` so export reissue after a tombstone must pass through a fresh-authority receipt. Support/debug bundles may mention the fresh-authority digest, but they must not turn old export approvals, stale handles, filenames, or raw locators into a hidden renewal path.

Last updated: 2026-05-22r512
