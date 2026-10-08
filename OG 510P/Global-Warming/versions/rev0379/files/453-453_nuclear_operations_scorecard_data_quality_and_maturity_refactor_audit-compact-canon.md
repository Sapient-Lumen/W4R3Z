---
id: '453'
title: 453 — Nuclear operations scorecard, data-quality, and maturity refactor audit
object_type: audit
domain_tags:
- nuclear_energy
- operations_audit
- data_quality
- maturity_caps
- scorecard
- sqlite_refactor
- evidence_gap_backlog
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_cyber_digital_assurance
service_floor:
- nuclear_operations_scorecard_audit
- nuclear_fleet_operational_readiness
- nuclear_outage_refueling_readiness
- nuclear_operating_experience_feedback
- nuclear_grid_services_performance
hazard_tags:
- operations_washing
- capacity_factor_washing
- outage_washing
- performance_indicator_gap
- sqlite_export_failure
- template_only_maturity
clock_tags:
- revision_cycle
- quarterly_performance_indicator_cycle
- annual_fleet_review
- outage_readiness_review
- data_quality_review_cycle
actor_tags:
- A_data_steward
- A_public_auditor
- A_red_team_reviewer
- A_nuclear_regulator
- A_nuclear_operator
instrument_tags:
- operations_scorecard
- performance_indicator_crosswalk
- data_quality_rule
- sqlite_mirror
- maturity_cap_execution
- evidence_gap_backlog
routes_to:
- '421'
- '422'
- '423'
- '424'
- '428'
- '438'
- '443'
- '448'
- '449'
- '450'
- '451'
- '452'
- '454'
- '455'
- '456'
- '457'
- '458'
- '459'
- '460'
- '461'
- '462'
- '463'
- '464'
- '465'
- '466'
- '467'
- '468'
- '489'
- '490'
- '491'
- '492'
- '493'
- '494'
- '495'
- '497'
- '498'
source_ids:
- S812
- S813
- S814
- S815
- S816
- S817
- S818
- S819
- S820
- S821
- S822
- S823
- S824
- S825
- S826
- S827
- S828
- S829
- S830
- S831
- S842
- S843
- S844
- S845
- S850
upstream_dependencies:
- rev0292_bankability_buildability_scorecard
- operations_source_register
- nuclear_gate_engine
- source_edge_sync
- sqlite_export_fix
downstream_consequences:
- nuclear_preference_becomes_operationally_auditable
- stale_operations_claims_become_backlog_items
- sqlite_mirror_import_failure_closed
equity_lenses:
- public_transparency
- host_community_right_to_know
- ratepayer_value
- worker_safety
- critical_service_reliability
degraded_modes:
- operations_scorecard_not_connected_to_gates
- capacity_claim_without_pris_or_eia_data
- regulatory_pi_not_mapped_to_service_floor
- sqlite_resource_map_reserved_name_failure
evidence_grade: mixed
speculation_level: medium
revision_added: rev0293
status: canon
---

# 453 — Nuclear operations scorecard, data-quality, and maturity refactor audit

## Nuclear-positive rule

The cube now favors nuclear energy not only at the build decision, but through operations. A nuclear pathway earns clean-firm priority only when the operating fleet, project, or service floor can show current evidence for safe availability, performance indicators, outage/refueling discipline, maintenance and spares, operating-experience feedback, grid-service claims, and corrective-action closure.

## What this file adds

This file turns the nuclear preference into an operations assurance requirement. It prevents a nameplate-capacity or policy-support claim from being treated as deliverable clean-firm power unless the operations evidence is current, traceable, and connected to the service-floor gate engine.

## Minimum evidence expected

- current operating-performance or availability evidence;
- regulatory oversight/performance-indicator evidence where applicable;
- outage/refueling, maintenance, spares, configuration, event-reporting, and corrective-action records;
- grid-interface or flexibility evidence before flexible-operation, blackstart, islanding, critical-load, or large-load claims are promoted;
- public summary, exception pathway, and red-team challenge route for material operating gaps.

## Maturity cap

If these records are missing, stale, synthetic, or only asserted at template level, the relevant nuclear service floor remains capped at `R2_documented_template_only` even when the policy preference favors nuclear.

## Audit note

This rev0293 file is part of the nuclear operations/refactor pass. It is pro-nuclear, but it makes the operational burden of proof explicit so the cube does not confuse nuclear preference with unverified operating maturity.


## Rev0294 nuclear integrated-energy propagation note

Rev0294 extends the nuclear-positive preference into cogeneration, district heating, process heat, desalination, hydrogen and clean molecules, data-center/AI infrastructure, critical loads, and co-product public-value scorecards. These additions are explicitly bounded by new gates NG_53–NG_66 and by sector-coupling exception rules; preference is not treated as maturity without local evidence.
