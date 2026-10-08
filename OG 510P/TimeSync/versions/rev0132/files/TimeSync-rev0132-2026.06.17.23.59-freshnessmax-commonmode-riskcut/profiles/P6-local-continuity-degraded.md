# P6-local-continuity-degraded — rev0132 profile map

## Purpose

Disconnected, partitioned, or survival-mode operation where local coherence may matter even without external traceability.

## Dominant pressure

Regime, freshness, holdover behavior, and validity scope.

## Obligations

```text
required_items: timestate
profile_default_items: clock_continuity_posture, validity_horizon
requestable_items: validity_scope, holdover_class, boundary_context, traceability_posture, timescale_realization, source_diversity_posture, pnt_risk_posture
```

## Profile-local applicability labels

- `diagnostic_local_only` — rank 0: Troubleshooting only.
- `local_display` — rank 10: Local display or operator awareness without external traceability claim.
- `partition_local_coordination` — rank 20: Coordination only inside the stated partition or validity scope.
- `local_continuity_operations` — rank 30: Profile-local continuity operation inside an explicitly bounded scope.

## Fallback mappings

- `local_continuity_operations` -> `partition_local_coordination` when `external_reference_lost_but_partition_scope_known`; boundary_context_required=true
- `partition_local_coordination` -> `local_display` when `validity_scope_or_holdover_class_unknown`; boundary_context_required=true
- `local_display` -> `diagnostic_local_only` when `state_not_safe_for_operator_display`; boundary_context_required=false

## Reference policy

```text
minimum_export_tier: 2
digest_required_when: cross_partition_replay, retained_degraded_operation_log
signed_binding_required_when: 
```

## Evidence policy

```text
summary_item_name: evaluator_evidence_summary
default_visibility: requestable
retention_required: False
retention_required_when: cross_partition_replay, retained_degraded_operation_log
profile_default_when: current_actionability_or_replay_boundary
minimum_summary_items: timestate.interval, timestate.timescale, timestate.freshness, timestate.regime, timestate.source_posture, timestate.applicability, assessment.assessed_profile, assessment.profile_conformance, assessment.applicability, validity_scope, holdover_class, boundary_context, assessment.validity_horizon
classes_that_cannot_satisfy_profile_obligations: unauthenticated_source_claim, external_evidence_reference, authorized_verifier_disclosure, replay_transparency_receipt, witness_cohort_summary, transparency_trust_policy_reference, lifecycle_authority_rotation_summary, lifecycle_authority_recovery_attestation, recovery_audit_rollup_summary, aggregate_privacy_control_summary, aggregate_revision_lineage_summary, aggregate_correction_authority_summary, aggregate_correction_authority_lifecycle_summary, portable_digest_binding_policy_summary, scope_composition_guard_summary, retained_prior_assessment, transport_metadata_only, not_observed
```

Evidence summaries remain compact item/class/obligation records. Redacted, replay-transparency, trust-policy, lifecycle-authority, recovery-rollup, and aggregate privacy-control and aggregate revision-lineage summaries may document external review, publication safety, correction lineage, or replay-visibility posture, but none of those surfaces exports salts/preimages, identities, rosters, proof material, policy language, privacy-budget internals, noise parameters, suppressed deltas, individual result identifiers, incident forensics, or gossip transcripts in ordinary summaries, satisfies profile obligations, or interprets external provenance.

## Normative rule digest

```text
sha256:ab2e9834905a3872741750c610d1df833cccf511d1e7a76f131b6ca4a8c506c9
```

This digest binds the normative profile rules represented by this profile map, not the rendered markdown file.


rev0088 evidence-policy note: `portable_digest_binding_policy_summary` is non-satisfying profile-obligation evidence and may only constrain digest-binding or discovery interpretation.


rev0088 compatibility-drift note: rendered profile summaries are checked against the normative catalog so non-satisfying evidence classes cannot silently disappear from human-facing profile maps.

rev0088 scope-composition note: `scope_composition_guard_summary` is non-satisfying profile-obligation evidence and may only constrain mixed-layer compatibility, discovery, lifecycle, and replay-transparency interpretation.
