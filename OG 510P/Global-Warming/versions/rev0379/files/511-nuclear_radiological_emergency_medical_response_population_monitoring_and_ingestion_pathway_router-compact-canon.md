---
id: '511'
title: Nuclear radiological emergency medical response, population monitoring, and ingestion-pathway router
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
- nuclear_population_monitoring_decontamination
- nuclear_radiological_triage_hospital_capacity
- nuclear_first_responder_radiation_safety
- nuclear_food_water_agriculture_control
- nuclear_drinking_water_alternate_supply
- nuclear_school_childcare_protective_action
hazard_tags:
- medical_surge_failure
- decontamination_bottleneck
- first_responder_exposure
- food_water_control_failure
- drinking_water_supply_gap
clock_tags:
- hospital_drill_cycle
- population_monitoring_exercise_cycle
- food_water_control_review_cycle
- worker_safety_training_cycle
actor_tags:
- A_public_health_authority
- A_hospital_coalition
- A_first_responder_agency
- A_water_utility
- A_food_agriculture_authority
- A_worker_safety_authority
instrument_tags:
- radiological_triage_protocol
- population_monitoring_site_plan
- decontamination_protocol
- food_water_control_trigger
- first_responder_dose_control
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
- '512'
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
- medical_surge_failure
- decontamination_bottleneck
- first_responder_exposure
- food_water_control_failure
- drinking_water_supply_gap
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
- medical_surge_failure
- decontamination_bottleneck
- first_responder_exposure
- food_water_control_failure
- drinking_water_supply_gap
proof_ledgers:
- radiological_triage_protocol
- population_monitoring_site_plan
- decontamination_protocol
- food_water_control_trigger
- first_responder_dose_control
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

# 511 — Nuclear radiological emergency medical response, population monitoring, and ingestion-pathway router

## Function

This router makes emergency medical response, population monitoring, decontamination, responder safety, and ingestion-pathway controls auditable instead of assumed.

## Nuclear-positive rule

Prefer nuclear where emergency preparedness is exercised, inclusive, medically realistic, publicly intelligible, and recoverable. Do not credit nuclear maturity where public alerting, protective-action pathways, KI/medical countermeasure decisions, evacuation/shelter access, ingestion-pathway controls, drills, corrective actions, or recovery/claims pathways remain template-only.

## Control-plane effect

This file adds emergency-preparedness evidence as a hard maturity cap. Local/project evidence must close the relevant gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `radiological_triage_protocol`
- `population_monitoring_site_plan`
- `decontamination_protocol`
- `food_water_control_trigger`
- `first_responder_dose_control`

## Source boundary

The source IDs in this file support emergency-preparedness gate design. They do not certify any real plant, EPZ, alert system, evacuation route, KI inventory, medical capacity, drill result, after-action closure, recovery claim, or public notification without local evidence.
