---
id: '374'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- evacuation
- shelter_in_place
- reentry
- protective_action
- transport_access
- civil_rights
service_floor:
- feasible_protective_action
- safe_evacuation_or_shelter_choice
hazard_tags:
- wildfire
- flood
- storm_surge
- toxic_release
- smoke
- heat
- violence
- outage
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- public_safety
- transport_operator
- shelter_operator
- school
- care_facility
- corrections_operator
- community_organization
instrument_tags:
- order
- advise
- evacuate
- shelter_in_place
- stage_reentry
- transport
- protect_rights
- appeal
routes_to:
- '295'
- '296'
- '337'
- '339'
- '340'
- '341'
- '345'
- '346'
- '372'
- '377'
source_ids:
- S676
- S677
upstream_dependencies:
- routes
- shelters
- fuel
- transport
- care_facility_rosters
- animal_shelter
- alert_channels
downstream_consequences:
- road_congestion
- unsafe_shelter
- abandoned_dependents
- unlawful_exclusion
- fatal_delay
equity_lenses:
- no_car
- pet_owner
- disability
- limited_english
- incarcerated_person
- migrant_worker
- rural_last_mile
degraded_modes:
- shelter_in_place
- vertical_evacuation
- bus_pickup
- facility_protect_in_place
- staged_reentry
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- evacuation_order_without_transport
- shelter_instruction_without_safe_building
- checkpoint_blocks_return
- facility_cannot_move
failure_modes:
- unmanaged_movement
- evacuation_trap
- shelter_abuse
- civil_rights_violation
- unsafe_reentry
proof_ledgers:
- protective_action_matrix
- route_status_log
- shelter_capacity_log
- transport_pickup_log
- reentry_appeal_log
restoration_conflicts:
- speed_vs_due_process
- evacuation_vs_shelter_risk
- property_security_vs_resident_return
- enforcement_vs_trust
assurance_tests:
- no_car_evacuation_drill
- facility_protect_in_place_test
- staged_reentry_tabletop
- checkpoint_civil_rights_audit
alert_interoperability_state: must_route_to_feasible_action
protective_action_authority: published_matrix_with_owner_and_appeal
---
# 374 — Ideal Solutions: Govern evacuation, shelter-in-place, staged return, and protective-action authority before alerts create unmanaged movement

## Core claim

Evacuation is not just a warning problem. It is a **protective-action authority** problem: who decides to move, shelter, stage, restrict, return, or hold people in place when routes, shelters, fuel, care responsibilities, prisons, hospitals, schools, animals, and toxic exposures are all constrained.

Existing files cover transport, shelter, animals, wildfire, reentry, public information, and safe refuge. This file binds them into one rule: an alert is not enough unless the protective action is feasible for the people receiving it. Ready.gov and FEMA guidance emphasize planning for evacuation and sheltering, and FEMA's people-first planning guidance stresses engaging underserved populations so plans reflect actual community needs [S676][S677].

## The protective-action matrix

Every jurisdiction should maintain a live matrix with at least these choices:

- evacuate now;
- prepare to evacuate;
- shelter in place;
- move vertically;
- relocate to clean air / cooling / medical refuge;
- restrict entry;
- allow staged reentry;
- protect-in-place for facilities that cannot move;
- activate transport for people without cars;
- activate animal/livestock route and shelter;
- issue worker, school, custody, and care-site orders.

Each row needs authority, thresholds, lead time, transport plan, route status, shelter capacity, medical/care constraints, communication mode, enforcement limits, civil-rights review, and appeal/correction path.

## The hardest users

A protective-action plan is not proven by a household with a car, cash, phone, English fluency, flexible job, and relatives outside the hazard zone. Test these paths instead:

- renter with no car and a pet;
- dialysis patient requiring transport and power;
- schoolchild whose caregiver cannot leave work;
- nursing-home resident in a smoke event;
- incarcerated person or immigration detainee;
- farmworker in employer-controlled housing;
- mobile-home park resident under tornado, wildfire, or flood warning;
- household afraid to pass checkpoints;
- tribal, island, or rural community with one road out.

## Anti-abuse rule

Protective action can become coercive or exclusionary. Curfews, checkpoints, access passes, evacuation orders, reentry denial, and shelter rules must be bounded by necessity, proportionality, public explanation, complaint channels, disability accommodation, language access, and independent review. A climate-ready state must be able to move people out of danger without using danger as an excuse for arbitrary policing or property exclusion.

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
