# ADR-0373: Removable-media local fallback post-detach export-bundle deletion and revocation tombstone schema split are typed

Status: Accepted
Date: 2026-05-30

## Context

r528 made export-bundle access approval-bound, query-access-bound, recipient-bound, retention-bounded, and export-ledger receipted. It also required a deletion receipt, but the deletion/revocation terminal step was still a promise inside the access receipt rather than its own auditable artifact.

The schema-refactor backlog also now points at `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` as the highest-priority post-detach const-heavy runtime surface still shaped like an exact historical fixture.

## Decision

Accept `post-detach-export-bundle-deletion-positive-and-negative-fixture-guarded` and add `removable.media.local.post_detach.export.bundle.deletion.receipt`. A managed export is not complete until a deletion receipt binds the r528 export access receipt, proves bounded retention expiry or explicit revocation, records terminal managed-copy and remote-object posture, keeps support visibility digest-only, advances a CAS-rooted deletion ledger, and refuses to claim erasure of unmanaged offline copies.

Also accept `post-detach-revocation-tombstone-generic-runtime-schema-plus-exact-fixture-split`: `spec/removable.media.local.post_detach.revocation.tombstone.schema.json` is now runtime-shaped, while `spec/removable.media.local.post_detach.revocation.tombstone.fixture.schema.json` preserves the exact r509 tombstone fixture.

## Consequences

- Export deletion is no longer a flag inside the export access receipt.
- Managed export copies and controlled remote objects have a terminal, ledgered cleanup/revocation receipt.
- The cube preserves the r509 tombstone history while allowing dynamic tombstone ids, digests, and times in runtime broker outputs.
- Offline-copy erasure remains explicitly out of scope; future authority is denied, but unmanaged recipient copies are not magically erased.

Last updated: 2026-05-30r529
