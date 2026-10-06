# Removable-media local fallback post-detach query projection is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Quarantine→Promote

r504 closed the contract, r505 closed launch evidence, and r506 closed recovery evidence. r507 closes the next seam: the resulting receipts must not become an ambient metadata index that leaks raw media paths, observed device hints, host identity, filenames, or full-text content.

See also:
- ADR: `adrs/ADR-0351-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.query.projection.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.query.projection.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-query-projection/`
- recovery evidence: `docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md`
- metadata background: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-query-projection-positive-and-negative-fixture-guarded`
- `sha256:5656565656565656565656565656565656565656565656565656565656565656`
- `known-bad-query-projection-shapes-must-fail-validation`

Derivative receipt queryability is admitted only as a lease-bound, redacted, derived projection after recovery evidence validates. The authoritative receipts remain authoritative; the index snapshot is evidence for navigation, not provenance authority.

## Evidence object shape

`spec/removable.media.local.post_detach.query.projection.schema.json` requires these closed-world sections:

- `contract_binding`: binds the projection to the r504 contract digest, r505 launch evidence digest, r506 recovery evidence digest, and content import receipt digest;
- `lease_binding`: requires `lease-required-no-ambient-index-read`, caller-bound single-query scope, revocation check, no open-ended live subscription, and bounded retention;
- `source_receipts`: proves the projection starts only after recovery evidence validates and keeps raw media hints, original media paths, and host paths out of the index;
- `projection_policy`: fixes the minimal allowlisted field set and states that the index is derived evidence, not authority;
- `redaction`: keeps original filenames, untrusted filename text, observed hints, device labels/serials, host user/home identity, and body text out of the first lane;
- `query_index`: keeps the index a derived snapshot with bounded equality queries, digest-only explicit joins, no aggregate counts, and no cross-lane ambient query;
- `export_policy`: keeps support-bundle projection redacted by default and requires explicit approval for export;
- `failure_policy`: fails closed on query without lease, raw path/hint leakage, full-text or filename indexing, host identity leakage, open-ended subscription, unbounded retention, or cross-lane query without explicit digest join.

## Red corpus

The query-projection red corpus starts under `spec/examples/invalid/removable-media/post-detach-query-projection/` with:

- `query-without-lease.json`
- `raw-media-path-leaked.json`
- `observed-hints-indexed.json`
- `full-text-indexing-enabled.json`
- `host-identity-leaked.json`
- `live-subscription-open-ended.json`
- `retention-unbounded.json`
- `cross-lane-query-without-explicit-join.json`
- `filename-indexed.json`

Each fixture is intentionally close to the canonical object and must fail validation. This prevents a convenient incident-search surface from becoming ambient telemetry.

## What this changes in implementation terms

The first launcher/indexer prototype now has four separate artifacts in this lane:

1. the r504 contract says which authority is allowed;
2. the r505 launch evidence says what the FreeBSD backend observed at launch;
3. the r506 recovery evidence says what survived and whether derivative receipt visibility is allowed;
4. the r507 query projection says what a user, support tool, or incident bundle may search or export about that receipt.

A receipt can be true and still not be ambiently queryable. Queryability is observation authority and therefore must be leased, redacted, and receipt-visible.

## Notes for backend implementers

Treat the index as a derived snapshot built from authoritative receipt digests. Do not index raw mount paths, `/ingest` names, device labels, serials, physical-path hints, host user names, home paths, original filenames, or body/full-text extracted from the derivative. A support or incident bundle may carry the projection plus authoritative receipt digests; rehydration requires explicit digest joins.

The first lane forbids live subscriptions and aggregate counts because they create enumeration surfaces that outlive the single reviewed import. Later lanes can add those features only with separate lease, threshold, retention, and redaction semantics.

## Hygiene

`tools/check_removable_media_local_post_detach_query_projection.py` validates the positive query-projection fixture, proves the red corpus fails, and keeps `typed-post-detach-query-projection-positive-and-negative-fixture-guarded`, `sha256:5656565656565656565656565656565656565656565656565656565656565656`, and `known-bad-query-projection-shapes-must-fail-validation` wired through the recovery evidence, contract, content import plan/receipt, and preopen map.

## r508 export-bundle continuation

r508 adds `removable.media.local.post_detach.export.bundle` so the redacted query projection cannot be bypassed by a support or incident raw debug bundle. The query projection now carries `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded`, `sha256:6262626262626262626262626262626262626262626262626262626262626262`, and `known-bad-post-detach-export-bundle-shapes-must-fail-validation` and points to `spec/removable.media.local.post_detach.export.bundle.schema.json`. Export starts from the redacted projection and authoritative receipt digests; raw receipt payloads, raw paths, observed hints, host identity, untrusted filenames, and body text stay out of the first-lane bundle.



## r509 tombstone denial

r509 adds `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded` so receipt search handles are not durable ambient authority. After tombstone visibility, stale query handles must return `deny-stale-handle-fail-closed`, export approvals must fail closed, and digest rehydration requires fresh authority instead of silently joining old projection/bundle digests back to authoritative receipts.


## r510 denial receipt addendum

Query attempts against tombstoned handles now produce a redacted denial receipt guarded by `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded`. The projection may expose a digest/reason-code summary of the denial, but not raw handle values, raw paths, filenames, host identity, or body text.

## r511 fresh-authority query note

r511 adds `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` / `sha256:7171717171717171717171717171717171717171717171717171717171717171` so query reissue after denial is visible as a fresh-authority receipt, not as a live continuation of the old query handle. The projection may expose only redacted digest/purpose/fresh-lease summaries.

Last updated: 2026-05-22r512
