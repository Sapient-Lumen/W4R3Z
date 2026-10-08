---
id: '513'
title: Nuclear emergency preparedness scorecard, EPZ public notification, and maturity-cap audit
object_type: integrity_gate
domain_tags:
- nuclear_energy
- nuclear_emergency_preparedness
- radiological_emergency_response
- epz_planning
- public_safety
- civil_protection
- nuclear_public_trust
service_floor:
- nuclear_emergency_public_information_center
- nuclear_reentry_relocation_recovery_decision
- nuclear_emergency_compensation_claims_access
- nuclear_epz_data_quality_demographic_update
- nuclear_emergency_preparedness_maturity_cap
- nuclear_protective_action_counterevidence_ledger
hazard_tags:
- public_information_failure
- reentry_confusion
- recovery_inequity
- compensation_access_failure
- epz_data_staleness
- counterevidence_unclosed
clock_tags:
- public_information_refresh_cycle
- reentry_relocation_review_cycle
- claims_access_test_cycle
- epz_data_quality_audit_cycle
actor_tags:
- A_public_information_officer
- A_recovery_authority
- A_public_auditor
- A_civil_rights_officer
- A_community_monitoring_board
- A_claims_administrator
instrument_tags:
- emergency_preparedness_scorecard
- public_information_center_protocol
- reentry_relocation_decision_matrix
- claims_access_pathway
- epz_data_quality_audit
- maturity_cap_execution
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '421'
- '422'
- '423'
- '424'
- '426'
- '428'
- '429'
- '430'
- '443'
- '489'
- '493'
- '498'
- '503'
- '504'
- '505'
- '506'
- '507'
- '508'
- '509'
- '510'
- '511'
- '512'
source_ids:
- S953
- S954
- S955
- S956
- S957
- S958
- S959
- S960
- S961
- S962
- S963
- S964
- S965
- S966
upstream_dependencies:
- nuclear_policy_preference
- radiological_monitoring_program
- physical_security_program
- climate_resilience_program
- civil_rights_language_access
downstream_consequences:
- emergency_preparedness_caps_nuclear_maturity
- pro_nuclear_preference_becomes_public_safety_assured
- public_acceptance_depends_on_exercised_response_pathways
equity_lenses:
- host_communities
- children
- pregnant_people
- disabled_people
- older_adults
- carless_households
- limited_english_proficiency_households
- long_term_care_residents
- hospital_patients
- workers
- schools
- rural_households
- tribal_communities
degraded_modes:
- public_information_failure
- reentry_confusion
- recovery_inequity
- compensation_access_failure
- epz_data_staleness
- counterevidence_unclosed
evidence_grade: control_plane_template_with_official_guidance_sources
speculation_level: low_for_gate_design_high_for_project_specific_readiness_until_localized
revision_added: rev0305
status: canon
bottlenecks:
- offsite_response_capacity
- public_alert_reach
- evacuation_transportation_capacity
- medical_surge_capacity
- ki_decision_communications
- after_action_closure
failure_modes:
- public_information_failure
- reentry_confusion
- recovery_inequity
- compensation_access_failure
- epz_data_staleness
- counterevidence_unclosed
proof_ledgers:
- emergency_preparedness_scorecard
- public_information_center_protocol
- reentry_relocation_decision_matrix
- claims_access_pathway
- epz_data_quality_audit
- maturity_cap_execution
- emergency_preparedness_gap_backlog
- emergency_preparedness_traceability_matrix
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_emergency_preparedness_gate_evaluation
- exercise_after_action_closure_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_preparedness_framework_sensitive_security_personal_and_route_details_redacted
nuclear_policy_orientation: favored_with_emergency_preparedness_epz_ki_evacuation_medical_and_recovery_gates
---

# 513 — Nuclear emergency preparedness scorecard, EPZ public notification, and maturity-cap audit

## Function

This audit file makes emergency preparedness a public-facing scorecard and maturity cap: nuclear remains favored, but not where public instructions, reentry, relocation, claims access, EPZ data, or counterevidence are unreviewable.

## Nuclear-positive rule

Prefer nuclear where emergency preparedness is exercised, inclusive, medically realistic, publicly intelligible, and recoverable. Do not credit nuclear maturity where public alerting, protective-action pathways, KI/medical countermeasure decisions, evacuation/shelter access, ingestion-pathway controls, drills, corrective actions, or recovery/claims pathways remain template-only.

## Control-plane effect

This file adds emergency-preparedness evidence as a hard maturity cap. Local/project evidence must close the relevant gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `emergency_preparedness_scorecard`
- `public_information_center_protocol`
- `reentry_relocation_decision_matrix`
- `claims_access_pathway`
- `epz_data_quality_audit`
- `maturity_cap_execution`

## Source boundary

The source IDs in this file support emergency-preparedness gate design. They do not certify any real plant, EPZ, alert system, evacuation route, KI inventory, medical capacity, drill result, after-action closure, recovery claim, or public notification without local evidence.
