---
id: '384'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- building_safety
- habitability
- inspection
- placards
- safe_return
- housing
- utility_reconnection
- permits
service_floor:
- building_safety_decision
- habitability_return_gate
- utility_reconnection_clearance
hazard_tags:
- earthquake
- flood
- wind
- wildfire
- smoke
- heat
- mold
- toxic_release
- outage
clock_tags:
- emergency_clock
- recovery_clock
- stock_turnover_clock
- learning_clock
actor_tags:
- building_department
- inspector
- engineer
- fire_marshal
- utility
- landlord
- tenant
- housing_agency
- legal_aid
instrument_tags:
- inspect
- placard
- restrict
- reconnect
- appeal
- repair
- document
routes_to:
- '287'
- '324'
- '352'
- '354'
- '355'
- '337'
- '348'
- '381'
- '382'
- '383'
source_ids:
- S692
upstream_dependencies:
- trained_evaluators
- access
- building_records
- utility_status
- legal_notice
- translation
- temporary_housing
downstream_consequences:
- injury
- carbon_monoxide_poisoning
- mold_exposure
- homelessness
- repair_delay
- insurance_claim_conflict
equity_lenses:
- renters
- multifamily_residents
- mobile_home_residents
- disabled_people
- older_adults
- low_income_homeowners
- informal_tenants
degraded_modes:
- rapid_external_evaluation
- temporary_restricted_use
- mobile_inspection_team
- paper_placard_registry
- tenant_safe_access_protocol
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- inspector_shortage
- placard_confusion
- tenant_displacement
- utility_reconnect_without_safety
- private_building_data_gap
- mold_hidden_damage
failure_modes:
- unsafe_return
- overly_broad_exclusion
- placard_not_appealable
- renter_loses_access_to_belongings
- utility_reconnected_to_unsafe_system
- repairs_begin_without_clearance
proof_ledgers:
- building_safety_evaluation_log
- placard_map
- utility_reconnection_clearance_log
- tenant_access_log
- appeal_log
- reinspection_queue
building_safety_placard_state: rapid/detailed evaluation, placard, utility clearance, reinspection, appeal, and
  tenant access path
---

# 384 — Ideal Solutions: Treat post-disaster building safety, habitability placards, utility reconnection, and safe return as recovery gates, not paperwork

## Core claim

Safe return is a service floor. A damaged building is not "recovering" until people know whether it can be entered, occupied, repaired, powered, cooled, insured, rented, or demolished. Post-disaster building safety evaluation is therefore not a narrow engineering afterthought. It is a gate for health, housing, utility reconnection, insurance, legal access, school reopening, small-business recovery, and public trust.

FEMA P-2055 and related post-disaster safety-assessment materials focus on the state of practice for evaluating structural and nonstructural safety and habitability after disasters [S692]. The climate cube turns that into an operating rule: every placard, restriction, reinspection, utility reconnection, and appeal should be part of the service-floor ledger.

## What the placard must mean

A placard should answer more than "red / yellow / green." It should make clear:

- what hazard or damage was evaluated;
- whether the decision is rapid, detailed, or provisional;
- what areas, uses, or systems are restricted;
- whether power, gas, water, elevator, HVAC, or fire protection can be reconnected;
- whether tenants may retrieve belongings safely;
- what repair or reinspection changes the status;
- where to appeal or request language / disability accommodation.

## The utility reconnection problem

Reconnection can become dangerous if it occurs before electrical, gas, water, sewer, fire, elevator, mold, or structural hazards are understood. The service-floor rule is not "restore utilities as fast as possible" in isolation. It is "restore utilities fast through a safety gate that does not strand low-income, renter, disabled, or multifamily users in indefinite limbo."

## Operating test

A jurisdiction passes this file only if it has trained evaluators, surge agreements, placard categories, multilingual tenant notice, utility reconnection rules, safe retrieval protocol, reinspection queue, appeal path, and a public map or private-safe ledger. The assessment must route to repair, temporary housing, insurance / assistance, code upgrade, buyout / retreat, or demolition, not just produce a colored sign.

## Cube rule

Any housing, school, shelter, workplace, utility, or business recovery packet should expose `building_safety_placard_state` if damaged structures control access. Blank means safe return is being assumed rather than governed.

---
Citations point to `sources/register.md`.
