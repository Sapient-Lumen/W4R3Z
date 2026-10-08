# rev0116 to rev0117 migration map

rev0117 is validation-compatible for existing valid rev0116 artifacts unless they relied on one of the newly rejected mutation-survivor seams.

## New rejection cases

- Local profile assessments with `profile_lifecycle_state` of `superseded`, `deprecated`, `revoked`, or `unknown` cannot carry actionable or conditional current actionability.
- Policy lifecycle-authority references with `compromise_response.state: none_known` must use `replay_visibility_effect: no_current_effect`.
- Aggregate lifecycle decision-table required row ids must retain their canonical row posture.
- Digest-binding policy rules for `retained_operator_record` cannot set `current_use_allowed: true`.

## New files

- `tools/aggregate_lifecycle_decision_semantics.py`
- `examples/negative/local-assessment-revoked-actionable-invalid.json`
- `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json`
- `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json`
- `examples/negative/digest-binding-policy-retained-current-invalid.json`
- `AUDIT-2026.06.13-rev0117.md`
- `archive/REV0117-AUDIT-LIFECYCLE-MUTATOR-ROWSEAL-REFACTOR.md`

## Validation delta

The semantic vector count increases from 342 to 346. The mutation-survivor probe count increases from 10 to 14.
