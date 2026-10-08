---
id: '449'
title: 449 — Nuclear operating excellence, fleet availability, and performance indicators
object_type: service_continuity
domain_tags:
- nuclear_energy
- operating_excellence
- fleet_availability
- capacity_factor
- reactor_oversight
- performance_indicators
- clean_firm_power
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_fleet_operational_readiness
- nuclear_capacity_factor_assurance
- nuclear_forced_outage_recovery
- nuclear_performance_indicator_monitoring
hazard_tags:
- unplanned_scram
- forced_outage
- capacity_factor_degradation
- safety_system_functional_failure
- performance_indicator_decline
clock_tags:
- quarterly_performance_indicator_cycle
- refueling_cycle
- fleet_review_cycle
- resource_adequacy_season
- public_oversight_window
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_grid_operator
- A_public_auditor
- A_operating_experience_program
instrument_tags:
- reactor_oversight_process
- performance_indicator_dashboard
- capacity_factor_ledger
- forced_outage_root_cause
- operating_experience_loop
routes_to:
- '17'
- '226'
- '247'
- '428'
- '429'
- '432'
- '436'
- '437'
- '438'
- '441'
- '442'
- '443'
- '444'
- '445'
- '446'
- '447'
- '448'
- '450'
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
- '489'
- '490'
- '491'
- '492'
- '493'
source_ids:
- S812
- S813
- S814
- S815
- S816
- S821
upstream_dependencies:
- licensed_operating_reactor
- qualified_operations_staff
- current_performance_indicators
- generation_and_outage_data
- independent_regulatory_oversight
downstream_consequences:
- nuclear_preference_strengthened_when_operations_are_high_availability_and_safe
- false_clean_firm_claim_if_capacity_or_forced_outage_evidence_is_stale
- maturity_cap_if_performance_indicators_are_unreported_or_declining
equity_lenses:
- critical_service_reliability
- ratepayer_value_from_existing_assets
- worker_fatigue_and_safety
- public_transparency
degraded_modes:
- nameplate_capacity_treated_as_deliverable_capacity
- high_capacity_factor_claim_without_current_data
- safety_performance_indicator_ignored
- forced_outage_closed_without_root_cause
evidence_grade: mixed
speculation_level: low
revision_added: rev0293
status: canon
---

# 449 — Nuclear operating excellence, fleet availability, and performance indicators

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
