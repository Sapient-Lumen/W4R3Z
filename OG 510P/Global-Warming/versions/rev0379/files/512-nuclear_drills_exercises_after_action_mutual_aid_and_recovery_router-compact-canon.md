---
id: '512'
title: Nuclear drills, exercises, after-action, mutual-aid, and recovery router
object_type: router
domain_tags:
- nuclear_energy
- nuclear_emergency_preparedness
- radiological_emergency_response
- epz_planning
- public_safety
- civil_protection
- nuclear_public_trust
service_floor:
- nuclear_long_term_care_healthcare_evacuation
- nuclear_pets_livestock_agriculture_continuity
- nuclear_emergency_drill_exercise_evaluation
- nuclear_after_action_corrective_action_closure
- nuclear_fema_nrc_onsite_offsite_coordination
- nuclear_mutual_aid_resource_typing
hazard_tags:
- exercise_theater
- after_action_nonclosure
- mutual_aid_unavailable
- healthcare_evacuation_failure
- animal_agriculture_continuity_gap
clock_tags:
- biennial_exercise_cycle
- after_action_closure_cycle
- mutual_aid_refresh_cycle
- healthcare_evacuation_rehearsal_cycle
actor_tags:
- A_fema
- A_nuclear_regulator
- A_state_emergency_management
- A_mutual_aid_coordinator
- A_healthcare_coalition
- A_agriculture_authority
instrument_tags:
- exercise_evaluation_report
- after_action_corrective_action_ledger
- mutual_aid_resource_typing
- healthcare_evacuation_drill
- animal_agriculture_continuity_plan
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
- '513'
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
- exercise_theater
- after_action_nonclosure
- mutual_aid_unavailable
- healthcare_evacuation_failure
- animal_agriculture_continuity_gap
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
- exercise_theater
- after_action_nonclosure
- mutual_aid_unavailable
- healthcare_evacuation_failure
- animal_agriculture_continuity_gap
proof_ledgers:
- exercise_evaluation_report
- after_action_corrective_action_ledger
- mutual_aid_resource_typing
- healthcare_evacuation_drill
- animal_agriculture_continuity_plan
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

# 512 — Nuclear drills, exercises, after-action, mutual-aid, and recovery router

## Function

This router turns exercises, after-action corrective closure, mutual aid, healthcare evacuation, animal/agriculture continuity, and FEMA/NRC coordination into the proof loop.

## Nuclear-positive rule

Prefer nuclear where emergency preparedness is exercised, inclusive, medically realistic, publicly intelligible, and recoverable. Do not credit nuclear maturity where public alerting, protective-action pathways, KI/medical countermeasure decisions, evacuation/shelter access, ingestion-pathway controls, drills, corrective actions, or recovery/claims pathways remain template-only.

## Control-plane effect

This file adds emergency-preparedness evidence as a hard maturity cap. Local/project evidence must close the relevant gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `exercise_evaluation_report`
- `after_action_corrective_action_ledger`
- `mutual_aid_resource_typing`
- `healthcare_evacuation_drill`
- `animal_agriculture_continuity_plan`

## Source boundary

The source IDs in this file support emergency-preparedness gate design. They do not certify any real plant, EPZ, alert system, evacuation route, KI inventory, medical capacity, drill result, after-action closure, recovery claim, or public notification without local evidence.
