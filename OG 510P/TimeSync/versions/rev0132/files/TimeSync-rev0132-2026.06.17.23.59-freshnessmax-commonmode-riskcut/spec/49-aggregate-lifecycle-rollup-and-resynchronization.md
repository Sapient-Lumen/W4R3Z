# 49 — Aggregate lifecycle rollup and emergency resynchronization

rev0085 closed FT-0084 by adding privacy-safe rollups for correction-authority lifecycle decisions, contestation resolution, emergency-withdrawal notification resynchronization, and lifecycle portability aggregation.

## Placement

The rollup is optional and aggregate-only:

```text
aggregate_summary.aggregate_correction_authority_lifecycle_rollup
```

It belongs to detached aggregate verifier audit summaries. It is not part of TimeState, local assessed state, profile assessment, individual challenge replay, or evaluator evidence satisfaction.

## Rollup shape

The rollup carries:

```text
rollup_version
rollup_window
current_interpretation_decision
lifecycle_population
decision_population
digest_bindings
emergency_resynchronization_summary
contestation_resolution_rollup
lifecycle_portability_aggregation
boundary
```

The important value is `current_interpretation_decision`, not a raw majority lifecycle state. The rollup outcome must remain safe when the population contains suppression states.

## Contestation-resolution rollup

The contestation rollup summarizes aggregate state classes such as pending, upheld, overturned, and unknown/redacted contestation. It may bind to a contestation-policy or decision-table digest, but it must not export contesting parties, legal process records, dispute evidence, reviewer identities, or exact incident timing.

Resolved-upheld contestation can coexist with current interpretation only after the local lifecycle decision table allows it and the contestation record is digest-bound. Resolved-overturned, pending, and unknown contestation suppress current interpretation.

## Emergency-withdrawal resynchronization

Emergency withdrawal suppresses current interpretation first. Resynchronization describes what happened after suppression without exposing response operations.

Allowed summary states include:

```text
not_applicable
withdrawal_active
resync_required
resync_in_progress
resync_completed
resync_failed
resync_contested
historical_after_resync
unknown_or_redacted
```

A concrete emergency withdrawal requires:

```text
withdrawal_digest
resynchronization_state
resynchronization_policy_digest when concrete
```

The rollup may expose count buckets and completion buckets, but not notification recipients, delivery channels, message payloads, response plans, incident forensics, authority identities, or exact incident windows.

## Lifecycle portability aggregation

Compatible-operator lifecycle aggregation is allowed only when digest-bound compatibility exists.

A portable lifecycle rollup requires a compatibility statement digest and an equivalent-or-stricter posture. Portability failure cannot coexist with a current-supported rollup decision.

## Boundary

The rollup may constrain aggregate replay-review posture only. It cannot become profile evidence, actionability evidence, source traceability, individual replay visibility, provenance, a monitor registry, or a cross-operator authority registry.
