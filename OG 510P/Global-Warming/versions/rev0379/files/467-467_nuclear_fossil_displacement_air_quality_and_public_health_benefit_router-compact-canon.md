---
id: '467'
title: 467 — Nuclear fossil-displacement, air-quality, and public-health benefit router
object_type: router
domain_tags:
- nuclear_energy
- fossil_displacement
- coal_retirement
- gas_displacement
- methane
- air_quality
- public_health
- environmental_justice
service_floor:
- nuclear_gas_displacement_case
- nuclear_coal_displacement_case
- nuclear_avoided_methane_leakage_claim
- nuclear_air_pollution_benefit_scorecard
- nuclear_public_health_avoidance_ledger
- nuclear_energy_security_import_reduction
hazard_tags:
- coal_retirement_delay
- gas_lock_in
- methane_leakage_underaccounted
- air_pollution_benefit_overclaim
- environmental_justice_misalignment
- fossil_backup_dependency
clock_tags:
- annual_emissions_inventory
- fossil_retirement_window
- air_quality_attainment_review_cycle
- methane_inventory_update_cycle
actor_tags:
- A_public_health_authority
- A_air_quality_regulator
- A_grid_planner
- A_nuclear_operator
- A_environmental_justice_reviewer
- A_public_auditor
instrument_tags:
- fossil_displacement_case
- coal_retirement_counterfactual
- gas_displacement_and_methane_boundary
- air_quality_public_health_scorecard
- EJ_benefit_distribution_audit
routes_to:
- '17'
- '429'
- '432'
- '444'
- '445'
- '464'
- '465'
- '466'
- '468'
source_ids:
- S842
- S844
- S848
- S849
- S850
upstream_dependencies:
- dispatch_counterfactual
- retired_or_avoided_fossil_unit_list
- pollutant_exposure_model
- methane_leakage_assumption
- benefit_distribution_map
downstream_consequences:
- nuclear_preference_is_tied_to_actual_fossil_avoidance
- air_quality_and_health_claims_get_evidence_requirements
- EJ_distribution_becomes_part_of_system_benefit_score
equity_lenses:
- coal_community_pollution_reduction
- gas_peaker_pollution_reduction
- environmental_justice_benefit_distribution
- import_dependency_and_energy_security
degraded_modes:
- nuclear_added_but_fossil_generation_not_reduced
- benefits_claimed_in_clean_grid_without_marginal_displacement
- methane_leakage_excluded_from_gas_counterfactual
- air_quality_benefit_not_spatially_mapped
evidence_grade: mixed
speculation_level: medium
revision_added: rev0296
status: canon
---

# 467 — Nuclear fossil-displacement, air-quality, and public-health benefit router

## Nuclear-positive rule

Nuclear receives the strongest cube preference when it prevents coal or gas generation, fossil-retirement delay, methane exposure, air-pollution damage, or reliability-driven fossil lock-in.

## Burden of proof

The scorecard asks: what fossil unit, fuel, capacity product, or reliability service is actually displaced? Which people receive the air-quality and reliability benefit? Which fossil dependence remains?
