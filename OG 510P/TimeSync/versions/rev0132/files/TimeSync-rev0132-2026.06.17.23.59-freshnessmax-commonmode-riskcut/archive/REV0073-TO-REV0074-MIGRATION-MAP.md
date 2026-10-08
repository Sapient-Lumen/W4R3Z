# Migration map — rev0073 to rev0074

## Machine-readable additions

- `schema/replay-transparency-audit.schema.json`
  - Added optional `witness_cohort_evaluation`.
  - Added optional `aggregate_summary.monitor_cohort_coverage`.
  - Added transparency-boundary flags for witness/monitor roster, identity, gossip, and provenance leakage.
- `evaluator/evidence-class-catalog.json`
  - Added `witness_cohort_summary` with `may_satisfy_profile_obligation: false`.
- `profiles/profile-catalog.json` and `profiles/applicability/*.json`
  - Added `witness_cohort_summary` to each profile's forbidden obligation evidence classes.
  - Regenerated normative profile digests.

## New fixtures

Positive:

```text
examples/evaluator/replay-transparency-receipt-p3-witnessed.json
examples/evaluator/aggregate-verifier-audit-summary-p3-monitor-cohort.json
```

Negative:

```text
examples/negative/replay-transparency-witness-count-threshold-invalid.json
examples/negative/replay-transparency-witness-disagreement-current-invalid.json
examples/negative/replay-transparency-witness-roster-leak-invalid.json
examples/negative/aggregate-monitor-cohort-small-group-unsuppressed-invalid.json
examples/negative/evidence-summary-witness-cohort-obligation-invalid.json
examples/negative/discovery-replay-transparency-witness-cohort-malformed-invalid.json
```

## Compatibility

Existing rev0073 replay-transparency records remain conceptually valid if they omit `witness_cohort_evaluation`; the field is optional. Records that include witness/monitor posture must satisfy rev0074 leakage and threshold rules.

Profile normative digests changed because the forbidden evidence-class set is normative.
