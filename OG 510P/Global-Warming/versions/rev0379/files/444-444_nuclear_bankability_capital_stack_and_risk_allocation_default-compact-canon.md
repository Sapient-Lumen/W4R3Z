---
id: '444'
title: 444 — Nuclear bankability, capital stack, and risk-allocation default
object_type: finance_packet
domain_tags:
- nuclear_energy
- nuclear_bankability
- capital_stack
- loan_guarantee
- risk_allocation
- public_finance
- clean_firm_power
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_liability
- financial_assurance
- decommissioning_trust
- incident_compensation
- public_risk_transfer
service_floor:
- nuclear_bankability_case
- nuclear_capital_stack_governance
- nuclear_loan_guarantee_readiness
- nuclear_orderbook_commitment
- nuclear_risk_allocation_matrix
hazard_tags:
- financing_gap
- cost_of_capital_spike
- residual_risk_dumping
- single_project_foak_exposure
- policy_reversal_risk
clock_tags:
- pre_fid_window
- credit_committee_window
- rate_case_window
- loan_guarantee_review_window
- portfolio_review_cycle
actor_tags:
- A_nuclear_finance_authority
- A_public_power_authority
- A_utility_commission
- A_ratepayer_advocate
- A_infrastructure_bank
- A_nuclear_operator
instrument_tags:
- capital_stack
- loan_guarantee
- regulated_asset_base
- contract_for_difference
- public_power_ownership
- risk_allocation_matrix
- open_book_cost_model
routes_to:
- '04'
- '17'
- '226'
- '247'
- '425'
- '428'
- '431'
- '433'
- '434'
- '438'
- '439'
- '443'
- '445'
- '446'
- '447'
- '448'
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
- '479'
- '480'
- '481'
- '482'
- '483'
source_ids:
- S776
- S801
- S802
- S803
- S811
upstream_dependencies:
- licensed_or_licensable_design
- creditworthy_owner
- public_value_case
- risk_allocation_negotiation
- regulatory_stability
downstream_consequences:
- lower_financing_cost_if_risk_is_allocated_explicitly
- false_bankability_if_residual_risk_is_hidden
- public_backlash_if_ratepayer_exposure_is_unbounded
equity_lenses:
- ratepayer_protection
- host_community_benefit
- public_budget_crowding_out
- intergenerational_cost_allocation
degraded_modes:
- vendor_promotion_without_credit_case
- loan_guarantee_without_repayment_path
- cost_overrun_socialized_without_public_value
- private_upside_public_downside
evidence_grade: mixed
speculation_level: medium
revision_added: rev0292
status: canon
---
# 444 — Nuclear bankability, capital stack, and risk-allocation default

## Claim

A nuclear-positive climate cube should not treat nuclear as merely a technology preference. It must treat nuclear as a **bankability problem under public-value constraints**.

The cube now favors nuclear where clean-firm capacity, fuel security, grid reliability, industrial heat, water security or high-load siting make nuclear a high-value option. But that preference is only operational when the capital stack can survive scrutiny.

The default rule is:

> nuclear is favored when the public can see a credible capital stack, risk-allocation matrix, repayment path, public-value covenant, and maturity cap before final investment decision.

This is deliberately pro-nuclear. It says public institutions should actively solve the financing problem instead of letting high cost of capital silently kill clean-firm projects. It is also deliberately bounded. A nuclear project is not mature because it has a sponsor, a reactor design, or a policy slogan. It becomes mature only when financing risk has been allocated, priced, disclosed and governed. [S776][S801][S802][S803]

## Policy default

For relevant clean-firm contexts, the burden of proof now shifts:

1. A serious clean-power portfolio should explain why existing nuclear life extension, uprates, restarts, repeat builds or bankable advanced nuclear are excluded.
2. A proposed nuclear project should explain who bears construction, financing, policy, offtake, fuel, security, waste, decommissioning and residual risks.
3. A public finance intervention should be scored as a pro-climate instrument when it lowers capital cost for a gated nuclear project without hiding ratepayer or taxpayer exposure.
4. A private offtaker should not be allowed to claim clean-firm leadership while externalizing grid, transmission, backup, water, emergency or public legitimacy costs.

## Required cube controls

The new table `cube/nuclear-finance-capital-stack.csv` records the financing instrument, capital provider, risk holder, repayment path and public-value condition.

The new table `cube/nuclear-risk-allocation-matrix.csv` records who bears cost overrun, schedule, licensing, offtake, force majeure, fuel, waste, decommissioning and policy-change risk.

The new table `cube/nuclear-project-stage-gate.csv` turns bankability into staged evidence: pre-feasibility, site/docket, capital stack, final investment decision, construction, fuel load, commercial operation and post-COD performance.

## Assurance consequence

A nuclear service floor that lacks an auditable capital stack is capped at `R2_documented_template_only` even if the technology is favored. A nuclear service floor that hides residual public exposure is capped at `R1_concept_only`. A project that discloses risk and creates public-value protections may advance once the parallel safety, waste, siting, security, workforce, grid and public-participation gates are met.
