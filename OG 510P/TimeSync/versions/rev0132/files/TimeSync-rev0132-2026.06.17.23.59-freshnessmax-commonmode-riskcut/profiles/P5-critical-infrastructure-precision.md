# P5-critical-infrastructure-precision — rev0132 profile map

## Purpose

Power, synchrophasor, and other critical-infrastructure timing contexts where known time quality, traceability, and warnings affect monitoring or control.

## Dominant pressure

Honest quality state at the live measurement/control boundary.

## Obligations

```text
required_items: timestate
profile_default_items: traceability_posture, sync_dimension, timescale_realization, clock_continuity_posture, source_diversity_posture, validity_horizon
requestable_items: boundary_context, holdover_class, validity_scope, time_error_bound, policy_acceptance, pnt_risk_posture
```

## Profile-local applicability labels

- `diagnostic_local_only` — rank 0: Local diagnostic observation only.
- `monitoring_only` — rank 10: May support monitoring but not protection or control action.
- `protected_monitoring` — rank 20: May support profile-local high-integrity monitoring where timing-quality obligations are met.
- `control_or_protection` — rank 30: May support profile-local control/protection use where all required timing-quality and traceability conditions are met.

## Fallback mappings

- `control_or_protection` -> `monitoring_only` when `discipline_loss_or_quality_degradation`; boundary_context_required=true
- `protected_monitoring` -> `monitoring_only` when `traceability_or_quality_obligation_missing`; boundary_context_required=true
- `monitoring_only` -> `diagnostic_local_only` when `state_unknown_or_expired`; boundary_context_required=false

## Reference policy

```text
minimum_export_tier: 3
digest_required_when: safety_or_compliance_retention, cross_boundary_control_evidence
signed_binding_required_when: independent_profile_binding_verification
```

## Evidence policy

```text
summary_item_name: evaluator_evidence_summary
default_visibility: retention_only
retention_required: True
retention_required_when: safety_or_compliance_retention, cross_boundary_control_evidence
profile_default_when: control_boundary_export, common_mode_dependency_visibility_required, current_actionability_or_replay_boundary, pnt_disruption_or_manipulation_risk_boundary
minimum_summary_items: timestate.interval, timestate.timescale, timestate.freshness, timestate.regime, timestate.source_posture, timestate.applicability, assessment.assessed_profile, assessment.profile_conformance, assessment.applicability, extension_hooks.traceability_posture, extension_hooks.sync_dimension, profile.fallback_mappings, boundary_context, policy_acceptance, extension_hooks.timescale_realization, extension_hooks.clock_continuity_posture, extension_hooks.source_diversity_posture, assessment.validity_horizon
classes_that_cannot_satisfy_profile_obligations: unauthenticated_source_claim, external_evidence_reference, authorized_verifier_disclosure, replay_transparency_receipt, witness_cohort_summary, transparency_trust_policy_reference, lifecycle_authority_rotation_summary, lifecycle_authority_recovery_attestation, recovery_audit_rollup_summary, aggregate_privacy_control_summary, aggregate_revision_lineage_summary, aggregate_correction_authority_summary, aggregate_correction_authority_lifecycle_summary, portable_digest_binding_policy_summary, scope_composition_guard_summary, retained_prior_assessment, transport_metadata_only, not_observed
```

Evidence summaries remain compact item/class/obligation records. Redacted, replay-transparency, trust-policy, lifecycle-authority, recovery-rollup, and aggregate privacy-control and aggregate revision-lineage summaries may document external review, publication safety, correction lineage, or replay-visibility posture, but none of those surfaces exports salts/preimages, identities, rosters, proof material, policy language, privacy-budget internals, noise parameters, suppressed deltas, individual result identifiers, incident forensics, or gossip transcripts in ordinary summaries, satisfies profile obligations, or interprets external provenance.

## Normative rule digest

```text
sha256:005a7bbcc67b9b092d40944de855835e0c78af0546e2535dc791f3ec0543a803
```

This digest binds the normative profile rules represented by this profile map, not the rendered markdown file.


rev0088 evidence-policy note: `portable_digest_binding_policy_summary` is non-satisfying profile-obligation evidence and may only constrain digest-binding or discovery interpretation.


rev0088 compatibility-drift note: rendered profile summaries are checked against the normative catalog so non-satisfying evidence classes cannot silently disappear from human-facing profile maps.

rev0088 scope-composition note: `scope_composition_guard_summary` is non-satisfying profile-obligation evidence and may only constrain mixed-layer compatibility, discovery, lifecycle, and replay-transparency interpretation.
