# P1-general-computing — rev0132 profile map

## Purpose

Routine host, application, logging, authentication, and user-facing time uses.

## Dominant pressure

Avoid false precision and stale time while keeping the model lightweight.

## Obligations

```text
required_items: timestate
profile_default_items: 
requestable_items: traceability_posture, boundary_context, holdover_class, timescale_realization, clock_continuity_posture, source_diversity_posture, validity_horizon
```

## Profile-local applicability labels

- `diagnostic_local_only` — rank 0: Local troubleshooting only; not exported as a basis for ordinary decisions.
- `display_time` — rank 10: User-facing or approximate display where precision, traceability, and ordering are not relied upon.
- `coarse_logging` — rank 20: General application or host logs where coarse order is useful but regulated/audit semantics are not claimed.
- `security_sensitive_time` — rank 30: Authentication, token, or policy decisions that rely on bounded current time.

## Fallback mappings

- `security_sensitive_time` -> `coarse_logging` when `freshness_or_traceability_not_sufficient_for_security_use`; boundary_context_required=false
- `coarse_logging` -> `display_time` when `uncertainty_or_staleness_too_large_for_log_ordering`; boundary_context_required=false
- `display_time` -> `diagnostic_local_only` when `state_not_safe_for ordinary user-facing display`; boundary_context_required=false

## Reference policy

```text
minimum_export_tier: 1
digest_required_when: retained_for_audit, detached_from_configured_boundary
signed_binding_required_when: 
```

## Evidence policy

```text
summary_item_name: evaluator_evidence_summary
default_visibility: requestable
retention_required: False
retention_required_when: retained_for_audit, detached_from_configured_boundary
profile_default_when: 
minimum_summary_items: timestate.interval, timestate.timescale, timestate.freshness, timestate.regime, timestate.source_posture, timestate.applicability, assessment.assessed_profile, assessment.profile_conformance, assessment.applicability, profile.required_items
classes_that_cannot_satisfy_profile_obligations: unauthenticated_source_claim, external_evidence_reference, authorized_verifier_disclosure, replay_transparency_receipt, witness_cohort_summary, transparency_trust_policy_reference, lifecycle_authority_rotation_summary, lifecycle_authority_recovery_attestation, recovery_audit_rollup_summary, aggregate_privacy_control_summary, aggregate_revision_lineage_summary, aggregate_correction_authority_summary, aggregate_correction_authority_lifecycle_summary, portable_digest_binding_policy_summary, scope_composition_guard_summary, retained_prior_assessment, transport_metadata_only, not_observed
```

Evidence summaries remain compact item/class/obligation records. Redacted, replay-transparency, trust-policy, lifecycle-authority, recovery-rollup, and aggregate privacy-control and aggregate revision-lineage summaries may document external review, publication safety, correction lineage, or replay-visibility posture, but none of those surfaces exports salts/preimages, identities, rosters, proof material, policy language, privacy-budget internals, noise parameters, suppressed deltas, individual result identifiers, incident forensics, or gossip transcripts in ordinary summaries, satisfies profile obligations, or interprets external provenance.

## Normative rule digest

```text
sha256:765e6ae445fbd35fd4979409ec9e4a40d138f16ba8bd994e757d35803453d197
```

This digest binds the normative profile rules represented by this profile map, not the rendered markdown file.


rev0088 evidence-policy note: `portable_digest_binding_policy_summary` is non-satisfying profile-obligation evidence and may only constrain digest-binding or discovery interpretation.


rev0088 compatibility-drift note: rendered profile summaries are checked against the normative catalog so non-satisfying evidence classes cannot silently disappear from human-facing profile maps.

rev0088 scope-composition note: `scope_composition_guard_summary` is non-satisfying profile-obligation evidence and may only constrain mixed-layer compatibility, discovery, lifecycle, and replay-transparency interpretation.
