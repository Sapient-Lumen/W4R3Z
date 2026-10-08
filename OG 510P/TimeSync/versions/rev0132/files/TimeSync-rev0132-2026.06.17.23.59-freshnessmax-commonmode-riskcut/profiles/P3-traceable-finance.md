# P3-traceable-finance — rev0132 profile map

## Purpose

Financial timestamping and audit contexts where traceability, documented uncertainty, retention, and profile identity matter.

## Dominant pressure

Traceability and retained reconstruction.

## Obligations

```text
required_items: timestate, assessment_time, assessed_profile, profile_conformance
profile_default_items: traceability_posture, sync_dimension, timescale_realization, validity_horizon
requestable_items: boundary_context, policy_acceptance, validity_scope, clock_continuity_posture, source_diversity_posture
```

## Profile-local applicability labels

- `diagnostic_local_only` — rank 0: Internal troubleshooting only; not an audit timestamp.
- `internal_recordkeeping` — rank 10: Internal recordkeeping without regulated timestamp claim.
- `retained_audit_record` — rank 20: Historical retained record whose profile reference is reconstructable for audit review.
- `regulated_timestamping` — rank 30: Timestamping use that satisfies the active traceable-finance profile obligations.

## Fallback mappings

- `regulated_timestamping` -> `internal_recordkeeping` when `traceability_or_reference_obligation_missing`; boundary_context_required=false
- `retained_audit_record` -> `internal_recordkeeping` when `retention_reference_not_resolvable_under_current_policy`; boundary_context_required=false
- `internal_recordkeeping` -> `diagnostic_local_only` when `state_not_safe_for_local_records`; boundary_context_required=false

## Reference policy

```text
minimum_export_tier: 3
digest_required_when: retained, detached, regulated_export, audit_reconstruction
signed_binding_required_when: receiver_must_verify_profile_binding_issuer
```

## Evidence policy

```text
summary_item_name: evaluator_evidence_summary
default_visibility: retention_only
retention_required: True
retention_required_when: retained, detached, regulated_export, audit_reconstruction
profile_default_when: regulated_timestamping_export, current_actionability_or_replay_boundary
minimum_summary_items: timestate.interval, timestate.timescale, timestate.freshness, timestate.regime, timestate.source_posture, timestate.applicability, assessment.assessed_profile, assessment.profile_conformance, assessment.applicability, extension_hooks.traceability_posture, extension_hooks.sync_dimension, profile.required_items, profile.profile_default_items, policy_acceptance, extension_hooks.timescale_realization, assessment.validity_horizon
classes_that_cannot_satisfy_profile_obligations: unauthenticated_source_claim, external_evidence_reference, authorized_verifier_disclosure, replay_transparency_receipt, witness_cohort_summary, transparency_trust_policy_reference, lifecycle_authority_rotation_summary, lifecycle_authority_recovery_attestation, recovery_audit_rollup_summary, aggregate_privacy_control_summary, aggregate_revision_lineage_summary, aggregate_correction_authority_summary, aggregate_correction_authority_lifecycle_summary, portable_digest_binding_policy_summary, scope_composition_guard_summary, retained_prior_assessment, transport_metadata_only, not_observed
```

Evidence summaries remain compact item/class/obligation records. Redacted, replay-transparency, trust-policy, lifecycle-authority, recovery-rollup, and aggregate privacy-control and aggregate revision-lineage summaries may document external review, publication safety, correction lineage, or replay-visibility posture, but none of those surfaces exports salts/preimages, identities, rosters, proof material, policy language, privacy-budget internals, noise parameters, suppressed deltas, individual result identifiers, incident forensics, or gossip transcripts in ordinary summaries, satisfies profile obligations, or interprets external provenance.

## Normative rule digest

```text
sha256:285944567f5e5304e0ab637a6fb0ee1809095f53140ab2de006f56f0005d0397
```

This digest binds the normative profile rules represented by this profile map, not the rendered markdown file.


rev0088 evidence-policy note: `portable_digest_binding_policy_summary` is non-satisfying profile-obligation evidence and may only constrain digest-binding or discovery interpretation.


rev0088 compatibility-drift note: rendered profile summaries are checked against the normative catalog so non-satisfying evidence classes cannot silently disappear from human-facing profile maps.

rev0088 scope-composition note: `scope_composition_guard_summary` is non-satisfying profile-obligation evidence and may only constrain mixed-layer compatibility, discovery, lifecycle, and replay-transparency interpretation.
