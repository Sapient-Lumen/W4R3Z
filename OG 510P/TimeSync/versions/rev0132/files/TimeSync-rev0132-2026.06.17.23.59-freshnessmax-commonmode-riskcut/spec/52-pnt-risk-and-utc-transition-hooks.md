# 52 — PNT risk and UTC transition hooks

rev0086 sharpens extension hooks for critical-infrastructure and degraded-local-continuity profiles without expanding the six-field TimeState core.

## PNT risk posture

Placement:

```text
extension_hooks.pnt_risk_posture
```

The hook summarizes PNT disruption and manipulation risk posture for profiles that need it, especially P5 and P6.

It can carry:

```text
disruption_warning_posture
manipulation_suspected_posture
holdover_degradation_model_reference
dynamic_time_inaccuracy_reference
time_quality_mapping_reference
common_mode_failure_hypothesis
evidence_posture
export_detail
```

`export_detail` is `summary_only`. The hook does not export raw sensors, RF captures, source rosters, receiver internals, operator incident records, or timing algorithms.

A warning or suspected/confirmed manipulation posture should constrain profile-local actionability according to profile rules. It does not mutate TimeState and does not become universal conformance logic.

## UTC transition hooks

`timescale_realization` now has optional planning fields:

```text
utc_transition_policy_digest
leap_second_policy_epoch
ut1_utc_tolerance_class
smear_policy_digest
continuous_utc_transition_supported
mixed_realization_boundary
```

These fields let profiles distinguish standard UTC, smeared UTC, and future continuous UTC transition handling without putting leap policy into the TimeState core.

## Boundary

The hooks are profile/evidence-level. They do not add fields to TimeState, do not define a PNT monitoring system, do not define a UTC authority registry, and do not certify external timescale realization.

Profiles may require or request these hooks. Absence, unknown posture, or redaction is interpreted through the active profile map.
