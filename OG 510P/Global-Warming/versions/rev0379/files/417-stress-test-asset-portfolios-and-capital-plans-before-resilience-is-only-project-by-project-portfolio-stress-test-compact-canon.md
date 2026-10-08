---
id: '417'
revision_added: rev0283
status: canon
object_type: audit
domain_tags:
- asset_portfolio
- capital_plan
- stress_testing
- infrastructure_asset_management
- public_finance
service_floor:
- asset_portfolio_stress_test
- portfolio_level_climate_risk
- capital_plan_risk_crosswalk
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
- asset_manager
- finance_officer
- public_works
- utility
- school_district
- health_system
- transport_agency
- auditor
instrument_tags:
- asset_inventory
- condition_rating
- climate_stress_test
- capital_plan_crosswalk
- criticality_score
- service_area_equity_map
- renewal_backlog
routes_to:
- '334'
- '356'
- '359'
- '408'
- '412'
- '414'
- '415'
- '419'
source_ids:
- S270
- S715
- S736
- S746
- S747
- S753
- S755
upstream_dependencies:
- infrastructure_asset_management
- model_governance
- readiness_scoring
- finance_stack
- maintenance_state
- service_floor_checklist
downstream_consequences:
- systemic_failure
- budget_shock
- inequitable_service_loss
- lost_grant_readiness
- asset_stranding
equity_lenses:
- small_utilities
- rural_counties
- low_income_service_users
- disabled_people
- students
- patients
- transit_dependent_households
degraded_modes:
- portfolio_triage
- critical_asset_hardening
- service_substitution
- renewal_deferral_with_monitoring
- temporary_capacity
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- projects_reviewed_one_by_one
- asset_inventory_stale
- criticality_not_mapped
- maintenance_backlog_hidden
- capital_plan_ignores_climate_scenarios
failure_modes:
- portfolio_blind_spot
- renewal_money_misallocated
- critical_service_failure
- fiscal_shock
- maintenance_debt_compounds
proof_ledgers:
- asset_inventory
- condition_and_criticality_log
- portfolio_stress_test
- capital_plan_crosswalk
- maintenance_backlog_register
- service_outage_scenario
asset_portfolio_stress_test: asset inventory and capital plan are stress-tested against climate scenarios, criticality,
  condition, maintenance backlog, and equity of service loss
---

# 417 — Stress-test asset portfolios and capital plans before resilience is only project by project

## Core claim

Project-by-project resilience is not enough. A bridge, school, pump station, clinic, road, substation, shelter, or data center can pass its own review while the portfolio still fails because dependencies, maintenance backlogs, renewal cycles, and fiscal constraints were never tested together.

NIST's community-resilience planning guide links social functions to buildings and infrastructure systems [S715]. The UN Handbook on Infrastructure Asset Management frames asset management as a local-capacity and sustainable-finance discipline [S746]. PIEVC resources include portfolio-level climate-risk assessment for infrastructure owners [S747]. ISO 55000's asset-management frame reinforces lifecycle value and risk [S755]. GFDRR's resilient-infrastructure work emphasizes mainstreaming disaster-risk management across infrastructure sectors [S753]. Climate-resilient infrastructure and financial-scenario materials add the point that resilience must enter capital planning and stress testing, not remain a project appendix [S736][S270].

## Portfolio packet

A portfolio stress test should include:

- asset inventory;
- condition and remaining useful life;
- climate exposure and design standard;
- service criticality;
- dependency on power, telecoms, access, staff, water, fuel, digital systems, or suppliers;
- maintenance backlog;
- renewal or replacement date;
- capital-plan funding source;
- equity of service loss if the asset fails.

## Capital-plan rule

Capital plans should not list climate resilience as a separate aspiration. Each capital line should indicate whether it maintains current service, reduces risk, creates new risk, preserves option value, or requires decommissioning.

## Cube rule

The field `asset_portfolio_stress_test` should mark whether an object has a portfolio-level inventory and scenario crosswalk. Blank means the archive may be overlearning from individual projects.

---
Citations point to `sources/register.md`.
