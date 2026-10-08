---
id: '505'
title: Nuclear effluent discharge, environmental surveillance, and tritium/groundwater router
object_type: integrity_gate
domain_tags:
- nuclear_energy
- radiological_monitoring
- public_dose_accountability
- radioactive_effluent_control
- environmental_surveillance
- tritium_groundwater_monitoring
- public_health_baseline
- independent_monitoring
- radiation_dashboard
- nuclear_public_trust
service_floor:
- nuclear_radioactive_effluent_source_monitoring
- nuclear_annual_effluent_environmental_reports
- nuclear_tritium_groundwater_surveillance
- nuclear_environmental_media_sampling
- nuclear_discharge_authorization_review
- nuclear_groundwater_leak_response
hazard_tags:
- unmonitored_effluent_pathway
- tritium_groundwater_plume
- sampling_gap
- annual_report_staleness
- discharge_authorization_gap
- groundwater_leak_underreporting
clock_tags:
- effluent_report_cycle
- groundwater_well_sampling_cycle
- environmental_media_sampling_cycle
- discharge_authorization_review_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_environmental_monitoring_lab
- A_water_utility
- A_host_community_reviewer
instrument_tags:
- radioactive_effluent_report
- radiological_environmental_monitoring_program
- groundwater_monitoring_well_network
- tritium_sampling_plan
- discharge_authorization_docket
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '421'
- '422'
- '428'
- '429'
- '430'
- '435'
- '460'
- '461'
- '485'
- '489'
- '490'
- '504'
- '506'
- '507'
- '508'
source_ids:
- S940
- S943
- S944
- S945
- S946
- S947
- S948
- S951
upstream_dependencies:
- nuclear_policy_preference
- public_dose_accountability
- radiological_monitoring_program
- public_assurance_evidence
downstream_consequences:
- radiological_monitoring_caps_nuclear_maturity
- pro_nuclear_preference_becomes_measurement_assured
- public_trust_depends_on_open_and_redacted_monitoring_evidence
equity_lenses:
- host_communities
- downstream_water_users
- children
- pregnant_people
- workers
- subsistence_fishing_hunting_households
- language_access_users
- disabled_people
- public_auditors
degraded_modes:
- unmonitored_effluent_pathway
- tritium_groundwater_plume
- sampling_gap
- annual_report_staleness
- discharge_authorization_gap
- groundwater_leak_underreporting
evidence_grade: control_plane_template_with_official_guidance_sources
speculation_level: low_for_gate_design_high_for_project_specific_readiness_until_localized
revision_added: rev0304
status: canon
bottlenecks:
- monitoring_data_latency
- lab_quality_assurance_capacity
- public_plain_language_translation
- security_sensitive_redaction_boundary
- dose_pathway_uncertainty
failure_modes:
- unmonitored_effluent_pathway
- tritium_groundwater_plume
- sampling_gap
- annual_report_staleness
- discharge_authorization_gap
- groundwater_leak_underreporting
proof_ledgers:
- radioactive_effluent_report
- radiological_environmental_monitoring_program
- groundwater_monitoring_well_network
- tritium_sampling_plan
- discharge_authorization_docket
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_radiological_monitoring_gate_evaluation
- monitoring_data_quality_publication_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_monitoring_framework_sensitive_local_details_redacted
nuclear_policy_orientation: favored_with_radiological_monitoring_dose_effluent_public_health_gates
---

# 505 — Nuclear effluent discharge, environmental surveillance, and tritium/groundwater router

## Function

This router makes the cube's pro-nuclear preference conditional on auditable radioactive effluent, environmental reports, tritium, groundwater and environmental media sampling. It is not enough for a nuclear pathway to be low-carbon, firm, licensed, financed, staffed, cyber-protected and physically secure; it must also be measurable in the public dose and environmental record.

## Nuclear-positive rule

Prefer nuclear where radiological releases, dose pathways, monitoring data, counterevidence, and public-health interfaces are visible enough to sustain trust. Do not credit nuclear maturity where monitoring is stale, unreviewable, inaccessible, over-aggregated, or published in a way that hides uncertainty while claiming public assurance.

## Control-plane effect

This file adds radiological monitoring as a maturity cap. Local/project evidence must close the relevant monitoring gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `radioactive_effluent_report`
- `radiological_environmental_monitoring_program`
- `groundwater_monitoring_well_network`
- `tritium_sampling_plan`
- `discharge_authorization_docket`

## Source boundary

The source IDs in this file support the monitoring/gate design. They do not certify any real plant, discharge, dose estimate, groundwater plume, environmental sample, monitoring station, health registry, laboratory result, or public notification without local evidence.
