---
id: '418'
revision_added: rev0283
status: canon
object_type: integrity_gate
domain_tags:
- service_levels
- contracts
- permits
- handoff
- performance_obligation
- public_private_delivery
service_floor:
- resilience_service_level_contract
- handoff_acceptance_test
- performance_obligation_before_closeout
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
- capital_clock
- standards_clock
- land_use_clock
- learning_clock
- recovery_clock
actor_tags:
- procurement_officer
- contract_manager
- asset_owner
- regulator
- utility
- PPP_unit
- auditor
- community_monitor
instrument_tags:
- service_level_agreement
- performance_specification
- handoff_test
- availability_standard
- penalty_or_correction_clause
- public_acceptance_record
routes_to:
- '350'
- '356'
- '365'
- '371'
- '412'
- '414'
- '417'
- '420'
source_ids:
- S276
- S736
- S745
- S748
- S749
upstream_dependencies:
- model_governance
- performance_monitoring
- finance_stack
- procurement_integrity
- public_ledger
- asset_portfolio_stress_test
downstream_consequences:
- unrepaired_failure
- contract_dispute
- maintenance_gap
- public_trust_loss
- unfunded_liability
equity_lenses:
- low_income_service_users
- renters
- patients
- students
- transit_dependent_people
- people_without_legal_help
degraded_modes:
- temporary_service_level
- manual_override_clause
- public_step_in_right
- contingency_operator
- performance_bond_or_reserve
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- design_intent_not_contractual
- handoff_lacks_performance_test
- private_operator_not_bound_to_climate_conditions
- maintenance_obligation_vague
- dashboard_not_tied_to_remedy
failure_modes:
- asset_exists_without_service
- operator_avoids_repair
- public_pays_twice
- service_floor_unenforceable
- false_closeout
proof_ledgers:
- service_level_clause
- handoff_acceptance_record
- performance_dashboard
- remedy_log
- maintenance_clause
- availability_report
resilience_service_level_contract: contract, permit, grant, or handoff includes measurable climate-resilience service
  levels, acceptance tests, remedies, and public reporting
---

# 418 — Write resilience service levels into contracts, permits, and handoffs before performance is optional

## Core claim

A resilience objective that is not written into the contract, permit, grant agreement, concession, rate case, operating plan, or handoff test may not survive procurement, value engineering, turnover, or fiscal stress. Rev0283 adds the enforceability rule: service-floor claims need service-level obligations.

UNDRR's infrastructure principles emphasize critical-service continuity [S745]. Climate-resilient infrastructure guidance treats resilience as a project-development and implementation discipline [S736]. TCFD and IFRS S2 show the same governance pattern for corporate claims: strategy, risk, metrics, and targets must be decision-useful rather than aspirational [S748][S749]. Existing transition-plan guidance reinforces that claims need implementation detail [S276].

## Service-level packet

A resilience delivery agreement should specify:

- protected service floor;
- hazard or scenario under which it must operate;
- allowed degraded mode;
- maximum outage or recovery time;
- user groups protected;
- data to be reported;
- acceptance test before handoff;
- maintenance obligation;
- remedy, penalty, reserve, or step-in right;
- public reporting cadence.

## Handoff rule

Project completion is not service acceptance. Acceptance occurs only when the asset, operator, data system, maintenance budget, emergency procedure, user notification path, and remedy route have all passed the specified test.

## Cube rule

The field `resilience_service_level_contract` tests whether resilience has become an enforceable obligation. Blank means performance may be optional after ribbon-cutting.

---
Citations point to `sources/register.md`.
