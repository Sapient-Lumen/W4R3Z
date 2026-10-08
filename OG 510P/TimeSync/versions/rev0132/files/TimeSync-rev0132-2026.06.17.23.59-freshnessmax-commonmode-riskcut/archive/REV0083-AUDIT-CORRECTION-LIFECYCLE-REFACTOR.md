# rev0084 audit/refactor — correction-authority lifecycle validator seam

The rev0083 validator separated aggregate revision lineage from correction-authority authorization, notification, and portability. The rev0084 audit found a new seam: lifecycle state should not be mixed into either revision-lineage relationship checks or notification freshness checks.

## Refactor

rev0084 adds:

```text
check_aggregate_correction_authority_lifecycle(...)
```

and leaves:

```text
check_aggregate_correction_authority_reference(...)
check_aggregate_revision_lineage(...)
```

in their narrower roles.

## Result

- Revision lineage still handles prior digests, monotonic sequence, correction effects, withdrawal/supersession/reconciliation, and suppressed-delta leakage.
- Correction-authority reference still handles authorization, notification, and compatible-operator correction-chain portability.
- Lifecycle handling now separately checks active/pending/expired/revoked/emergency/contested states, revocation checks, emergency-withdrawal suppression, contestation digest binding, and lifecycle non-leakage boundaries.

This reduces copy-paste drift and prevents lifecycle semantics from silently widening into profile evidence, privacy controls, or provenance.
