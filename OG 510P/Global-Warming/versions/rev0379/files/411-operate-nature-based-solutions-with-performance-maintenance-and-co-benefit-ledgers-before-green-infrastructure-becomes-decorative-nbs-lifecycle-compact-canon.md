---
id: '411'
revision_added: rev0282
status: canon
object_type: service_continuity
domain_tags:
- nature_based_solutions
- green_infrastructure
- ecosystem_services
- flood_risk
- heat_risk
- water_quality
- coastal_buffer
service_floor:
- nature_based_solution_lifecycle
- ecosystem_buffer_performance
- green_infrastructure_OandM
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
- parks_department
- stormwater_utility
- public_works
- watershed_authority
- land_trust
- tribal_government
- community_group
- ecologist
instrument_tags:
- NBS_project_plan
- performance_metric
- maintenance_plan
- ecological_monitoring
- land_stewardship_agreement
- co_benefit_ledger
- adaptive_management
routes_to:
- '12'
- '17'
- '24'
- '326'
- '347'
- '405'
- '408'
- '409'
- '412'
source_ids:
- S736
- S738
- S739
upstream_dependencies:
- land_access
- water_rights
- maintenance_budget
- ecological_design
- community_stewardship
- monitoring_capacity
downstream_consequences:
- flood_storage_loss
- urban_heat_inequity
- water_quality_decline
- habitat_failure
- trust_loss
equity_lenses:
- shade_deserts
- floodplain_communities
- tribal_stewards
- renters_near_green_amenities
- low_income_neighborhoods
- downstream_communities
degraded_modes:
- temporary_gray_green_hybrid
- stewardship_microgrant
- maintenance_trigger
- performance_recalibration
- public_failure_notice
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- maintenance_unfunded
- performance_uncertain
- land_tenure_unclear
- greenwashing_claims
- co_benefits_not_measured
- community_stewardship_unpaid
failure_modes:
- trees_planted_without_survival_plan
- wetland_restored_without_hydrology_protection
- NBS_used_to_delay_hard_protection_or_retreat
- benefits_claimed_without_monitoring
proof_ledgers:
- NBS_performance_log
- maintenance_schedule
- survival_or_condition_survey
- hydrology_monitoring
- co_benefit_ledger
- stewardship_budget
- failure_repair_log
nature_based_solution_lifecycle: requires design, land and water rights, performance targets, maintenance owner,
  ecological monitoring, co-benefit ledger, and adaptive-management trigger
---

# 411 — Operate nature-based solutions with performance, maintenance, and co-benefit ledgers before green infrastructure becomes decorative

## Core claim

Nature-based solutions are real infrastructure when they measurably reduce heat, flood, erosion, water-quality, drought, coastal, habitat, or service-continuity risk and have a lifecycle owner. They are not real infrastructure when planted, photographed, and abandoned.

FEMA's nature-based-solutions guide explicitly includes monitoring, tracking, and maintenance [S738]. World Bank NBS materials describe nature-based solutions as resilience tools that can complement or substitute for gray infrastructure in some contexts [S739]. Infrastructure-resilience finance guidance emphasizes lifecycle performance and benefits, not only capital completion [S736]. The archive's rule is therefore simple: no NBS claim without performance, maintenance, and adaptive-management proof.

## Lifecycle rule

Every NBS row should state:

- hazard and service floor it protects;
- design condition and failure condition;
- land / water / tenure authority;
- construction and establishment period;
- maintenance and stewardship owner;
- monitoring metric and frequency;
- co-benefits and possible harms;
- trigger for repair, redesign, or retirement.

## Anti-greenwashing rule

A project may be beautiful, popular, and beneficial while still not being risk reduction. If it cannot show the protected service, design condition, maintenance owner, and performance ledger, call it greening, not resilience.

## Cube rule

All ecosystem-buffer and green-infrastructure rows should expose `nature_based_solution_lifecycle`. Blank means the archive should assume the project may be decorative or under-maintained.

---
Citations point to `sources/register.md`.
