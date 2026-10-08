# rev0096 to rev0097 migration map

rev0097 does not change the TimeState core, profile catalog, transport adapter catalog, evidence-class catalog, or schema IDs.

## New executable checks

Lifecycle-authority references now fail semantic validation when:

```text
anti_rollback_sequence.freeze_check.basis_time > anti_rollback_sequence.checked_at
lifecycle-authority discovery/renewal/sequence/freeze/rotation/delegation/compromise event time > lifecycle_status.evaluated_at
those same event times > anchor_evaluation.evaluated_at for current replay visibility
recovery_attestation_reference issued/verified/contained/portability time > compromise_response.checked_at
```

## New files

```text
+ tools/policy_lifecycle_temporal.py
+ AUDIT-2026.06.12-rev0097.md
+ archive/REV0096-TO-REV0097-MIGRATION-MAP.md
+ archive/REV0097-AUDIT-POLICY-LIFECYCLE-TEMPORAL-REFACTOR.md
+ examples/negative/policy-lifecycle-authority-freeze-basis-after-sequence-invalid.json
+ examples/negative/replay-transparency-policy-authority-discovery-after-lifecycle-invalid.json
+ examples/negative/replay-transparency-recovery-attestation-after-compromise-invalid.json
```

## Modified files

```text
~ tools/validate_archive.py
~ tests/semantic-test-vectors.yaml
~ tests/fixture-derivations.yaml
~ README.md
~ START_HERE.md
~ INDEX.md
~ VALIDATION-REPORT.md
~ REVISION-RECEIPT.json
~ frontier-ticket.json
~ CHANGELOG.md
~ tools/lint_revision_references.py
```

## Compatibility note

Existing valid rev0096 fixtures remain valid when lifecycle-authority and recovery-attestation events predate the lifecycle, compromise response, and replay evaluations that rely on them. New failures indicate previously accepted stale or impossible status evidence.
