# Removable-media local fallback post-detach export-bundle deletion and revocation tombstone schema split

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Bundles, Registry→Diff→Gate

## Problem

r528 made export-bundle access auditable and required a deletion receipt, but terminal deletion was still only a requirement inside the access receipt. That left one more seam: an export could be approved, visible, and retention-bounded without a standalone receipt proving that the managed copy or controlled remote object actually reached a terminal state.

The cube schema audit also kept `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` as the next highest-priority const-heavy post-detach runtime surface.

## Change

r529 adds `removable.media.local.post_detach.export.bundle.deletion.receipt` with `post-detach-export-bundle-deletion-positive-and-negative-fixture-guarded`. The receipt binds:

- the exact r528 export access receipt by computed digest;
- the export bundle and revocation tombstone by computed digest;
- bounded retention expiry or explicit revocation as the deletion trigger;
- terminal local managed-copy and controlled remote-object posture;
- absence of live/raw locators and support-visible raw values;
- explicit non-claim of unmanaged offline-copy erasure;
- CAS-rooted deletion-ledger advancement after the export ledger.

r529 also adds `post-detach-revocation-tombstone-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` is now the runtime contract, while `spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json` preserves the exact r509 example.

## Negative corpus

The red corpus rejects missing or stale export-access bindings, deletion before expiry without revocation, live remote objects, live local managed copies, offline-erasure overclaims, raw locator visibility, unbounded retention, non-advancing deletion ledger roots, and non-terminal managed-export outcomes.

## Validation

Run:

```bash
python3 tools/check_removable_media_local_post_detach_export_bundle_deletion_receipt.py
python3 tools/check_removable_media_local_post_detach_revocation_tombstone.py
python3 tools/check_cube_schema_refactor_backlog.py
```

Last updated: 2026-05-30r529
