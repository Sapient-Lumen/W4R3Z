---
id: '450'
title: 450 — Nuclear outage, refueling, maintenance, and spares control
object_type: delivery_packet
domain_tags:
- nuclear_energy
- outage_management
- refueling
- preventive_maintenance
- spares
- asset_management
- configuration_management
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_planned_outage_refueling_readiness
- nuclear_preventive_maintenance_and_spares
- nuclear_online_maintenance_risk_control
- nuclear_fuel_reload_and_core_design_review
- nuclear_configuration_management
hazard_tags:
- outage_overrun
- maintenance_deferral
- spare_part_shortage
- configuration_drift
- fuel_reload_error
- craft_workforce_bottleneck
clock_tags:
- refueling_outage_window
- maintenance_rule_cycle
- spares_lead_time
- configuration_control_window
- core_design_review_window
actor_tags:
- A_outage_management_team
- A_nuclear_maintenance_program
- A_reactor_engineering_team
- A_supply_chain_qa_body
- A_nuclear_operator
instrument_tags:
- outage_readiness_review
- maintenance_rule_program
- critical_spares_register
- configuration_management_system
- fuel_reload_safety_review
routes_to:
- '247'
- '421'
- '422'
- '423'
- '427'
- '431'
- '435'
- '439'
- '446'
- '449'
- '451'
- '452'
- '453'
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
source_ids:
- S817
- S818
- S819
- S814
- S820
upstream_dependencies:
- outage_scope_freeze
- critical_spares_inventory
- qualified_maintenance_workforce
- configuration_baseline
- fuel_cycle_plan
downstream_consequences:
- shorter_safer_outages_if_work_scope_is_controlled
- forced_outage_risk_if_maintenance_is_deferred
- safety_risk_if_configuration_records_are_not_current
equity_lenses:
- worker_safety
- local_workforce_access
- ratepayer_value
- public_reporting_of_material_events
degraded_modes:
- outage_schedule_claim_without_critical_path
- spares_procurement_without_quality_records
- online_maintenance_without_risk_review
- core_reload_review_not_traceable
evidence_grade: mixed
speculation_level: medium
revision_added: rev0293
status: canon
---

# 450 — Nuclear outage, refueling, maintenance, and spares control

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
