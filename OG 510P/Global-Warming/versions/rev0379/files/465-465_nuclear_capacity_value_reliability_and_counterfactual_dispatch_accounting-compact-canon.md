---
id: '465'
title: 465 — Nuclear capacity value, reliability, and counterfactual dispatch accounting
object_type: scoring_model
domain_tags:
- nuclear_energy
- capacity_value
- resource_adequacy
- ELCC
- counterfactual_dispatch
- large_loads
- grid_reliability
- firm_capacity
service_floor:
- nuclear_capacity_value_accreditation
- nuclear_elcc_firm_capacity_claim
- nuclear_counterfactual_dispatch_model
- nuclear_grid_reliability_avoided_shortfall
- nuclear_retirement_avoidance_case
- nuclear_repowering_vs_retirement_review
hazard_tags:
- resource_adequacy_shortfall
- large_load_growth
- capacity_credit_overclaim
- retirement_risk
- dispatch_model_error
- unserved_energy
clock_tags:
- seasonal_resource_adequacy_cycle
- capacity_accreditation_cycle
- retirement_notice_window
- large_load_interconnection_window
actor_tags:
- A_grid_planner
- A_resource_adequacy_authority
- A_nuclear_operator
- A_load_serving_entity
- A_public_auditor
- A_data_center_load_owner
instrument_tags:
- capacity_value_ledger
- ELCC_or_accreditation_model
- counterfactual_dispatch_run
- retirement_avoidance_case
- large_load_reliability_screen
routes_to:
- '17'
- '226'
- '297'
- '429'
- '432'
- '437'
- '445'
- '451'
- '457'
- '464'
- '466'
- '467'
- '468'
source_ids:
- S842
- S846
- S847
- S851
upstream_dependencies:
- hourly_load_shape
- nuclear_availability_distribution
- planned_and_forced_outage_data
- capacity_market_or_resource_adequacy_rule
- large_load_growth_scenario
downstream_consequences:
- nuclear_clean_firm_preference_gets_capacity_value_proof
- retirement_and_uprate_claims_use_reliability_counterfactuals
- large_load_nuclear_match_gets_resource_adequacy_gate
equity_lenses:
- critical_load_reliability
- ratepayer_value
- unserved_energy_avoidance
- grid_reliability_for_public_services
degraded_modes:
- nameplate_capacity_counted_as_firm_capacity
- high_capacity_factor_assumed_without_outage_distribution
- large_load_claim_ignores_transmission_constraint
- retirement_avoidance_no_clean_replacement_counterfactual
evidence_grade: mixed
speculation_level: medium
revision_added: rev0296
status: canon
---

# 465 — Nuclear capacity value, reliability, and counterfactual dispatch accounting

## Nuclear-positive rule

The cube treats nuclear capacity as highly valuable for clean-firm reliability where the value is measured with resource-adequacy methods rather than nameplate slogans.

## Maturity cap

A nuclear pathway cannot claim reliability maturity unless capacity value, outage distribution, seasonal adequacy, transmission deliverability, and counterfactual unserved-energy reduction are documented.
