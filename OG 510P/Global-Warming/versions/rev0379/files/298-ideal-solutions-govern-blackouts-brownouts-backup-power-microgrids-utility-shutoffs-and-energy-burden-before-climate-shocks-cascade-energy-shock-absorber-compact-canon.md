---
id: '298'
revision_added: rev0267
status: canon
object_type: shock_absorber
domain_tags:
- energy
- outage
- utility
- backup_power
- microgrids
- affordability
service_floor:
- energy_shock_absorber
- outage_resilience
- utility_affordability
hazard_tags:
- blackout
- brownout
- heat
- cold
- storm
- wildfire
- flood
- cyber
- fuel_shortage
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- utility
- regulator
- emergency_manager
- local_government
- energy_office
- social_protection_agency
instrument_tags:
- pre_stage
- prioritize
- island
- compensate
- subsidize
- reconnect
- audit
- sunset
routes_to:
- '297'
- '252'
- '253'
- '279'
- '283'
- '289'
- '290'
- '306'
- '311'
- '316'
- '317'
source_ids:
- S502
- S503
- S505
- S506
- S507
- S508
- S509
- S510
- S511
- S512
- S513
- S514
- S515
- S518
- S532
upstream_dependencies:
- fuel_or_charging
- grid_controls
- telecoms
- cyber
- staff
- spare_parts
- payment_support
downstream_consequences:
- medical_device_failure
- payment_failure
- water_failure
- food_spoilage
- indoor_air_failure
- heat_death
equity_lenses:
- energy_burdened_households
- medically_dependent_people
- rural_households
- renters
- informal_workers
- custodial_populations
degraded_modes:
- targeted_load_support
- clean_backup
- battery_hub
- emergency_tariff_relief
- paper_reconnection_process
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- restoration_priority
- backup_fuel
- interconnection
- generator_maintenance
- shutoff_rules
- household_cash
failure_modes:
- backup_theatre
- fossil_fallback_lock_in
- unowned_restoration_priority
- energy_burden_cascade
proof_ledgers:
- restoration_priority_log
- backup_fuel_log
- microgrid_dispatch_log
- shutoff_moratorium_log
- arrears_relief_log
restoration_conflicts:
- fuel_allocation
- grid_repair_order
- critical_facility_vs_household_load
- clean_backup_vs_diesel_emergency
assurance_tests:
- seventy_two_hour_outage_drill
- critical_facility_islanding_test
- utility_shutoff_heat_audit
---
# 298 — Ideal Solutions: Govern blackouts, brownouts, backup power, microgrids, utility shutoffs, and energy burden before climate shocks cascade

## Claim

File `297` defines energy continuity as a climate-critical service. This file defines the **energy shock absorber**: the operational machinery that prevents power stress from cascading into unsafe homes, failed medical devices, failed water systems, broken communications, food spoilage, payment failure, transport paralysis, care collapse, debt, eviction, and preventable death.

The shock absorber must work for outages, brownouts, planned safety shutoffs, heat-driven peak stress, cold snaps, wildfire / smoke, floods, hurricanes, drought-linked hydropower / cooling constraints, cyber incidents, fuel interruptions, equipment failure, and fast-growing load. [S502] [S503] [S505] [S506] [S507] [S508]

## Cascade map

Climate shock or system stress → generation / transmission / distribution / fuel / communications / payment / workforce disruption → outage or curtailment → heat / cold exposure, medical-device failure, water pressure loss, wastewater overflow, alert failure, transport / charging / fuel failure, food spoilage, business closure, school closure, benefit access failure, arrears, shutoff, informal coping, unsafe generators, fire / carbon monoxide risk, displacement, and rights loss.

The absorber interrupts the cascade before outage becomes social failure.

## Shock-absorber canon

1. **Trigger extended-outage planning before the lights go out.** Heat, cold, smoke, wildfire, flood, storm, drought, cyber, and fuel-risk forecasts should activate critical-load review, backup testing, hub staffing, medically dependent outreach, fuel / battery logistics, and public communication.

2. **Segment outages by duration, geography, and consequence.** A four-hour outage, a 24-hour outage, a 72-hour outage, and a multi-week outage are different emergencies. Urban high-rise housing, rural feeders, informal settlements, islands, flood-isolated neighborhoods, and medically dependent households need different plans.

3. **Use a critical-load ladder.** Define which loads are life-safety, health, water / sanitation, communications, transport, food, housing, finance / benefit access, and ordinary service. Every load-shed, microgrid islanding, restoration, and demand-response action must know which rung it is cutting.

4. **Restore by service consequence.** Customer count alone is not enough. Restoration must account for critical services, medically dependent people, long-term-care facilities, water and wastewater assets, communications, cooling / warming centers, shelters, elevators, transport depots, fuel / charging hubs, and food cold-chain nodes. [S509]

5. **Protect medically dependent people at home.** The absorber must include privacy-preserving registries, opt-in outreach, equipment and battery support, backup charging, transport to powered sites, caregiver routing, shelter options, pharmacy continuity, and follow-up after restoration. [S512]

6. **Exercise healthcare black-sky operation.** Health facilities must drill generator / battery / microgrid operation, fuel resupply, cold-chain continuity, oxygen, dialysis, lab, pharmacy, IT, elevators, sterilization, HVAC, and surge staffing under long outages. [S513]

7. **Bind water and wastewater to energy restoration.** Electric utilities, emergency managers, water utilities, and wastewater operators need shared priority lists, contact protocols, mobile generation, fuel plans, spares, and public boil-water / sanitation messaging. [S514]

8. **Keep resilience hubs operational, not symbolic.** Hubs must publish what they can actually provide: hours of operation, power capacity, cooling / heating, charging, refrigeration, water, communications, first aid, language access, disability access, transport links, security, staffing, supplies, and rules for pets / service animals / family units. [S510] [S518]

9. **Give microgrids and solar-plus-storage a black-sky operating envelope.** Every project should define islanding, critical loads, fuel / battery autonomy, recharge assumptions, seasonal performance, maintenance, cyber/manual mode, public access, ownership, and cost recovery. [S511] [S518]

10. **Allocate backup fuel and batteries as public goods during crisis.** Fuel, portable batteries, charging stations, mobile generators, repair crews, and spares must be prioritized by service consequence, not political visibility.

11. **Power communications, payment, and route-status channels.** Alerts, local radio, cell towers, broadband, emergency call centers, ATMs, point-of-sale, benefit-card systems, traffic signals, depot dispatch, charging networks, fuel pumps, route feeds, and public status dashboards need backup and fallback modes.

12. **Treat shutoffs and arrears as shock multipliers.** Emergency moratoria, reconnection support, bill credits, arrears management, energy-efficiency support, and benefit access belong in outage planning because unaffordable power is a service break before the storm arrives. [S515]

13. **Make demand response fair and visible.** Emergency curtailment should protect critical uses, compensate participants, avoid hidden penalties, publish distributional impacts, and include opt-outs or overrides for care, health, disability, refrigeration, communications, and livelihood-critical uses.

14. **Make large loads reliability citizens.** Data centers, industrial electrification, charging depots, ports, cold chains, and other large loads must carry demand flexibility, backup, grid-upgrade, local-service, water, land, and restoration obligations proportional to their system impact. [S507]

15. **Prepare spares, workforce, vegetation, and mutual aid.** Resilience is not only equipment. It requires trained crews, mutual-aid compacts, vegetation management, spare transformers and switches, staging areas, safe worker conditions, security, repair access, and route-clearing coordination.

16. **Build cyber and manual fallback into energy operations.** Smart-grid, demand-response, microgrid, charging, metering, payment, communications, and outage-management platforms need offline operating procedures and manual restoration paths.

17. **Exit dirty emergency dependence deliberately.** Transitional diesel use may remain necessary, but each plan must reduce avoidable generator use through efficiency, passive survivability, batteries, clean distributed generation, thermal storage, shared hubs, and clean-fuel plans where credible.

18. **Publish the after-action correction ledger.** Outage reviews should identify distributional duration, critical-service failures, failed backups, communication gaps, carbon monoxide / fire harms, shutoffs, bills, complaints, restoration decisions, missed medically dependent households, and required upgrades.

## Minimum energy-shock-absorber ledger

| Question | Evidence required |
|---|---|
| What failed? | Feeder, asset, fuel chain, software, communications, workforce, payment, backup, or governance failure. |
| Who lost service? | Duration by neighborhood, household type, facility, medically dependent status, tenure, income, disability, age, language, rural / urban, and digital access where privacy permits. |
| Which critical loads were protected? | Facility and home-load status, degraded-service level, backup duration, fuel / battery status, and unmet need. |
| What cascaded? | Health, WASH, transport, food, housing, finance, legal, school, care, communication, and recovery consequences. |
| What restored first? | Public restoration rationale, deviations, appeals, and equity check. |
| What will change? | Funded upgrades, maintenance, affordability protections, hub changes, registry changes, mutual-aid changes, and regulatory orders. |

## What this file routes to

- use `297` first if the question is about energy continuity as a service floor
- use this file when the prompt asks about outages, brownouts, backup power, microgrids, resilience hubs, critical loads, utility shutoffs, planned safety shutoffs, load shedding, energy burden, or outage restoration
- pair with `293` / `294` when warning and telecom channels need backup power
- pair with `295` / `296` when transport, charging, fuel, depots, ports, or freight need energy continuity
- pair with `277` / `278` when water or wastewater assets depend on power
- pair with `279` / `280`, `283` / `284`, and `281` / `282` when health, care, disability, medical dependence, schools, childcare, and child protection are at stake
- pair with `287` / `288`, `289` / `290`, and `291` / `292` when housing, bills, debt, benefit access, legal identity, or remedies fail during outages

## What this rules out

It rules out outage planning that protects infrastructure but not people. It rules out restoration that optimizes only average customer minutes. It rules out resilience hubs with no operating envelope. It rules out microgrids with no public-service obligation. It rules out utility affordability policy that starts after disconnection. It rules out load shedding that hides who is being cut. It rules out climate plans that electrify everything but do not govern degraded operation.

## Compression rule

**An outage is not only an energy event. It is a cascade test of the entire climate state.**

## Rev0268 energy-shock bridge — blackout recovery must govern waste streams

Energy shock absorbers now plan for spoiled food, failed compactors, downed wires in debris, generator hazards, battery / e-waste hazards, landfill / transfer backup, medical-waste refrigeration, and cleanup fleet charging / fueling. A blackout after-action ledger should record waste and environmental-health cascades. Pair with `299` and `300`. [S532]

---
Citations point to `sources/register.md`.
