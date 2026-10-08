---
id: '401'
revision_added: rev0281
status: canon
object_type: service_continuity
domain_tags:
- recovery_mobility
- transport_access
- vehicle_loss
- public_transit
- paratransit
- last_mile
- return_access
service_floor:
- recovery_mobility_access
- transport_to_recovery_services
- vehicle_and_transit_restoration
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- storm
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- legal_clock
- learning_clock
actor_tags:
- transport_agency
- paratransit_provider
- case_manager
- school_transport
- health_transport
- benefits_agency
- repair_contractor
- FTA_or_transit_authority
instrument_tags:
- emergency_transit
- paratransit_surge
- vehicle_repair_or_replacement
- fuel_or_charging_support
- shuttle
- route_status
- mobility_voucher
- access_map
routes_to:
- '295'
- '296'
- '316'
- '386'
- '391'
- '392'
- '393'
- '400'
source_ids:
- S721
- S722
upstream_dependencies:
- roads
- bridges
- transit_assets
- fuel_or_charging
- payment_rails
- casework_locations
- clinic_and_school_locations
- route_status_data
downstream_consequences:
- missed_medicine
- missed_school
- unemployment
- missed_deadlines
- unrepaired_homes
- food_insecurity
equity_lenses:
- no_car_households
- disabled_people
- older_adults
- rural_households
- students
- workers
- people_in_shelters_or_hotels
- limited_english_households
degraded_modes:
- mobile_service_delivery
- community_shuttle
- paper_trip_voucher
- phone_dispatch
- temporary_paratransit_eligibility
- fuel_or_charging_token
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- aid_sites_far_from_no_car_households
- primary_vehicle_damage_not_routed
- transit_restoration_aims_at_commute_not_recovery_need
- paratransit_capacity_overloaded
- fuel_or_charging_unavailable
failure_modes:
- household_misses_clinic_school_benefit_or_job
- shelter_exit_fails
- repair_access_delayed
- isolation_of_disabled_or_rural_people
- income_loss
proof_ledgers:
- recovery_trip_demand_map
- vehicle_loss_log
- transit_restoration_status
- paratransit_wait_time
- fuel_charging_access_log
- mobile_service_route_log
recovery_mobility_access: recovery-critical trips are mapped, prioritized, and served through transit, paratransit,
  vehicle support, fuel/charging, shuttles, mobile services, or route-to-need alternatives
---

# 401 — Maintain recovery mobility to jobs, schools, clinics, benefits, and repair sites before access fails

## Core claim

Recovery is spatial. People must reach jobs, schools, clinics, dialysis, pharmacies, food, benefits, legal help, inspectors, repair sites, banks, and family. If transport recovery only restores general traffic or commuter routes, the people with the most recovery tasks may remain stranded.

FEMA individual assistance can include transportation and other needs after disaster [S721]. FTA's Emergency Relief Program helps public transit systems protect, repair, or replace equipment and facilities after emergencies and natural disasters [S722]. The archive's addition is a trip-purpose rule: recovery mobility should be scored by whether recovery-critical trips can happen, not only whether roads or routes are nominally open.

## Recovery mobility packet

The packet should include:

- damaged primary-vehicle intake and repair/replacement route;
- transit and paratransit restoration priority for shelters, clinics, schools, benefits, pharmacies, food, and job sites;
- mobile benefit / clinic / legal services where trips are impossible;
- fuel and charging support;
- route-status information in accessible formats;
- rural, island, tribal, and last-mile alternatives;
- trip vouchers or shuttles linked to casework.

## Access-not-traffic rule

A reopened road is not enough. The test is whether households without reliable cars, phones, credit cards, fuel, disability accommodations, or local knowledge can make the trips recovery requires.

## Cube rule

All stabilization and durable-recovery packets should expose `recovery_mobility_access`. Blank means the archive should assume assistance exists somewhere but may not be reachable.

---
Citations point to `sources/register.md`.
