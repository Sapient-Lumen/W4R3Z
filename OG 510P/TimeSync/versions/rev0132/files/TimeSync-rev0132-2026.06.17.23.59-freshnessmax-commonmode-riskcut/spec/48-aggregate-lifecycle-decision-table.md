# 48 — Aggregate lifecycle decision table

rev0086 closes the ambiguity left by per-reference correction-authority lifecycle fields by making current, historical, and suppressed aggregate interpretation an executable decision surface.

## Problem

A correction-authority reference can now report lifecycle state, revocation posture, emergency withdrawal, contestation, notification posture, and portability posture. Those fields interact. Without a single decision table, implementations can accidentally treat an active-looking state as current even when an emergency withdrawal, revoked status, unresolved contestation, unchecked revocation, stale notification, or portability failure should suppress current interpretation.

## Placement

The machine-readable table is carried as:

```text
tests/aggregate-lifecycle-decision-table.yaml
schema/aggregate-lifecycle-decision-table.schema.json
```

Each lifecycle-bearing correction-authority reference also carries:

```text
authority_lifecycle.decision_table_digest
authority_lifecycle.current_interpretation_decision
```

The digest binds the decision table. The decision value is the local interpretation outcome for that reference.

## Decision vocabulary

The rev0086 vocabulary is closed for this revision:

```text
current_supported
current_supported_guarded
historical_only
suppressed_by_emergency_withdrawal
suppressed_by_revocation
suppressed_by_contestation
suppressed_by_unknown_lifecycle
suppressed_by_notification_staleness
suppressed_by_portability_failure
```

`current_supported` and `current_supported_guarded` are the only values that can accompany `lifecycle_effect: aggregate_interpretation_current`.

## Required rows

The table must include rows for:

```text
active-current
pending-rotation-current-guarded
expired-historical-only
revoked-suppressed
emergency-withdrawal-suppressed
contested-suppressed
unknown-redacted-suppressed
```

These rows are not documentation-only. `tools/validate_archive.py` validates that they exist and that the decision vocabulary is complete.

## Local reference rules

The validator derives the expected decision from the actual lifecycle posture.

- `revocation_status: revoked` or `lifecycle_state: revoked` resolves to `suppressed_by_revocation`.
- Active, completed, or contested emergency withdrawal resolves to `suppressed_by_emergency_withdrawal`.
- Pending, overturned, or unknown contestation resolves to `suppressed_by_contestation`.
- Unchecked, unknown, or redacted lifecycle/revocation resolves to `suppressed_by_unknown_lifecycle`.
- Expired or historical-only lifecycle resolves to `historical_only`.
- Pending rotation with current effect resolves to `current_supported_guarded`.
- Active lifecycle with current effect resolves to `current_supported`.

The explicit `current_interpretation_decision` must match the derived value.

## Digest rules

Known lifecycle states require a digest that binds `aggregate_correction_authority_lifecycle_rules`.

Every lifecycle reference requires a digest that binds `aggregate_lifecycle_decision_table`.

Non-empty contestation states require a contestation digest, including resolved-upheld contestation. Emergency withdrawal requires a withdrawal digest and a concrete resynchronization posture. Concrete emergency resynchronization requires a resynchronization-policy digest.

## Boundary

The decision table is not an authority registry, revocation service, notification service, transparency log, legal process, incident-response system, or provenance graph.

It determines only whether aggregate correction-authority evidence can support current aggregate interpretation, historical-only interpretation, or suppression. It does not update TimeState, profile assessment, current actionability, individual replay visibility, source traceability, or profile-obligation satisfaction.
