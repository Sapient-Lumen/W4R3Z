---
id: '311'
revision_added: rev0270
status: canon
object_type: service_continuity
domain_tags:
- clean_air
- health
- wildfire_smoke
- indoor_air
- air_quality
service_floor:
- breathable_air
- cleaner_air_refuge
- respiratory_safety
hazard_tags:
- smoke
- air_pollution
- heat
- wildfire
- outage
- ozone
- dust
- contamination
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- public_health_agency
- school
- building_operator
- city
- employer
- housing_provider
instrument_tags:
- monitor
- warn
- filter
- ventilate
- shelter
- procure
- retrofit
- enforce
routes_to:
- '24'
- '252'
- '279'
- '280'
- '283'
- '285'
- '286'
- '287'
- '293'
- '294'
- '297'
- '306'
- '310'
- '436'
- '437'
source_ids:
- S551
- S552
- S553
- S554
- S555
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- filters
- hvac_capacity
- power
- shelter_access
- respirator_fit
- indoor_air_data
failure_modes:
- stay_inside_without_filtration
- unequal_refuge
- school_closure_sprawl
- worker_smoke_exposure
- polluted_recovery
proof_ledgers:
- aqi_record
- indoor_pm25_reading
- cleaner_air_space_map
- filter_delivery
- school_workplace_thresholds
---
# 311 — Ideal Solutions: Protect clean air as a climate-critical service during smoke, heat, pollution, and power stress

## Claim

Clean air is not only a mitigation co-benefit.
During wildfire smoke, extreme heat, dust, ozone episodes, industrial accidents, mold recovery, and power outages, **breathable air becomes a service floor**.

The archive already says climate policy should reduce combustion pollution.
This note adds the continuity rule: when outdoor air is unsafe, people need realistic indoor and public clean-air options, not just advice to stay inside.

WHO identifies ambient air pollution as a major health risk, with large mortality burdens and unequal exposure [S551]. State of Global Air 2025 reports air pollution as the leading environmental risk factor for death worldwide [S552]. EPA and CDC guidance on wildfire smoke warns that smoke can enter homes and that people may need cleaner indoor air, high-efficiency filtration, respirators, and symptom monitoring [S553][S554]. Health Canada guidance treats cleaner air spaces as community facilities that jurisdictions can identify and manage before smoke events [S555].

So the climate-service rule is simple: **a warning to breathe safer air is not complete unless safer air exists, is reachable, is powered, and is usable by people at highest risk.**

## Fast rule

**Every heat, smoke, wildfire, housing, school, care, worker, shelter, and outage packet should include a clean-air floor: outdoor monitoring, indoor filtration / ventilation strategy, public cleaner-air spaces, access support, thresholds, communications, and correction after exposure.**

## Clean-air continuity canon

### 1. Treat clean air as a service, not a lifestyle product

Air cleaners, sealed rooms, MERV filters, respirators, and HVAC upgrades cannot be left only to private purchase.
Low-income households, renters, schools, care homes, prisons, outdoor workers, unhoused people, and medically vulnerable people need public routes.

House rule: **a service floor cannot depend on the household already owning the equipment that proves the policy works.**

### 2. Distinguish outdoor warnings from indoor protection

AQI and smoke forecasts are necessary but insufficient.
A plan should also ask:

- which homes can actually keep smoke out;
- which public buildings can provide cleaner air;
- which schools can remain open safely;
- which shelters have filtration and power;
- which workplaces must stop, relocate, or provide respirators;
- which care facilities, clinics, and prisons have indoor-air thresholds;
- which households receive filters, box-fan kits where safe, or portable air cleaners.

House rule: **do not tell people to stay indoors if indoors is also unsafe.**

### 3. Build cleaner-air spaces before the smoke season

Cleaner-air spaces should be identified, upgraded, staffed, publicized, and connected to transport before smoke arrives.
They need:

- filtration and ventilation checks;
- backup power or priority restoration;
- water, toilets, cooling, seating, accessibility, and child-safe areas;
- language access and trusted communication;
- hours matched to risk;
- protocols for crowding, infection, and security without exclusion;
- after-action data on use and unmet demand.

House rule: **a cleaner-air space is not a label on a map; it is an operating promise.**

### 4. Pair smoke and heat policy

Heat and smoke often collide.
Closing windows may protect from smoke but worsen heat.
Ventilation may cool but import PM2.5.
Power outages can disable filtration and cooling at the same time.

The packet should therefore test combined events:

- heat + smoke;
- smoke + outage;
- heat + smoke + school day;
- smoke + outdoor work;
- smoke + evacuation;
- smoke + shelter crowding;
- smoke + mold / ash cleanup.

House rule: **clean air and thermal survivability must be solved together, not sequentially.**

### 5. Define institutional thresholds

Schools, care facilities, workplaces, prisons, shelters, and public buildings need clear thresholds for filtration mode, outdoor activity, relocation, closure, paid shutdown, remote service, or emergency transport.

Thresholds should be tied to:

- outdoor AQI / PM2.5;
- indoor PM2.5 where monitored;
- heat index / indoor temperature;
- medical vulnerability;
- staffing;
- power and HVAC status;
- transport access.

House rule: **if thresholds are undefined, decisions will be late, unequal, and blame-shifting.**

### 6. Protect cleanup workers and returnees

After wildfires, floods, and storms, air risks continue through ash, dust, mold, demolition, contaminated debris, generators, and open burning.
Recovery guidance should include PPE, respirators, ventilation, safe reentry, worker stop-work authority, debris controls, and household cleanup support.

House rule: **recovery is not safe if the air is treated as already recovered.**

## Minimum clean-air ledger

| Question | Evidence required |
|---|---|
| What is the air hazard? | smoke, PM2.5, ozone, dust, mold, ash, combustion, chemical release, indoor accumulation |
| Who cannot self-protect? | renters, children, older adults, disabled people, medically vulnerable people, outdoor workers, unhoused people, people in custody |
| Where is cleaner air available? | public map, capacity, accessibility, hours, power, filtration, cooling, toilets, transport |
| What threshold changes operations? | school, work, shelter, care, prison, transit, outdoor events, cleanup |
| What equipment exists? | filters, portable air cleaners, HVAC mode, respirators, fit / use guidance, backup power |
| What was measured? | outdoor AQI, indoor PM2.5, use of spaces, unmet demand, health calls, worker injury, complaints |

## What this routes to

- use `311` for wildfire smoke, air pollution, indoor air, cleaner-air shelters, smoke-ready schools, worker smoke exposure, AQI thresholds, ventilation / filtration, clean-air equipment, or smoke + heat + outage questions;
- pair with `306` for thermal survivability;
- pair with `279` / `280` for health and disease ecology;
- pair with `287` / `288` for housing and shelter;
- pair with `285` / `286` for worker protection;
- pair with `297` / `298` for power and filtration continuity.

## Compression rule

**Clean air is a climate-critical service. Smoke and pollution warnings are not enough; people need monitored air, filtered indoor space, powered cleaner-air refuges, institutional thresholds, access support, and correction ledgers when exposure falls on those least able to self-protect.**

---
Citations point to `sources/register.md`.
