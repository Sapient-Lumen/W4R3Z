---
id: '379'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- prepositioning
- logistics
- mutual_aid
- fuel
- spares
- shelter
- health
- cash
- safe_sites
service_floor:
- preimpact_prepositioning_status
- access_window_action
hazard_tags:
- flood
- wildfire
- storm
- heat
- smoke
- drought
- outage
- disease
- supply_chain_disruption
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- logistics_chief
- emergency_manager
- utility_operator
- public_health_agency
- procurement_officer
- humanitarian_agency
- community_organization
instrument_tags:
- stage
- move
- preclear
- procure
- standby
- demobilize
- reuse
- review
routes_to:
- '319'
- '323'
- '324'
- '332'
- '333'
- '339'
- '353'
- '361'
- '372'
- '373'
- '378'
source_ids:
- S672
upstream_dependencies:
- forecast_trigger
- staging_sites
- contracts
- routes
- fuel
- staffing
- inventory
- finance_release
downstream_consequences:
- access_closed
- late_supplies
- crew_stranded
- market_spike
- shelter_unready
equity_lenses:
- remote_community
- no_car_household
- informal_settlement
- care_facility
- small_utility
- small_business
degraded_modes:
- mobile_staging
- local_cache
- mutual_aid_standby
- community_distribution_point
- demobilization_reuse
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- trigger_too_late
- staging_site_in_hazard_zone
- contract_not_precleared
- demobilization_unclear
failure_modes:
- late_logistics
- wasted_false_alarm
- unreachable_cache
- prepositioning_inequity
proof_ledgers:
- prepositioning_status_board
- route_closure_clock
- inventory_release_log
- staging_site_safety_log
- demobilization_log
restoration_conflicts:
- speed_vs_cost
- central_cache_vs_local_need
- security_vs_public_visibility
- reuse_vs_specificity
assurance_tests:
- access_window_drill
- staging_site_pull_test
- contract_activation_test
- demobilization_after_false_alarm_review
anticipatory_finance_rule: preapproved_standby_and_release_costs
prepositioning_state: triggered_staging_with_access_window_clock
---
# 379 — Ideal Solutions: Pre-position people, supplies, contracts, mobile assets, and safe sites on trigger windows before impact closes access

## Core claim

A warning can create a narrow window when action is possible but access is still open. The archive already tracks recovery rails, mutual aid, spares, fuel, logistics, and emergency procurement. This file adds the pre-impact rule: **move before the road, port, grid, staffing pool, or market closes.**

Anticipatory systems often require pre-positioning of stock, readiness activities, and pre-agreed early actions [S672]. The forecast-to-action cube should treat pre-positioning as an operating status, not as generic preparedness.

## What can be pre-positioned

The list is broader than relief goods:

- fuel, generators, mobile batteries, charging, and black-start support;
- water, filters, pumps, chemicals, and repair clamps;
- mobile clinics, oxygen, dialysis transport, pharmacy caches, and cold chain;
- HEPA filters, masks, cooling supplies, water, electrolytes, and shade;
- road-clearing equipment, culvert crews, inspectors, and debris capacity;
- school, shelter, animal, and accessible transport resources;
- translation, call-center, rumor-control, and public-information staff;
- contracts, purchase orders, lodging, childcare, and payroll authority;
- cash-distribution agents, liquidity, vouchers, and grievance staff;
- mobile safe sites for remote, tribal, island, rural, and informal communities.

## The access-window clock

Each pre-positioning packet needs a latest-safe-departure time. For wildfire, flood, storm surge, cyclone, smoke, heat, or civil-disruption contexts, the clock may close before the hazard arrives. The cube should therefore record lead time, route vulnerability, staging area, owner, trigger, release authority, fallback, demobilization rule, and liability/insurance status.

## The anti-waste rule

Pre-positioning creates false-alarm costs. The answer is not to avoid staging; it is to prefer reusable, movable, no-regrets, or graduated assets where possible. A staged crew can inspect drains, check facilities, test generators, update shelter layouts, or conduct outreach even if the forecast shifts. The after-action ledger should ask whether the staged asset was useful, not only whether the exact predicted event occurred.

## Operating test

The file is operational only if a named owner can answer five questions before the event, not while the event is already unfolding:

1. What signal activates the action?
2. Who is authorized to act without waiting for a new meeting?
3. What money, staff, contracts, routes, and public messages are already pre-cleared?
4. Which households, workers, institutions, or places are likely to be missed by the nominal channel?
5. How will the decision be reviewed if the forecast misses, the hazard shifts, or the action causes harm?

A forecast, warning, model, dashboard, or alert is not a service floor by itself. It becomes a service floor only when it releases an owned action bundle with funding, authority, equity checks, degraded modes, public explanation, and after-action learning.

## Cube rule

Every trigger-facing packet should expose `forecast_trigger_rule`, `impact_based_decision_support`, `anticipatory_finance_rule`, `protective_action_authority`, `alert_interoperability_state`, `false_alarm_learning`, and `prepositioning_state` where relevant. Blank fields mean the cube should demote the readiness score, not assume the prose is sufficient.

---
Citations point to `sources/register.md`.
