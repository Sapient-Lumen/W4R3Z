---
id: '466'
title: 466 — Nuclear lifecycle emissions, land, material, and environmental externality ledger
object_type: ledger
domain_tags:
- nuclear_energy
- lifecycle_assessment
- GHG
- land_use
- material_intensity
- water_thermal_externality
- environmental_footprint
- comparative_metrics
service_floor:
- nuclear_lifecycle_emissions_boundary
- nuclear_land_use_footprint
- nuclear_material_intensity_footprint
- nuclear_land_material_per_mwh_metric
- nuclear_environmental_externality_ledger
- nuclear_comparative_safety_metric
hazard_tags:
- lifecycle_boundary_error
- land_use_overclaim
- material_intensity_overclaim
- thermal_pollution_ignored
- water_externality_ignored
- cherry_picked_LCA
clock_tags:
- lifecycle_inventory_review_cycle
- environmental_permit_review_cycle
- thermal_discharge_review_cycle
- supply_chain_update_cycle
actor_tags:
- A_lifecycle_assessor
- A_environmental_regulator
- A_nuclear_operator
- A_public_auditor
- A_host_community_reviewer
instrument_tags:
- lifecycle_GHG_boundary
- land_use_metric
- material_intensity_metric
- environmental_externality_ledger
- comparative_safety_metric
- LCA_source_crosswalk
routes_to:
- '430'
- '436'
- '455'
- '459'
- '461'
- '464'
- '465'
- '467'
- '468'
source_ids:
- S843
- S844
- S845
- S848
- S850
upstream_dependencies:
- LCA_boundary_definition
- supply_chain_inventory
- land_occupation_metric
- material_inventory
- water_and_thermal_discharge_assessment
downstream_consequences:
- nuclear_benefit_claims_are_lifecycle_bounded
- land_material_and_externality_claims_become_queryable
- comparative_safety_claims_are_separated_from_security_or_site_claims
equity_lenses:
- host_community_environmental_burden
- water_ecology
- mining_and_fuel_cycle_externalities
- transparent_LCA_assumptions
degraded_modes:
- operational_zero_carbon_claim_used_as_lifecycle_claim
- land_footprint_ignores_mining_or_transmission
- material_metric_not_normalized_per_MWh
- externalities_hidden_behind_clean_firm_label
evidence_grade: mixed
speculation_level: medium
revision_added: rev0296
status: canon
---

# 466 — Nuclear lifecycle emissions, land, material, and environmental externality ledger

## Nuclear-positive rule

The cube favors nuclear partly because its lifecycle, land-use, material and safety profile can compare favorably with fossil-heavy alternatives when boundaries are explicit.

## Guardrail

Lifecycle accounting must include fuel-cycle, construction, operations, decommissioning, water/thermal, land, and material boundaries. Operational zero-carbon language is not enough for maturity.
