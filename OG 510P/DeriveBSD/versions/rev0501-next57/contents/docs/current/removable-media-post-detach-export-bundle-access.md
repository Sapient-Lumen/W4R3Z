# Current removable-media post-detach export-bundle access

The current post-detach export path is approval-bound, query-access-bound, recipient-bound, and export-ledger receipted. A redacted r508 export bundle does not become visible merely because it exists; r528 requires a typed `removable.media.local.post_detach.export.bundle.access.receipt` first.

The access receipt proves explicit approval, a committed query-projection access receipt, revocation and tombstone checks before export, recipient-bound transport, bounded retention/deletion posture, redacted contents only, denial-selection and rate-limit joins for failed exports, and monotonic export ledger advancement.

The red corpus rejects missing approval, stale query-access binding, missing tombstone checks, raw authoritative receipts, raw paths, unbound recipients, live locators, unbounded retention, non-advancing export ledger roots, and missing deletion-receipt requirements.

Last updated: 2026-05-30r528
