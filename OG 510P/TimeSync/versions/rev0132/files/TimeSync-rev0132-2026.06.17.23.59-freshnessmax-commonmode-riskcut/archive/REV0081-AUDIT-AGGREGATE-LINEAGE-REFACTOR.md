# Audit/refactor — aggregate lineage validator seam

## Finding

rev0081 introduced aggregate privacy controls, but aggregate publication interpretation was split between cadence, privacy controls, compromise-era suppression, and recovery-audit rollups. Correction and reconciliation semantics would have increased copy-paste drift if added directly to those checks.

## Refactor

rev0082 isolates aggregate correction / withdrawal / supersession / reconciliation semantics in:

```text
check_aggregate_revision_lineage(...)
```

and adds:

```text
digest_binds(...)
```

for repeated digest-binding checks used by prior aggregate and revision-chain fields.

## Preserved boundary

The refactor preserves the existing rev0081 aggregate privacy-control semantics. It adds only the new lineage checks and does not alter the six-field TimeState core, profile assessment model, transparency trust-policy layer, or authorized-verifier challenge layer.

## Follow-up risk

The next likely seam is correction-authority portability: if multiple operators publish aggregate corrections, TimeSync needs a bounded way to refer to authority, notification, and chain compatibility without becoming a publication protocol.
