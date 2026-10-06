# ADR-0372: Removable-media local fallback post-detach export-bundle access and export-bundle schema split are typed

Status: Accepted
Date: 2026-05-30

## Context

r508 made the post-detach export bundle redacted, approval-bound, recipient-bound, and derived from the query projection rather than raw receipts. r527 added a per-access query-projection receipt. The next gap is that export release itself still looks like a property of the bundle rather than a separately auditable access transition.

The schema audit also identifies `spec/removable.media.local.post_detach.export.bundle.schema.json` as the highest-priority const-heavy post-detach schema still acting like an exact fixture.

## Decision

Accept `post-detach-export-bundle-access-positive-and-negative-fixture-guarded` and add `removable.media.local.post_detach.export.bundle.access.receipt`. A bundle can become visible only after an access receipt proves explicit approval, committed query-projection access, revocation/tombstone checks, recipient binding, redacted contents, bounded retention/deletion posture, denial/rate-limit joins for failures, and a CAS-rooted export ledger.

Also accept `post-detach-export-bundle-generic-runtime-schema-plus-exact-fixture-split`: the r508 export-bundle schema is now runtime-shaped, while `spec/removable.media.local.post_detach.export.bundle.fixture.schema.json` preserves the exact historical fixture.

## Consequences

- Export release is no longer implicit in the export bundle object.
- Support/debug access cannot bypass query-projection access, approval, recipient binding, or tombstone checks.
- The schema-refactor backlog advances by one high-priority post-detach surface without rewriting historical r508 evidence.

Last updated: 2026-05-30r528
