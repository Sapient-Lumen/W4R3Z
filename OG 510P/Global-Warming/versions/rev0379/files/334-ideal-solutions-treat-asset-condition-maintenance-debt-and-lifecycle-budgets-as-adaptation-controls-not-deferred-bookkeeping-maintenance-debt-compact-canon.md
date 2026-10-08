---
id: '334'
revision_added: rev0273
status: canon
object_type: delivery_packet
domain_tags:
- maintenance
- asset_management
- infrastructure
- lifecycle
- public_finance
- resilience
- operations
service_floor:
- maintained_asset_floor
- lifecycle_budget_continuity
- asset_condition_visibility
hazard_tags:
- heat
- flood
- wildfire
- storm
- drought
- outage
- corrosion
- aging_infrastructure
- compound_shock
clock_tags:
- stock_turnover_clock
- finance_clock
- seasonal_clock
- learning_clock
- recovery_clock
actor_tags:
- asset_owner
- utility
- municipality
- regulator
- public_works_department
- transport_agency
- school_district
- housing_authority
- auditor
- funder
instrument_tags:
- inspect
- maintain
- budget
- rank
- repair
- replace
- decommission
- condition_assess
- publish
routes_to:
- '18'
- '22'
- '37'
- '39'
- '64'
- '130'
- '244'
- '250'
- '251'
- '253'
- '315'
- '324'
- '326'
- '330'
source_ids:
- S579
- S593
- S594
upstream_dependencies:
- asset_inventory
- condition_data
- maintenance_crews
- operating_budget
- procurement
- inspection_authority
- rate_or_tax_capacity
- public_records
downstream_consequences:
- service_interruption
- higher_repair_cost
- unsafe_reoccupancy
- cascade_failure
- public_trust_loss
- maladaptation
- stranded_new_capex
equity_lenses:
- low_income_neighborhoods
- rural_systems
- public_housing_residents
- school_children
- transit_dependent_people
- renters
- fenceline_communities
degraded_modes:
- preseason_patch
- temporary_service_reduction
- targeted_lifeline_maintenance
- mobile_backup
- asset_retirement_with_service_substitute
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- deferred_maintenance
- capital_bias
- invisible_operating_budget
- condition_data_gap
- political_preference_for_new_assets
- fragmented_ownership
- short_budget_cycle
failure_modes:
- resilience_capex_on_top_of_rotting_baseline
- new_project_politics_hides_maintenance_backlog
- asset_condition_unknown
- maintenance_staff_cut_first
- inspection_without_repair_money
- rebuild_repeats_fragility
proof_ledgers:
- asset_condition_register
- maintenance_backlog_log
- inspection_cycle
- criticality_score
- lifecycle_budget
- repair_completion_log
- failure_near_miss_log
- deferred_maintenance_risk_register
restoration_conflicts:
- new_build_vs_maintenance
- visible_ribbon_cutting_vs_invisible_reliability
- short_term_rate_pressure_vs_long_term_service
- asset_extension_vs_retirement
assurance_tests:
- condition_data_spot_check
- maintenance_backlog_stress_test
- budget_scenario_test
- near_miss_review
- preseason_critical_asset_walkdown
maintenance_state: condition_known_backlog_ranked_budgeted_and_rechecked
---

# 334 — Ideal Solutions: Treat asset condition, maintenance debt, and lifecycle budgets as adaptation controls, not deferred bookkeeping

## Claim

Adaptation fails when it adds climate features to neglected systems. **Maintenance debt is climate risk.**

A culvert that is half blocked, a roof past its design life, an unserviced pump, an aging transformer, a shelter HVAC system with no filters, a bridge with deferred inspection, a school with failing windows, a public-housing tower with broken elevators, or a drainage channel full of debris can turn a manageable hazard into a service-floor collapse.

The archive already values operations and maintenance. rev0273 makes the rule harder: every resilience claim should state the condition of the baseline asset. Global Center on Adaptation guidance emphasizes lifecycle integration [S579]. World Bank / G20 maintenance work says deferred maintenance has real economic and service consequences [S593]. OECD's lifecycle-governance work says infrastructure faces pressure to perform as crises and climate change become more frequent [S594].

## Compact rule

**No asset is climate-resilient if its condition is unknown.**

A serious packet includes:

- asset inventory and ownership;
- condition score and inspection cycle;
- criticality score by service consequence;
- maintenance backlog and funding gap;
- hazard exposure and climate stressors;
- repair, replacement, retirement, or service-substitution path;
- operating budget and staffing plan;
- public record of near misses and failures.

## Why this changes priority

Capital programmes often prefer new assets because they are visible, financeable, and politically attractive. But the service floor may need boring maintenance first: cleaning drains, replacing filters, servicing pumps, removing vegetation, clearing culverts, repairing roofs, replacing backup batteries, staffing inspection offices, fixing elevators, and testing generators.

The archive's priority rule is therefore: **fund the asset condition that protects the service floor, not the project category that sounds most modern.** Sometimes that means a solar microgrid. Sometimes it means a drain-cleaning crew. Sometimes it means retiring an asset and replacing the service with a safer route.

## Failure modes

The bad version of adaptation is a ribbon-cutting layer above a decaying base. It creates resilience hubs with failed HVAC. It builds new drainage while old culverts clog. It installs sensors but cuts maintenance staff. It hardens a facility that should be moved. It funds capital but not O&M. It treats inspection as compliance rather than repair authorization.

## Cube routing

Route this file whenever a packet involves infrastructure, buildings, schools, shelters, hospitals, water systems, drainage, roads, bridges, ports, grids, public housing, transit, labs, waste facilities, or resilience hubs. Pair with `250`, `251`, `253`, `315`, `324`, `326`, and `330`.

---
Citations point to `sources/register.md`.
