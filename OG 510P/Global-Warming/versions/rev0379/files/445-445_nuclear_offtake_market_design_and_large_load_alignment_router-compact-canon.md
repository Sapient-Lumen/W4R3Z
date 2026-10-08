---
id: '445'
title: 445 — Nuclear offtake, market design, and large-load alignment router
object_type: market_integrity_gate
domain_tags:
- nuclear_energy
- nuclear_market_design
- offtake
- large_loads
- data_centers
- capacity_markets
- clean_firm_power
- grid_reliability
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_creditworthy_offtake
- nuclear_clean_firm_capacity_market
- nuclear_large_load_alignment
- nuclear_data_center_power_match
- nuclear_grid_connection_deliverability
hazard_tags:
- load_growth_underforecast
- grid_connection_bottleneck
- phantom_clean_power_claim
- localized_rate_shock
- large_load_instability
clock_tags:
- interconnection_queue_window
- capacity_accreditation_window
- large_load_ramp_window
- resource_adequacy_cycle
- ppa_term
actor_tags:
- A_large_load_customer
- A_data_center_operator
- A_grid_operator
- A_utility_commission
- A_offtake_counterparty
- A_nuclear_operator
instrument_tags:
- clean_firm_ppa
- capacity_accreditation
- large_load_tariff
- interconnection_study
- curtailment_and_flexibility_protocol
- 24_7_cfe_contract
routes_to:
- '17'
- '226'
- '247'
- '297'
- '431'
- '432'
- '434'
- '437'
- '438'
- '444'
- '446'
- '447'
- '448'
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
source_ids:
- S804
- S805
- S806
- S807
- S808
- S809
- S810
- S811
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
upstream_dependencies:
- load_forecast
- interconnection_study
- offtake_credit_case
- resource_adequacy_need
- transmission_deliverability
downstream_consequences:
- nuclear_build_case_strengthened_by_creditworthy_clean_firm_load
- grid_risk_if_large_load_connection_precedes_resource_deliverability
- public_backlash_if_large_loads_raise_rates_without_benefit
equity_lenses:
- rate_impact_on_nonparticipants
- community_benefit_from_large_loads
- grid_reliability_for_critical_services
- water_and_land_use_for_data_centers
degraded_modes:
- data_center_green_claim_without_deliverable_power
- ppa_without_public_grid_value
- capacity_market_credit_without_performance
- large_load_connection_without_flexibility
evidence_grade: mixed
speculation_level: medium
revision_added: rev0292
status: canon
---
# 445 — Nuclear offtake, market design, and large-load alignment router

## Claim

The nuclear-positive cube should treat fast-growing large loads as a reason to favor nuclear — but only if the load contract improves the grid rather than raiding it.

AI and data-center demand are now large enough to change planning. EIA expects U.S. electricity demand to grow strongly through 2027, with large computing centers a key driver. EPRI's 2026 scenarios put U.S. data-center consumption in a much higher 2030 range than its earlier projections. NERC has also issued guidance on reliability risk from emerging large loads. [S805][S807][S806]

This makes nuclear more important, not less. High-capacity-factor clean firm power is a good match for high-load customers, industrial heat, mission-critical facilities and resource-adequacy gaps. But the cube must prevent a bad version of the pattern: large customers reserve scarce deliverability, claim clean energy, and leave everyone else with higher prices, transmission congestion or reliability risk.

## Nuclear-positive routing rule

When a file or service floor involves large load growth, clean firm procurement, industrial heat, 24/7 carbon-free electricity, data centers, grid adequacy, or critical-load continuity, it should route to the nuclear assessment plane by default.

The preferred sequence is:

1. preserve and uprate existing nuclear where safety and economics support it;
2. use creditworthy offtake to back safe restarts or repeat-build projects;
3. align SMR/advanced reactor offtake with licensing, fuel, supply-chain and host-community evidence;
4. require large-load flexibility, interconnection studies, public-value covenants and ratepayer protections before treating the offtake as maturity evidence.

Corporate nuclear PPAs and advanced-reactor agreements are useful market signals, not public certification. They strengthen the case for nuclear deployment only when mapped to grid deliverability, public benefit, safety, water, emergency planning, waste, and project controls. [S808][S809]

## New cube artifacts

`cube/nuclear-offtake-market-design.csv` records offtake structure, term, buyer credit, capacity value, grid benefit, deliverability, and public-value conditions.

`cube/nuclear-large-load-nuclear-match.csv` records whether a large load is a good nuclear match, whether it has flexibility, whether it pays its grid costs, and whether the public receives reliability or emissions value.

## Assurance consequence

The cube now favors nuclear for large-load matching, but it caps maturity if the offtake is only a press release, if deliverability is missing, if rate impacts are undisclosed, or if the customer claims clean firm power while leaning on fossil backup or public grid reserves.


## Rev0294 nuclear integrated-energy propagation note

Rev0294 extends the nuclear-positive preference into cogeneration, district heating, process heat, desalination, hydrogen and clean molecules, data-center/AI infrastructure, critical loads, and co-product public-value scorecards. These additions are explicitly bounded by new gates NG_53–NG_66 and by sector-coupling exception rules; preference is not treated as maturity without local evidence.
