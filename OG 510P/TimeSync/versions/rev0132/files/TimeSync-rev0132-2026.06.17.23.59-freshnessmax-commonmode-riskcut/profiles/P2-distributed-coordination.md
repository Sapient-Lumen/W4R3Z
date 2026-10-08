# P2-distributed-coordination — rev0132 profile map

## Purpose

Datacenter and distributed-system coordination where bounded uncertainty affects ordering, leases, transactions, or coordination safety.

## Dominant pressure

Interval semantics, freshness, regime, and explicit applicability for coordination-sensitive uses.

## Obligations

```text
required_items: timestate
profile_default_items: validity_horizon
requestable_items: boundary_context, traceability_posture, validity_scope, timescale_realization, clock_continuity_posture, source_diversity_posture
```

## Profile-local applicability labels

- `diagnostic_local_only` — rank 0: Troubleshooting state only; not usable for ordering, leases, or coordination decisions.
- `local_ordering_hint` — rank 10: May assist non-safety local ordering heuristics; not a correctness basis.
- `bounded_lease_coordination` — rank 20: Usable for profile-local lease or timeout coordination where interval/freshness obligations are met.
- `external_transaction_ordering` — rank 30: Usable for stronger transaction-ordering semantics defined by the profile.

## Fallback mappings

- `external_transaction_ordering` -> `bounded_lease_coordination` when `transaction_ordering_bound_not_met_but_lease_bound_met`; boundary_context_required=false
- `bounded_lease_coordination` -> `local_ordering_hint` when `freshness_or_uncertainty_exceeds_lease_bound`; boundary_context_required=true
- `local_ordering_hint` -> `diagnostic_local_only` when `partition_or_regime_unknown_for_coordination`; boundary_context_required=true

## Reference policy

```text
minimum_export_tier: 2
digest_required_when: detached_or_cross_operator_coordination
signed_binding_required_when: 
```

## Evidence policy

```text
summary_item_name: evaluator_evidence_summary
default_visibility: requestable
retention_required: False
retention_required_when: detached_or_cross_operator_coordination
profile_default_when: current_actionability_or_replay_boundary
minimum_summary_items: timestate.interval, timestate.timescale, timestate.freshness, timestate.regime, timestate.source_posture, timestate.applicability, assessment.assessed_profile, assessment.profile_conformance, assessment.applicability, profile.fallback_mappings, validity_scope, assessment.validity_horizon
classes_that_cannot_satisfy_profile_obligations: unauthenticated_source_claim, external_evidence_reference, authorized_verifier_disclosure, replay_transparency_receipt, witness_cohort_summary, transparency_trust_policy_reference, lifecycle_authority_rotation_summary, lifecycle_authority_recovery_attestation, recovery_audit_rollup_summary, aggregate_privacy_control_summary, aggregate_revision_lineage_summary, aggregate_correction_authority_summary, aggregate_correction_authority_lifecycle_summary, portable_digest_binding_policy_summary, scope_composition_guard_summary, retained_prior_assessment, transport_metadata_only, not_observed
```

Evidence summaries remain compact item/class/obligation records. Redacted, replay-transparency, trust-policy, lifecycle-authority, recovery-rollup, and aggregate privacy-control and aggregate revision-lineage summaries may document external review, publication safety, correction lineage, or replay-visibility posture, but none of those surfaces exports salts/preimages, identities, rosters, proof material, policy language, privacy-budget internals, noise parameters, suppressed deltas, individual result identifiers, incident forensics, or gossip transcripts in ordinary summaries, satisfies profile obligations, or interprets external provenance.

## Normative rule digest

```text
sha256:a703581ff9091ed961f9d27057e0e3775571b74860c60206dbe073a6edd7b679
```

This digest binds the normative profile rules represented by this profile map, not the rendered markdown file.


rev0088 evidence-policy note: `portable_digest_binding_policy_summary` is non-satisfying profile-obligation evidence and may only constrain digest-binding or discovery interpretation.


rev0088 compatibility-drift note: rendered profile summaries are checked against the normative catalog so non-satisfying evidence classes cannot silently disappear from human-facing profile maps.

rev0088 scope-composition note: `scope_composition_guard_summary` is non-satisfying profile-obligation evidence and may only constrain mixed-layer compatibility, discovery, lifecycle, and replay-transparency interpretation.
