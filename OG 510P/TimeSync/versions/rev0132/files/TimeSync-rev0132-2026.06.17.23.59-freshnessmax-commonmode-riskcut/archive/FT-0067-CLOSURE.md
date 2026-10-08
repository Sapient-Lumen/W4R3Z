# FT-0067 closure — validity horizon and current actionability

Closed in rev0068.

## Decision

Add `profile_assessments[*].validity_horizon` as a profile-assessment-scoped object.

The field is not a TimeState core field and not an extension hook. Current actionability is profile-specific and policy-specific: the same TimeState can be record-only for one profile, actionable for another, and unsatisfied for a third.

## Why

rev0067 could say that a profile assessment was bound to evidence and retained correctly, but it could not say whether the assessment was still usable for action at the evaluator's policy-check time. It also lacked an explicit guard against treating `export_context.exported_at` as renewed timing freshness.

## Guardrails

- Export time is never freshness.
- Retention context alone does not make an assessment actionable.
- Validity horizon is a compact decision surface, not a policy engine.
- The field binds to profile assessment and policy check time, not to transport.

## Validator-backed rules

- `current_actionability` must match `policy_acceptance.actionability` when both are present.
- `evaluated_at` must match `policy_acceptance.checked_at` when both are present.
- Actionable/conditional horizons must include `not_after` and be inside the validity window at `evaluated_at`.
- `used_as_freshness_basis` for export time is rejected.
- Discovery-returned validity horizons are schema and semantic checked.
