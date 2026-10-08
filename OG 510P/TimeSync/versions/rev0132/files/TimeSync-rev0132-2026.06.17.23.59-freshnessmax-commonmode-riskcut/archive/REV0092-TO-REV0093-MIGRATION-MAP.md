# rev0092 to rev0093 migration map

## Compatibility

rev0093 is wire/core compatible with rev0092. The six-field TimeState model is unchanged.

## Validator behavior changes

Archives that passed rev0092 can fail rev0093 when current-use supporting observations are temporally after the evaluation or publication event that consumes them.

New fail-closed checks:

```text
anchor_evaluation.checkpoint_consistency.checked_at <= anchor_evaluation.evaluated_at
witness_cohort_evaluation.observed_at <= anchor_evaluation.evaluated_at
transparency_trust_policy_reference.lifecycle_status.revocation_check.checked_at <= lifecycle_status.evaluated_at
transparency_trust_policy_reference.lifecycle_status.drift_status.checked_at <= lifecycle_status.evaluated_at
aggregate_correction_authority_lifecycle_rollup.rollup_window.end <= aggregate_record_created_at / issued_at
```

## Files added

```text
AUDIT-2026.06.12-rev0093.md
archive/REV0092-TO-REV0093-MIGRATION-MAP.md
archive/REV0093-AUDIT-TEMPORAL-COHERENCE-REFACTOR.md
examples/negative/replay-transparency-checkpoint-after-evaluation-invalid.json
examples/negative/replay-transparency-witness-after-evaluation-invalid.json
examples/negative/transparency-policy-lifecycle-revocation-after-evaluation-invalid.json
examples/negative/transparency-policy-lifecycle-drift-after-evaluation-invalid.json
examples/negative/aggregate-lifecycle-rollup-window-after-artifact-invalid.json
```

## Files materially changed

```text
tools/temporal_coherence.py
tools/validate_archive.py
tests/semantic-test-vectors.yaml
README.md
START_HERE.md
INDEX.md
VALIDATION-REPORT.md
REVISION-RECEIPT.json
frontier-ticket.json
CHANGELOG.md
```
