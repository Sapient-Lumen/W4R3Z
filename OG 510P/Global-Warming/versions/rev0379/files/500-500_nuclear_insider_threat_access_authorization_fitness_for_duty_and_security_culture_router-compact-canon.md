---
id: '500'
title: Nuclear insider threat, access authorization, fitness-for-duty, and security culture router
object_type: integrity_gate
domain_tags:
- nuclear_energy
- physical_security
- nuclear_security
- design_basis_threat
- insider_threat
- transport_security
- drone_security
- security_safe_publication
service_floor:
- nuclear_insider_mitigation_program
- nuclear_access_authorization_program
- nuclear_fitness_for_duty_security
- nuclear_behavioral_observation
- nuclear_security_culture_self_assessment
- nuclear_escort_and_visitor_control
hazard_tags: &id001
- insider_threat
- access_authorization_failure
- fitness_for_duty_failure
- behavioral_observation_gap
- contractor_access_gap
- security_culture_erosion
clock_tags:
- access_authorization_refresh_cycle
- behavioral_observation_training_cycle
- fitness_for_duty_review_cycle
- security_culture_self_assessment_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_physical_security_manager
- A_security_force
- A_human_resources_officer
- A_contractor
instrument_tags: &id002
- access_authorization_program
- insider_mitigation_program
- fitness_for_duty_program
- behavioral_observation_training
- security_culture_self_assessment
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '421'
- '422'
- '423'
- '428'
- '429'
- '430'
- '441'
- '493'
- '498'
- '499'
- '501'
- '502'
- '503'
source_ids:
- S925
- S932
- S933
- S934
- S937
upstream_dependencies:
- nuclear_policy_preference
- physical_security_program
- public_assurance_evidence
- security_safe_publication_boundary
downstream_consequences:
- physical_security_caps_nuclear_maturity
- pro_nuclear_preference_becomes_security_assured
- sensitive_information_is_controlled_not_published
equity_lenses:
- host_communities
- workers
- critical_service_users
- future_generations
- public_auditors
degraded_modes: *id001
evidence_grade: control_plane_template_with_official_guidance_sources
speculation_level: low_for_gate_design_high_for_project_specific_readiness_until_localized
revision_added: rev0303
status: canon
bottlenecks:
- classified_or_security_sensitive_evidence
- security_workforce_depth
- regulator_review_capacity
- law_enforcement_coordination
- public_redaction_boundary
failure_modes: *id001
proof_ledgers: *id002
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_physical_security_gate_evaluation
- security_sensitive_publication_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_framework_sensitive_local_details_redacted
nuclear_policy_orientation: favored_with_physical_security_insider_drone_transport_gates
---

# 500 — Nuclear insider threat, access authorization, fitness-for-duty, and security culture router

## Function

This router makes the human-security layer of nuclear expansion explicit: unescorted access, contractor/vendor access, insider mitigation, behavioral observation, fitness for duty, and security culture must be auditable without exposing personal or protected details.

## Nuclear-positive rule

Prefer nuclear only where the trusted-workforce system is strong enough to prevent false confidence in guarded facilities. Expansion, restarts, uprates, SMRs, and fuel-cycle facilities cannot rise above template maturity if insider and access controls are stale or non-reviewable.

## Control-plane effect

Rev0303 creates a separate insider/access/security-culture evidence plane so security is not collapsed into generic workforce or cybersecurity tables.

## Evidence burden

Minimum evidence includes access-authorization procedures, trustworthiness/reliability determinations, contractor/vendor access governance, insider mitigation, fitness-for-duty integration, behavioral observation refreshers, and periodic nuclear security culture assessment. Sources: [S925]; [S932]; [S933]; [S934]; [S937].
