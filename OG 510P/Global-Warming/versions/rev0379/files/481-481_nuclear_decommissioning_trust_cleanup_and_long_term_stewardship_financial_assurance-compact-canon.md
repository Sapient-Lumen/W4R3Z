---
id: '481'
title: 481 — Nuclear decommissioning trust, cleanup, and long-term stewardship financial assurance
object_type: control_packet
domain_tags:
- nuclear_energy
- decommissioning_financial_assurance
- decommissioning_trust
- cleanup_funding
- long_term_stewardship
- waste_funding
service_floor:
- nuclear_decommissioning_trust_adequacy
- nuclear_decommissioning_cost_escalation_control
- nuclear_decommissioning_trust_governance
- nuclear_decontamination_cleanup_funding
- nuclear_long_term_stewardship_funding
- nuclear_environmental_remediation_financial_assurance
- nuclear_waste_repository_liability_boundary
- nuclear_spent_fuel_liability_allocation
hazard_tags:
- decommissioning_funding_shortfall
- cost_escalation_underestimate
- trust_governance_conflict
- cleanup_funding_gap
- long_term_stewardship_unfunded
- waste_liability_boundary_gap
clock_tags:
- biennial_decommissioning_fund_report
- annual_pre_shutdown_funding_review
- license_termination_planning_clock
- long_term_stewardship_review_cycle
actor_tags:
- A_nuclear_operator
- A_regulator
- A_public_auditor
- A_decommissioning_authority
- A_waste_management_organization
- A_ratepayer_advocate
instrument_tags:
- decommissioning_trust_fund
- financial_assurance_report
- cost_escalation_stress_test
- cleanup_funding_ledger
- long_term_stewardship_fund
routes_to:
- '00'
- '01'
- '02'
- '04'
- '05'
- '421'
- '422'
- '423'
- '425'
- '428'
- '430'
- '431'
- '447'
- '459'
- '461'
- '463'
- '479'
- '480'
- '482'
- '483'
source_ids:
- S879
- S880
- S881
- S887
- S888
upstream_dependencies:
- nuclear_backend_finance_alignment
- nuclear_spent_fuel_backend_pathway
- nuclear_ratepayer_public_value_safeguard
downstream_consequences:
- decommissioning_financial_assurance_becomes_a_hard_cap
- trust_fund_shortfalls_are_exposed_as_public_value_gaps
- cleanup_and_long_term_stewardship_are_no_longer_externalities
equity_lenses:
- intergenerational_equity
- host_community_cleanup_rights
- ratepayer_protection
- taxpayer_backstop_transparency
degraded_modes:
- underfunded_decommissioning
- optimistic_cost_escalation_assumption
- fund_diversion
- unfunded_site_restoration
- spent_fuel_stranded_cost
evidence_grade: mixed
speculation_level: medium
revision_added: rev0299
status: canon
---

# 481 — Nuclear decommissioning trust, cleanup, and long-term stewardship financial assurance

## Audit function

This file makes decommissioning and cleanup financial assurance part of the nuclear-positive architecture. It distinguishes operating benefit from end-of-life cost closure: a plant can provide clean firm value while still failing maturity if decommissioning, spent-fuel, remediation, and long-term stewardship funding are not current and segregated.

## Nuclear-positive rule

The cube favors nuclear only when benefits do not depend on shifting end-of-life costs to future ratepayers, taxpayers, host communities, or waste custodians. Rev0299 therefore treats decommissioning trusts, funding status, escalation assumptions, cleanup cashflow, and long-term stewardship as hard gates.

## Refactor output

This file introduces `cube/nuclear-decommissioning-trust-oversight.csv`, `cube/nuclear-cleanup-recovery-funding.csv`, `cube/nuclear-financial-assurance-maturity-cap-execution.csv`, and publication controls for fund balances and local vulnerabilities.

## Sources

- [S879]
- [S880]
- [S881]
- [S887]
- [S888]
