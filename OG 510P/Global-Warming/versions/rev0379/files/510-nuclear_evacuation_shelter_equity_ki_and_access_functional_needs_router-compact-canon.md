---
id: '510'
title: Nuclear evacuation, shelter equity, KI, and access/functional-needs router
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
- nuclear_evacuation_route_capacity
- nuclear_shelter_in_place_readiness
- nuclear_transportation_assistance_registry
- nuclear_disability_access_evacuations
- nuclear_ki_distribution_decision_pathway
- nuclear_medical_countermeasure_stockpile
hazard_tags:
- evacuation_route_failure
- shelter_access_failure
- ki_misuse_or_shortage
- language_access_failure
- functional_needs_exclusion
clock_tags:
- evacuation_route_exercise_cycle
- ki_inventory_rotation_cycle
- access_functional_needs_registry_update_cycle
actor_tags:
- A_local_emergency_management
- A_public_health_authority
- A_disability_access_officer
- A_transit_operator
- A_school_district
- A_long_term_care_operator
instrument_tags:
- evacuation_route_capacity_model
- shelter_in_place_protocol
- ki_distribution_decision_tree
- access_functional_needs_test
- transportation_assistance_registry
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
- '511'
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
- evacuation_route_failure
- shelter_access_failure
- ki_misuse_or_shortage
- language_access_failure
- functional_needs_exclusion
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
- evacuation_route_failure
- shelter_access_failure
- ki_misuse_or_shortage
- language_access_failure
- functional_needs_exclusion
proof_ledgers:
- evacuation_route_capacity_model
- shelter_in_place_protocol
- ki_distribution_decision_tree
- access_functional_needs_test
- transportation_assistance_registry
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

# 510 — Nuclear evacuation, shelter equity, KI, and access/functional-needs router

## Function

This router turns evacuation, shelter-in-place, KI, transportation assistance, disability access, language access, schools, and long-term-care plans into explicit nuclear maturity caps.

## Nuclear-positive rule

Prefer nuclear where emergency preparedness is exercised, inclusive, medically realistic, publicly intelligible, and recoverable. Do not credit nuclear maturity where public alerting, protective-action pathways, KI/medical countermeasure decisions, evacuation/shelter access, ingestion-pathway controls, drills, corrective actions, or recovery/claims pathways remain template-only.

## Control-plane effect

This file adds emergency-preparedness evidence as a hard maturity cap. Local/project evidence must close the relevant gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `evacuation_route_capacity_model`
- `shelter_in_place_protocol`
- `ki_distribution_decision_tree`
- `access_functional_needs_test`
- `transportation_assistance_registry`

## Source boundary

The source IDs in this file support emergency-preparedness gate design. They do not certify any real plant, EPZ, alert system, evacuation route, KI inventory, medical capacity, drill result, after-action closure, recovery claim, or public notification without local evidence.
