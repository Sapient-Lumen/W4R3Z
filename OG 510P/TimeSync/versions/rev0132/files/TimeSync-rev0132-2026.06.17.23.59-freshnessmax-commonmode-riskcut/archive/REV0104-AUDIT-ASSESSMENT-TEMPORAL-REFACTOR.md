# rev0104 audit — assessment temporal validity refactor

## Why this was next

After rev0103, the major cross-surface replay, transport, digest, retained-export, aggregate, profile-compatibility, and policy-equivalence timestamp gaps had been reduced. The next riskiest remaining executable gap was closer to the core local assessment path: whether local actionability checks can qualify an assessment before the assessment exists.

## Implemented refactor

`tools/assessment_temporal.py` now owns:

```text
check_policy_acceptance
check_validity_horizon
check_profile_assessment_temporal
```

`tools/validate_archive.py` now delegates these checks when validating `local_assessed_state` profile assessments.

## New negative cases

```text
local-assessment-policy-check-before-assessment-invalid.json
local-assessment-validity-evaluated-before-assessment-invalid.json
local-assessment-profile-time-before-validity-window-invalid.json
```

All three are patch-derived from `examples/local-assessed-state-p3-satisfied.json` through `tests/fixture-derivations.yaml`, reducing copy-drift.

## What this does not do

This does not change the TimeState core, profile catalog, transport adapter catalog, evidence-class catalog, digest policy, or discovery vocabulary. It is a local profile-assessment consistency check.

## Remaining work

FT-0090 should remain open. Further work should keep the same bar: extract concern families only when it reduces executable drift, and add fixtures only when they guard a real stale-evidence or binding failure.
