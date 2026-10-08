---
id: '437'
object_type: router
domain_tags:
- nuclear_energy
- grid_planning
- resource_adequacy
- industrial_heat
- data_centers
- desalination
- hydrogen
- high_load_siting
- nuclear_regulatory_legitimacy
- nuclear_bankability
- nuclear_buildability
- nuclear_market_design
- nuclear_supply_chain
- nuclear_public_value
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_grid_interconnection_readiness
- nuclear_high_load_load_matching
- nuclear_industrial_heat
- nuclear_desalination_and_water_security
- nuclear_high_load_siting
hazard_tags:
- resource_adequacy_shortfall
- large_load_growth
- transmission_constraint
- gas_supply_constraint
- heat_smoke_outage
- industrial_decarbonization_gap
clock_tags:
- interconnection_queue_window
- capacity_planning_window
- industrial_offtake_window
- '2030_2035'
actor_tags:
- A_grid_planner
- A_data_center_operator
- A_industrial_heat_user
- A_water_authority
- A_nuclear_operator
- A_ratepayer_advocate
instrument_tags:
- interconnection_agreement
- power_purchase_agreement
- contracts_for_difference
- capacity_market
- industrial_heat_offtake
- desalination_of_take
- demand_flexibility_contract
routes_to:
- '17'
- '226'
- '247'
- '297'
- '306'
- '311'
- '429'
- '431'
- '432'
- '434'
- '436'
- '438'
- '439'
- '442'
- '443'
- '444'
- '445'
- '446'
- '447'
- '448'
- '454'
- '455'
- '456'
- '457'
- '458'
- '464'
- '465'
- '466'
- '467'
- '468'
source_ids:
- S771
- S776
- S789
- S790
- S791
- S792
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
- resource_adequacy_need
- large_load_interconnection_queue
- industrial_heat_demand
- transmission_capacity
- nuclear_project_sequence
downstream_consequences:
- clean_firm_load_matching
- avoided_fossil_lock_in
- ratepayer_burden_allocation
- demand_flexibility_contracting
equity_lenses:
- ratepayer_protection
- host_community
- essential_service_priority
- worker_transition
- water_affordability
degraded_modes:
- data_center_load_jumps_queue
- nuclear_claim_without_offtake
- industrial_heat_claim_without_process_integration
- ratepayer_cross_subsidy_hidden
evidence_grade: mixed_reliability_and_nuclear_policy_reference
speculation_level: explicit_policy_orientation_with_grid_load_caps
revision_added: rev0290
status: canon
priority_class: nuclear_positive_default_execution
owner_accountability: nuclear_preference_requires_named_operator_regulator_procurement_grid_host_community_and_public_challenge_owners
evidence_freshness: current_access_2026_sources_registered_and_revision_scoped
procurement_open_data_integrity: nuclear_delivery_requires_open_book_milestone_change_order_benefit_and_risk_transfer_traceability
civil_rights_language_access_gate: host_community_emergency_planning_public_challenge_and_benefit_covenants_must_be_language_accessible
workforce_competency_succession: nuclear_operations_construction_fuel_cycle_regulatory_emergency_and_cyber_roles_require_credentialed_depth
resilience_assurance_case: nuclear_preference_is_capped_by_deployment_sequence_fuel_cycle_siting_water_grid_delivery_and_exception_evidence
internal_control_posture: pro_nuclear_orientation_is_declared_queryable_audited_and_exception_logged
corrective_action_state: nuclear_gaps_generate_backlog_until_dated_local_evidence_and_retest_closure_exist
independent_audit_redress: independent_public_challenge_required_for_nuclear_inclusion_exclusion_or_project_maturity_claims
---
# Nuclear grid-load, industrial heat, and high-load match router

Nuclear should be routed into the cube wherever the problem is continuous clean power, high-quality heat, desalination, hydrogen, data centers, grid adequacy, or critical-load continuity. The point is not to make every load nuclear. The point is to prevent the cube from solving high-load reliability with implicit fossil fallback.

IEA tracks nuclear as a low-emission dispatchable source that can complement renewables where accepted [S790]. IAEA describes nuclear's 24/7 low-carbon role in the clean energy transition [S791]. DOE and IEA both emphasize renewed nuclear interest while leaving delivery evidence as the hard constraint [S771][S776]. NERC reliability assessments give the grid adequacy context for large-load and resource-addition decisions [S789]. NEA's digital SMR dashboard gives a way to separate credible deployment status from aspiration [S792].

## Rule

Any service floor involving continuous electricity, critical loads, industrial heat, desalination, hydrogen, data centers, or firm capacity must either:

1. route to nuclear assessment; or
2. enter the nuclear exception ledger with a reason nuclear is infeasible, inferior, illegal, too slow, too costly, socially unbuildable, or unnecessary for that loadcase.

## High-load covenant

A high-load user should not receive clean-firm nuclear benefits without a public record of interconnection cost allocation, reliability contribution, demand-flexibility obligations, emergency curtailment rules, ratepayer protection, water use, and community benefits.


## Rev0294 nuclear integrated-energy propagation note

Rev0294 extends the nuclear-positive preference into cogeneration, district heating, process heat, desalination, hydrogen and clean molecules, data-center/AI infrastructure, critical loads, and co-product public-value scorecards. These additions are explicitly bounded by new gates NG_53–NG_66 and by sector-coupling exception rules; preference is not treated as maturity without local evidence.
