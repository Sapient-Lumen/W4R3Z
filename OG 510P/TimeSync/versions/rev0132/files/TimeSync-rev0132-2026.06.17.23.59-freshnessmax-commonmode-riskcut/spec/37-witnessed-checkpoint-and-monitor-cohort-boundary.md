# 37 — Witnessed-checkpoint and monitor-cohort boundary

## Purpose

rev0073 can say whether a replay-transparency anchor was fresh, checkpoint-consistent, and free of an observed split-view signal. It deliberately does not say whether the checkpoint was independently witnessed or observed by a monitor cohort.

rev0074 adds a compact summary for that boundary.

The new fields are review posture only:

```text
challenge_replay_transparency_receipt.witness_cohort_evaluation
aggregate_verifier_audit_summary.aggregate_summary.monitor_cohort_coverage
```

They do not turn TimeSync into a witness protocol, gossip protocol, monitor registry, transparency log, Merkle proof format, external authorization system, audit chain, or provenance graph.

## Witness/cohort evaluation

`witness_cohort_evaluation` MAY appear on a `challenge_replay_transparency_receipt`.

It summarizes:

```text
status
basis
observed_at
cohort_independence
split_view_signal
proof_boundary
```

The allowed status values are intentionally coarse:

```text
not_used
witnessed_consistent
monitor_cohort_observed
combined_witness_and_monitor_consistent
insufficient_independent_observation
witness_or_monitor_disagreement_observed
not_checked
unknown
```

A consistent witness/monitor status means only that the replay-transparency posture had a summarized independent-observation basis at the declared evaluation boundary. It does not mean the underlying TimeState was traceable, fresh, diverse, valid, or actionable.

## Cohort independence

The independence summary is threshold posture, not a roster:

```text
status: independent_threshold_met | same_operator_or_same_root | insufficient_or_unknown | not_assessed | not_applicable
assessment_basis: policy_commitment | verifier_private_record | external_monitor_report | aggregate_audit_summary | not_applicable
reported_witness_count: integer
reported_monitor_count: integer
threshold: integer
roster_exported: false
identity_exported: false
dependency_details_exported: false
```

If a receipt claims `witnessed_consistent`, `monitor_cohort_observed`, or `combined_witness_and_monitor_consistent`, the validator requires:

```text
observed_at present
anchor_evaluation.checkpoint_consistency.status == checked_consistent
cohort_independence.status == independent_threshold_met
positive threshold
reported counts meeting the threshold required by the claimed status
```

For `combined_witness_and_monitor_consistent`, both witness and monitor counts must be nonzero and their sum must meet the threshold.

## Split-view and disagreement boundary

A witness or monitor disagreement is a replay-visibility signal only.

If `witness_cohort_evaluation.status` is `witness_or_monitor_disagreement_observed`, or if `split_view_signal.status` is `disagreement_observed`, then the receipt cannot claim `anchor_evaluation.current_visibility_status == current_at_evaluation`.

The exported record may say that a disagreement signal exists. It MUST NOT export:

```text
conflict internals
witness identities
monitor identities
gossip transcripts
witness signatures or countersignature material
monitor logs
dependency details
external provenance interpretation
```

## Aggregate monitor-cohort coverage

`aggregate_summary.monitor_cohort_coverage` MAY appear on `aggregate_verifier_audit_summary`.

It is a privacy-preserving coverage summary, not a monitor registry:

```text
coverage_status
coverage_basis
minimum_group_size
monitor_observation_count
witness_observation_count
small_group_suppressed
monitor_roster_exported: false
monitor_identity_exported: false
cohort_details_exported: false
gossip_transcripts_exported: false
```

If the sum of monitor and witness observations is below `minimum_group_size`, the aggregate summary must suppress the small group. `reported_aggregate` coverage cannot be used for a below-threshold group.

## Evidence-class rule

rev0074 adds `witness_cohort_summary` to the evidence class catalog:

```text
may_satisfy_profile_obligation: false
may_appear_in_exported_summary: true
```

A witness/cohort summary may support replay-transparency review. It cannot satisfy profile obligations and cannot upgrade traceability, freshness, source diversity, profile conformance, validity horizon, current actionability, transport authentication, verifier authorization, or TimeSync provenance.

## Discovery

Discovery may return replay-transparency records that include witness/cohort posture. Returned records are nested-validated as `replay-transparency-audit` objects.

Malformed witness/cohort posture inside a returned `replay_transparency_receipt` causes discovery semantic validation to fail.

## Non-goals

TimeSync does not define:

```text
witness key formats
witness rosters
monitor identities
monitor enrollment or authorization
gossip transcripts
Merkle proof encodings
threshold-signature schemes
log federation
external transparency-log trust anchors
legal authority for verifier or monitor access
policy equivalence between witness cohorts
```

Those may be important external systems. TimeSync records only the compact review posture needed to avoid misleading replay-transparency interpretation.
