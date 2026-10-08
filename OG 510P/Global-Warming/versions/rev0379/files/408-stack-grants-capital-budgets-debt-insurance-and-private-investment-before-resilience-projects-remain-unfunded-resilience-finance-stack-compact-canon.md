---
id: '408'
revision_added: rev0282
status: canon
object_type: finance
domain_tags:
- resilience_finance
- capital_budget
- grant_stacking
- match
- debt
- adaptation_investment
service_floor:
- resilience_finance_stack
- project_match_and_cashflow
- capital_budget_integration
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- storm
- drought
- sea_level
- smoke
clock_tags:
- recovery_clock
- capital_clock
- standards_clock
- land_use_clock
- learning_clock
actor_tags:
- finance_officer
- grant_manager
- capital_budget_officer
- insurer
- development_bank
- utility
- private_owner
- community_lender
instrument_tags:
- grant_stack
- capital_improvement_plan
- bond
- revolving_fund
- insurance_incentive
- concessional_finance
- local_match
- contingency_budget
routes_to:
- '351'
- '356'
- '359'
- '360'
- '405'
- '409'
- '411'
- '412'
source_ids:
- S490
- S622
- S623
- S626
- S736
- S737
upstream_dependencies:
- mitigation_pipeline
- benefit_cost_equity_test
- capital_budget_calendar
- procurement_readiness
- local_match
downstream_consequences:
- project_delay
- fiscal_stress
- maladapted_repair
- unfunded_maintenance
- adaptation_inequality
equity_lenses:
- low_capacity_jurisdictions
- small_utilities
- low_income_ratepayers
- tribal_governments
- small_businesses
- renters
degraded_modes:
- phased_project
- technical_assistance_award
- match_waiver_request
- regional_pooling
- temporary_protection_with_upgrade_path
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- match_gap
- reimbursement_lag
- credit_constraints
- grant_writer_shortage
- private_benefit_public_cost
- OandM_unfunded
failure_modes:
- project_ready_but_unfunded
- money_flows_to_capacity_rich_applicants
- resilience_improvement_creates_affordability_pressure
- grant_funds_build_without_maintenance
proof_ledgers:
- funding_stack_table
- match_source_log
- cashflow_forecast
- debt_capacity_check
- OandM_budget
- affordability_impact_note
resilience_finance_stack: requires funding sources, match, cashflow, debt capacity, affordability, procurement,
  and lifecycle O&M before project approval is treated as readiness
---

# 408 — Stack grants, capital budgets, debt, insurance, and private investment before resilience projects remain unfunded

## Core claim

A resilience project is not real because it is eligible. It becomes real when the money, match, cash flow, procurement, maintenance, and affordability effects are governed together. Otherwise the archive confuses a grant opportunity with risk reduction.

HMGP and HMA can finance mitigation work after disasters or through mitigation programs [S623][S622]. GFOA's cost-documentation guidance shows why reimbursement and audit records are themselves recovery rails [S626]. OECD and climate-resilient infrastructure finance guidance emphasize that adaptation investment needs enabling policy, bankable pipelines, and financing models, not only needs assessments [S736][S737]. The World Bank's lifelines framing reinforces that resilient infrastructure protects service continuity, not just asset value [S490].

## Finance-stack rule

Each project should state:

- planning / scoping funds;
- design and permitting funds;
- construction funds;
- local match and cash-flow bridge;
- debt or ratepayer exposure;
- private-owner contribution, if any;
- affordability protection;
- operations, maintenance, monitoring, and replacement funds.

## Equity rule

A competitive grant system can reward administrative capacity rather than risk need. Technical assistance, regional pooling, pre-approved scopes, match relief, and community-benefit tests should be treated as finance instruments, not optional charity.

## Cube rule

All mitigation-pipeline rows should expose `resilience_finance_stack`. Blank means the archive should assume the project is a concept, not a funded risk-reduction pathway.

---
Citations point to `sources/register.md`.
