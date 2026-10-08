# 31 — Profile assessment validity horizon and current actionability — rev0068

## Purpose

A TimeState says what time interval, timescale, freshness posture, regime, source posture, and applicability were assessed. A retained export says when a record was exported. Neither of those answers the profile-specific question:

```text
Is this assessed profile conclusion usable for action at the evaluator's policy-check time?
```

rev0068 closes FT-0067 by adding `profile_assessments[*].validity_horizon`.

This field is deliberately profile-assessment scoped. It is not part of the six-field TimeState core and it is not an extension hook shared by all profile assessments on the same TimeState. Two profiles may legitimately reach different actionability conclusions over the same TimeState.

## Shape

```json
{
  "evaluated_at": "2026-05-21T07:35:00Z",
  "not_before": "2026-05-21T07:34:59Z",
  "not_after": "2026-05-21T07:35:01Z",
  "current_actionability": "actionable | conditional | record_only | not_actionable | unknown",
  "basis": "profile_policy | local_policy | freshness | holdover_model | retention_context | operator_configuration | unknown",
  "assessment_time_binding": "profile_assessment_time | timestate_interval | freshness_state | holdover_model | policy_defined | historical_record_only | unknown",
  "export_time_role": "not_used | record_timestamp_only | used_as_freshness_basis",
  "evidence_posture": "claimed | assessed | profile_defined | redacted | unknown"
}
```

## Normative constraints

- `validity_horizon` belongs to a profile assessment, not to the TimeState core.
- `current_actionability` MUST match `policy_acceptance.actionability` when both are present.
- `evaluated_at` MUST match `policy_acceptance.checked_at` when both are present.
- `not_before` MUST NOT be after `not_after`.
- `actionable` and `conditional` horizons require `not_after`.
- `actionable` and `conditional` conclusions MUST NOT be outside the stated validity window at `evaluated_at`.
- `export_time_role: used_as_freshness_basis` MUST be rejected. Export time can document carriage or retention, but it cannot refresh an assessment.
- `basis: retention_context` alone MUST NOT make an assessment actionable.

## Profile placement

```text
P1: requestable
P2: profile-default
P3: profile-default
P4: requestable
P5: profile-default
P6: profile-default
```

P2 needs this for coordination/lease-style decisions. P3 and P5 need it for retained or regulated replay review. P6 needs it because degraded or partition-local operation often depends on holdover windows. P1 and P4 keep it requestable because their default concerns are usually logging and synchronization characterization rather than per-assessment action authorization.

## Evidence class

rev0068 adds `validity_horizon_summary` to the evaluator evidence class catalog. It can satisfy a `validity_horizon` obligation, but it remains a compact summary of the decision basis. It is not a policy engine, audit log, clock algorithm, or proof of continued validity after `evaluated_at`.

## Boundary

A retained record may remain useful as a historical fact while being non-actionable for new decisions. A fresh export may carry a stale assessment. A current policy check may reject an old assessment even when the original profile conformance was satisfied. These are different facts and must not be collapsed.
