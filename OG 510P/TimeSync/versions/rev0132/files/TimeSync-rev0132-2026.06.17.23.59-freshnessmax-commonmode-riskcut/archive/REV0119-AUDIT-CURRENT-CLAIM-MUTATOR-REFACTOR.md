# rev0119 audit — current-claim mutator refactor

## Scope

The audit re-ran mutation pressure against fields that preserve or weaken satisfied/current meaning: evidence-summary minimum items, profile conformance, policy actionability, validity-horizon actionability, and fallback metadata.

## Closed survivors

1. Satisfied evidence summaries no longer count stale `assessment.validity_horizon` minimum witnesses.
2. Unsatisfied profile conformance can no longer preserve actionable or conditional policy/validity-horizon actionability.
3. Satisfied or unsatisfied assessments can no longer retain `evaluation_summary.fallback_mapping` from a fallback path.
4. `policy_acceptance.status: accepted` can no longer carry conditional actionability.

## Refactor notes

The revision avoided a new registry. It tightened existing helpers:

- `tools/evidence_summary_semantics.py` now separates timeless assessment conclusion facts from current evidence inputs.
- `tools/assessment_temporal.py` owns the current-actionability guardrails for conformance and policy acceptance.
- `tools/validate_archive.py` keeps the profile-map-aware fallback metadata check because it already has the resolved profile map in scope.

## Remaining risk

The next risk is broader portability/current-use mutation pressure in detached challenge and replay chains. The audit should keep adding probes only when an exploratory mutation preserves a stronger claim, not when it merely downgrades a record to historical or explanatory use.
