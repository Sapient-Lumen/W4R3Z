---
id: '454'
title: 454 — Nuclear cogeneration, district heat, and process-heat integration router
object_type: router
domain_tags:
- nuclear_energy
- cogeneration
- district_heating
- process_heat
- industrial_decarbonization
- thermal_storage
- integrated_energy_systems
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_cogeneration_dispatch
- nuclear_district_heat_service
- nuclear_industrial_process_heat
- nuclear_thermal_storage_interface
- nuclear_waste_heat_recovery
- nuclear_heat_market_access
hazard_tags:
- thermal_of_take_failure
- heat_network_leak
- industrial_trip_coupling
- nuclear_industrial_interface_failure
- thermal_storage_mismatch
clock_tags:
- heat_season
- industrial_load_cycle
- refueling_cycle
- thermal_storage_cycle
- cogeneration_dispatch_window
actor_tags:
- A_nuclear_operator
- A_district_energy_authority
- A_industrial_heat_customer
- A_grid_operator
- A_public_auditor
instrument_tags:
- cogeneration_dispatch_protocol
- heat_offtake_contract
- nuclear_industrial_interface_agreement
- thermal_storage_control
- public_value_scorecard
routes_to:
- '17'
- '226'
- '247'
- '297'
- '421'
- '422'
- '423'
- '425'
- '426'
- '428'
- '429'
- '430'
- '431'
- '432'
- '433'
- '434'
- '435'
- '436'
- '437'
- '438'
- '439'
- '440'
- '441'
- '442'
- '443'
- '444'
- '445'
- '446'
- '447'
- '448'
- '449'
- '450'
- '451'
- '452'
- '453'
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
source_ids:
- S822
- S823
- S825
- S826
upstream_dependencies:
- licensed_reactor_or_project
- thermal_load_study
- safety_separation_case
- heat_network_rights_of_way
- offtake_contract
downstream_consequences:
- nuclear_value_expands_beyond_electricity
- industrial_decarbonization_pathway_strengthened
- maturity_cap_if_heat_load_or_safety_interface_not_evidenced
equity_lenses:
- district_heat_affordability
- industrial_worker_safety
- host_community_benefits
- ratepayer_public_value
degraded_modes:
- cogeneration_claim_without_heat_load
- industrial_heat_claim_without_safety_boundary
- district_heat_claim_without_customer_protection
- thermal_storage_claim_without_dispatch_test
evidence_grade: mixed
speculation_level: medium
revision_added: rev0294
status: canon
---

# 454 — Nuclear cogeneration, district heat, and process-heat integration router

## Nuclear-positive rule

The cube now treats useful heat as a first-class nuclear co-product. Where credible heat demand exists, nuclear cogeneration, district heating, process heat, waste-heat recovery, and thermal storage should be preferred over fossil heat, provided safety, interface, public-value, and deliverability gates are met.

## What this file adds

This router converts nuclear heat from a background co-benefit into service floors, owner roles, evidence tables, maturity gates, and public-value checks. The preference is strongest for existing reactors with nearby heat sinks, repeatable industrial clusters, and district-energy systems where customer protections and safety separation can be demonstrated.

## Maturity cap

No nuclear heat pathway may exceed `R2_documented_template_only` until heat-load data, dispatch protocol, nuclear/industrial interface boundaries, customer protections, and emergency fallback evidence are recorded.
