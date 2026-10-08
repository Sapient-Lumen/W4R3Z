---
id: '323'
revision_added: rev0272
status: canon
object_type: service_continuity
domain_tags:
- energy
- fuel
- blackstart
- critical_loads
- charging
- microgrids
- resilience_hubs
- backup_power
service_floor:
- emergency_energy_input_continuity
- blackstart_readiness
- critical_load_power
- critical_mobility_energy
hazard_tags:
- outage
- heat
- cold
- flood
- wildfire
- storm
- cyber
- supply_chain
- compound_shock
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- stock_turnover_clock
- learning_clock
actor_tags:
- utility
- fuel_supplier
- emergency_manager
- transport_operator
- hospital
- water_utility
- telecom_operator
- resilience_hub
- regulator
instrument_tags:
- prioritize
- prearrange
- stockpile
- rotate
- allocate
- test
- electrify
- island
- restore
routes_to:
- '252'
- '297'
- '298'
- '303'
- '308'
- '316'
- '317'
- '318'
- '319'
- '322'
source_ids:
- S499
- S510
- S511
- S576
upstream_dependencies:
- fuel_supply
- fuel_waivers
- drivers
- roads
- ports
- payment_rails
- telecoms
- cyber
- maintenance_crews
- blackstart_resources
- gas_electric_coordination
downstream_consequences:
- water_failure
- telecom_failure
- hospital_surge
- missed_dialysis
- food_cold_chain_loss
- payment_failure
- shelter_failure
- responder_delay
equity_lenses:
- medically_dependent_people
- older_adults
- disabled_people
- rural_communities
- low_income_households
- people_without_cars
- critical_workers
degraded_modes:
- manual_fuel_allocation
- priority_delivery_routes
- islanded_microgrid
- mobile_battery_or_generator
- cleaner_air_powered_hub
- paper_critical_load_list
- fuel_card_bypass
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- fuel_delivery
- blackstart_dependency
- generator_maintenance
- battery_state_of_charge
- critical_load_list
- supplier_contracts
- fuel_quality
- driver_access
- gas_electric_coordination
failure_modes:
- generator_without_fuel
- blackstart_resource_unavailable
- critical_load_not_prioritized
- diesel_lock_in
- fuel_card_failure
- charger_without_power
- resilience_hub_dark
- priority_list_capture
proof_ledgers:
- critical_load_register
- fuel_inventory_and_turnover_log
- blackstart_drill_record
- generator_maintenance_log
- battery_state_of_charge_log
- fuel_allocation_log
- critical_charger_status_map
restoration_conflicts:
- hospital_vs_water_vs_telecom_fuel
- generator_fuel_vs_evacuation_fuel
- blackstart_fuel_vs_public_safety_fuel
- short_term_diesel_vs_clean_resilience
assurance_tests:
- seven_day_energy_input_outage_drill
- blackstart_coordination_tabletop
- fuel_supplier_failover_test
- critical_load_field_verification
- clean_backup_transition_audit
---

# 323 — Ideal Solutions: Protect emergency fuel, black-start, critical charging, and energy inputs as climate-critical services

## Claim

rev0267 made electricity continuity a service floor. rev0271 made hidden rails visible. This file adds the most awkward energy rail: **during climate shocks, fuel, black-start capability, generator logistics, batteries, critical charging, and energy-input allocation are climate-critical services, not back-office details.**

The long-term doctrine is still electrification, efficiency, demand flexibility, microgrids, storage, and clean firming. But the live-shock doctrine must face the transitional fact that many life-safety systems still depend on liquid fuel, gas-electric coordination, maintained generators, and priority energy logistics. DOE already advises local leaders to plan emergency fuel, maintain supplies in multiple locations, keep fuel fresh, arrange supplier relationships, and define priority end users [S499]. FERC's blackstart work adds the grid-scale point: restart after a blackout requires stronger gas-electric collaboration and planning, not merely installed capacity [S576].

House rule: **do not pretend diesel is the resilience solution; also do not write climate plans that silently assume fuel, black-start, batteries, and charging will appear when the outage begins.**

## Fast rule

**Every critical-service packet that depends on backup power must name its energy input, fuel or charging path, black-start or islanding assumption, maintenance duty, allocation priority, and clean-backup transition plan.**

## The compact canon

### 1. Name the energy input, not just the asset

A generator is not continuity. A battery is not continuity. A microgrid is not continuity. Continuity is the governed chain: equipment, fuel or charge, maintenance, switching, controls, staff, access, priority, cyber recovery, payment, and a tested degraded mode.

Critical loads should be verified in the field: water pumps, wastewater lift stations, hospitals, pharmacies, oxygen systems, dialysis, telecoms, shelters, cooling / clean-air hubs, traffic control, dispatch, payment/cash sites, food cold chains, and fuel sites themselves. The register should include runtime, input type, refill route, maintenance status, emissions / ventilation risk, ownership, and who can authorize operation.

### 2. Treat fuel as a bridge with a sunset path

Emergency fuel can save lives, but it can also preserve dirty, fragile, isolated backup systems. The correct doctrine is transitional discipline: prearrange fuel where needed, prioritize it transparently, and use every replacement cycle to shift toward efficiency, islandable solar + storage, thermal storage, demand controls, clean firming, and shared resilience hubs where feasible [S510][S511].

A fuel plan should therefore carry two dates: the next emergency drill and the next clean-backup replacement opportunity.

### 3. Black-start is a dependency, not a technical footnote

Many continuity plans assume the grid comes back. But a severe outage can require black-start resources, transmission restoration, gas-electric coordination, communications, field crews, and cold-load pickup management before ordinary service returns. Where gas, telecoms, water, transport, and power mutually depend on one another, restart sequences should be rehearsed as dependency graphs.

### 4. Allocate energy by service consequence

Energy-input priority should not follow whoever has the loudest request, best contract, or most political leverage. It should follow service consequence: lives, water, medical products, communications, shelter, food, public safety, payments, and restoration crews. The allocation ledger should record who got fuel or charging priority, who was deferred, why, and what compensating measures were offered.

### 5. Make cleaner backup inspectable

A clean-backup claim should prove runtime, islanding, maintenance, cyber fallback, indoor-air safety, user access, staff training, and restoration coordination. A resilience hub that cannot power filtration, cooling, water, communications, device charging, medical-device support, and basic registration under outage is a sign, not a service floor.

## Minimum readiness ledger

| Test | Minimum evidence | Failure signal |
|---|---|---|
| critical-load register | field-verified list with runtime, input type, owner, contact, and priority class | unknown loads compete during outage |
| fuel / charge continuity | inventory, supplier contracts, turnover, delivery routes, manual purchase authority | generator exists but cannot run |
| black-start / islanding | black-start drill, microgrid test, switching protocol, cyber fallback | system cannot restart after major blackout |
| clean-backup transition | replacement-cycle plan, emissions/ventilation controls, battery/storage readiness | diesel emergency becomes permanent infrastructure |

## Bottom line

Emergency energy inputs are a bridge rail. The archive should govern them honestly: protect life-safety service today, expose dependency, allocate by service consequence, and use each replacement cycle to move from fragile combustion backup toward tested clean resilience.

---
Citations point to `sources/register.md`.
