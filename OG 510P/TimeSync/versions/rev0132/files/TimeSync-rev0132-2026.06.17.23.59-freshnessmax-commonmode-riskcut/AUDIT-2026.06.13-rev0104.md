# TimeSync rev0104 audit — assessment temporal validity refactor

rev0104 continues FT-0090 with executable validation work only. The pass focuses on local profile assessments because they are the place where TimeSync turns a TimeState plus profile evaluation into local actionability.

## Risk found

rev0103 already checked many cross-surface timestamp relationships, but local profile assessments still had a narrow hole: `policy_acceptance.checked_at` and `validity_horizon.evaluated_at` could predate `assessment_time` without a dedicated semantic failure.

That matters because a consumer could read the profile assessment as actionable even though the local policy or validity decision was checked before the assessment existed. The archive already required equality between `validity_horizon.evaluated_at` and `policy_acceptance.checked_at` when both are present, but it did not explicitly order either against `assessment_time`.

A second related gap was `assessment_time_binding: profile_assessment_time`. The field said the validity horizon was bound to the profile assessment time, but validation did not prove that `assessment_time` actually fell inside `not_before` / `not_after`.

## Change made

Added `tools/assessment_temporal.py` and wired it into `check_local_assessed_state`.

The new helper rejects:

```text
profile assessment assessment_time > policy_acceptance.checked_at
profile assessment assessment_time > validity_horizon.evaluated_at
validity_horizon.not_before > profile assessment assessment_time when assessment_time_binding is profile_assessment_time
profile assessment assessment_time > validity_horizon.not_after when assessment_time_binding is profile_assessment_time
```

It also moved the existing policy-acceptance and validity-horizon checks out of `tools/validate_archive.py`, reducing the validator's ownership of local assessment actionability logic.

## New fixtures

Added three derivation-checked negative fixtures:

```text
examples/negative/local-assessment-policy-check-before-assessment-invalid.json
examples/negative/local-assessment-validity-evaluated-before-assessment-invalid.json
examples/negative/local-assessment-profile-time-before-validity-window-invalid.json
```

Added semantic vectors:

```text
TV-N279
TV-N280
TV-N281
```

The semantic test suite now has 300 vectors.

## Non-goals

rev0104 does not make policy acceptance a source of TimeState provenance, traceability, transport authentication, freshness, profile digest binding, or profile evidence. It only prevents stale local actionability checks from qualifying an assessment that was not yet made.

FT-0090 remains open for selective validator decomposition and fixture-family derivation.
