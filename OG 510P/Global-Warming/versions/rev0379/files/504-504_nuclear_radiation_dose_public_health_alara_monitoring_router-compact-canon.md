---
id: '504'
title: Nuclear radiation dose, public health, and ALARA monitoring router
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
- nuclear_public_dose_limit_compliance
- nuclear_alara_release_optimization
- nuclear_radiation_protection_program_public_interface
- nuclear_worker_public_dose_separation
- nuclear_public_health_baseline_monitoring
- nuclear_dose_counterevidence_review
hazard_tags:
- public_dose_overclaim
- alara_program_gap
- dose_pathway_misattribution
- low_dose_risk_miscommunication
- occupational_public_dose_boundary_error
- radiological_trust_failure
clock_tags:
- annual_public_dose_report_cycle
- alara_review_cycle
- public_health_baseline_review_cycle
- dose_counterevidence_review_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_radiation_protection_manager
- A_public_health_agency
- A_public_auditor
instrument_tags:
- public_dose_assessment
- alara_release_review
- radiation_protection_program
- public_health_baseline_ledger
- dose_counterevidence_ledger
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
- '441'
- '489'
- '493'
- '498'
- '503'
- '505'
- '506'
- '507'
- '508'
source_ids:
- S939
- S940
- S941
- S942
- S952
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
- public_dose_overclaim
- alara_program_gap
- dose_pathway_misattribution
- low_dose_risk_miscommunication
- occupational_public_dose_boundary_error
- radiological_trust_failure
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
- public_dose_overclaim
- alara_program_gap
- dose_pathway_misattribution
- low_dose_risk_miscommunication
- occupational_public_dose_boundary_error
- radiological_trust_failure
proof_ledgers:
- public_dose_assessment
- alara_release_review
- radiation_protection_program
- public_health_baseline_ledger
- dose_counterevidence_ledger
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_radiological_monitoring_gate_evaluation
- monitoring_data_quality_publication_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_monitoring_framework_sensitive_local_details_redacted
nuclear_policy_orientation: favored_with_radiological_monitoring_dose_effluent_public_health_gates
---

# 504 — Nuclear radiation dose, public health, and ALARA monitoring router

## Function

This router makes the cube's pro-nuclear preference conditional on auditable public dose, ALARA, dose pathways, public-health baselines, and counterevidence review. It is not enough for a nuclear pathway to be low-carbon, firm, licensed, financed, staffed, cyber-protected and physically secure; it must also be measurable in the public dose and environmental record.

## Nuclear-positive rule

Prefer nuclear where radiological releases, dose pathways, monitoring data, counterevidence, and public-health interfaces are visible enough to sustain trust. Do not credit nuclear maturity where monitoring is stale, unreviewable, inaccessible, over-aggregated, or published in a way that hides uncertainty while claiming public assurance.

## Control-plane effect

This file adds radiological monitoring as a maturity cap. Local/project evidence must close the relevant monitoring gates before nuclear service floors can rise above documented-template maturity.

## Required evidence

- `public_dose_assessment`
- `alara_release_review`
- `radiation_protection_program`
- `public_health_baseline_ledger`
- `dose_counterevidence_ledger`

## Source boundary

The source IDs in this file support the monitoring/gate design. They do not certify any real plant, discharge, dose estimate, groundwater plume, environmental sample, monitoring station, health registry, laboratory result, or public notification without local evidence.
