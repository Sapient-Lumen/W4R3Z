# Removable-media local fallback post-detach export-bundle access and schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Bundles, Registry→Diff→Gate

## Problem

r508 made post-detach export bundles redacted and approval-bound, and r527 made query-projection access auditable. The remaining seam was the actual bundle release: a broker could still treat an already-shaped bundle as visible without a separate receipt proving that approval, query-access, recipient binding, tombstone checks, and transport/retention constraints were all evaluated for this attempt.

The cube schema audit also kept `spec/removable.media.local.post_detach.export.bundle.schema.json` as the highest-priority const-heavy post-detach schema, which meant dynamic runtime exports were still forced through an exact historical fixture shape.

## Change

r528 adds `removable.media.local.post_detach.export.bundle.access.receipt` with `post-detach-export-bundle-access-positive-and-negative-fixture-guarded`. The receipt binds:

- explicit export approval;
- committed `removable.media.local.post_detach.query.projection.access.receipt`;
- revocation and tombstone checks before export visibility;
- recipient-bound transport and bounded retention/deletion posture;
- redacted bundle contents only;
- denial-selection and rate-limit debit availability for failed export attempts;
- a CAS-rooted export ledger with prior, expected, new, and anchor roots.

r528 also adds `post-detach-export-bundle-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.export.bundle.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.export.bundle.fixture.schema.json` preserves the exact r508 example.

## Negative corpus

The red corpus rejects missing approval, stale query-access binding, missing tombstone checks, raw authoritative receipts, raw path visibility, unbound recipients, live locators, unbounded retention, non-advancing export ledger roots, and missing deletion-receipt requirements.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_export_bundle_access_receipt.py
python3 tools/check_removable_media_local_post_detach_export_bundle.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r528
