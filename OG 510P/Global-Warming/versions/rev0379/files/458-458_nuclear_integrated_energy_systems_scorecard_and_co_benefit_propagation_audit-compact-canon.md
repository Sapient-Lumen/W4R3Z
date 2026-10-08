---
id: '458'
title: 458 — Nuclear integrated energy systems scorecard and co-benefit propagation audit
object_type: audit
domain_tags:
- nuclear_energy
- integrated_energy_systems
- co_benefit_audit
- sector_coupling
- public_value
- maturity_caps
- data_quality
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_integrated_energy_system_scorecard
- nuclear_coproduct_dispatch_governance
- nuclear_co_benefit_public_value_ledger
- nuclear_sector_coupling_exception_path
- nuclear_co_product_maturity_audit
hazard_tags:
- co_benefit_washing
- sector_coupling_greenwash
- private_capture_of_public_benefit
- unpriced_interface_risk
- maturity_overclaim
clock_tags:
- revision_cycle
- integrated_resource_plan_cycle
- public_value_review_cycle
- co_product_dispatch_review
- data_quality_review_cycle
actor_tags:
- A_data_steward
- A_public_auditor
- A_red_team_reviewer
- A_nuclear_operator
- A_grid_operator
- A_water_utility
- A_district_energy_authority
instrument_tags:
- integrated_energy_scorecard
- co_benefit_propagation_audit
- sector_coupling_exception_ledger
- public_value_test
- maturity_cap_execution
routes_to:
- '421'
- '422'
- '423'
- '424'
- '425'
- '426'
- '428'
- '438'
- '443'
- '448'
- '453'
- '454'
- '455'
- '456'
- '457'
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
- rev0293_operations_scorecard
- nuclear_gate_engine
- co_product_service_floors
- source_edge_sync
- sqlite_export
downstream_consequences:
- nuclear_co_benefits_become_queryable
- unverified_sector_coupling_claims_become_backlog_items
- policy_preference_propagates_to_heat_water_hydrogen_data_center_contexts
equity_lenses:
- public_transparency
- ratepayer_value
- water_access
- district_heat_affordability
- host_community_benefits
degraded_modes:
- co_benefit_claim_not_connected_to_gates
- integrated_energy_path_not_reflected_in_service_floor_map
- private_offtake_not_tested_for_public_value
- sqlite_view_omits_coproduct_gates
evidence_grade: mixed
speculation_level: medium
revision_added: rev0294
status: canon
---

# 458 — Nuclear integrated energy systems scorecard and co-benefit propagation audit

## Audit purpose

This file verifies that the nuclear-positive preference has propagated into non-electric and integrated-energy applications without turning co-benefits into slogans. It converts heat, water, hydrogen, synthetic fuels, data centers, critical loads, and public-value claims into service floors, gates, traceability rows, and gap backlog items.

## Maturity cap

If a nuclear co-product claim lacks quantified demand, interface design, safety separation, public-value accounting, ecological/water controls, dispatch priority, and independent challengeability, the relevant service floor remains capped at `R2_documented_template_only`.
