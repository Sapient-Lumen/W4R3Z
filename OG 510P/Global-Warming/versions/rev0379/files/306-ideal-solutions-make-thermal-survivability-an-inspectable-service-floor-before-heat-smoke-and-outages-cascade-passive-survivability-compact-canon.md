---
id: '306'
revision_added: rev0269
status: canon
object_type: service_continuity
domain_tags:
- heat
- thermal_survivability
- buildings
- cooling
- passive_design
- clean_air
service_floor:
- thermal_survivability
- passive_survivability
- safe_indoor_temperature
hazard_tags:
- heat
- humid_heat
- smoke
- outage
- wildfire
- urban_heat
- housing_insecurity
clock_tags:
- seasonal_clock
- emergency_clock
- stock_turnover_clock
- recovery_clock
actor_tags:
- building_owner
- housing_authority
- local_government
- public_health_agency
- school
- care_operator
instrument_tags:
- shade
- cool
- ventilate
- insulate
- retrofit
- inspect
- open
- subsidize
routes_to:
- '07'
- '13'
- '20'
- '24'
- '252'
- '283'
- '285'
- '287'
- '297'
- '311'
- '313'
- '314'
- '436'
- '437'
- '442'
- '443'
source_ids:
- S86
- S262
- S419
- S545
upstream_dependencies:
- buildings
- power
- water
- clean_air
- transport
- housing_rights
- public_health
- affordability
downstream_consequences:
- heat_illness
- school_closure
- care_failure
- hospital_surge
- labor_loss
- indoor_air_harm
equity_lenses:
- renters
- older_adults
- disabled_people
- outdoor_workers
- schoolchildren
- people_in_custody
- homeless_people
degraded_modes:
- passive_cooling
- cleaner_air_space
- shaded_route
- cool_room
- outage_safe_fan
- public_cooling_transport
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- indoor_heat_data
- rental_split_incentive
- outage_safe_cooling
- shade_gap
- cool_space_access
- building_codes
failure_modes:
- warning_without_survivability
- cooling_center_without_transport
- ac_without_affordability
- sealed_hot_box
- smoke_trapped_inside
proof_ledgers:
- indoor_temperature_log
- humidity_log
- cooling_space_map
- shade_inventory
- outage_safe_cooling_test
restoration_conflicts:
- ventilation_vs_smoke
- cooling_load_vs_grid_stress
- landlord_cost_vs_tenant_safety
assurance_tests:
- indoor_heat_drill
- cooling_space_access_test
- smoke_heat_outage_scenario
---
# 306 — Ideal Solutions: Make thermal survivability an inspectable service floor before heat, smoke, and outages cascade

## Claim

The archive already treats cooling, buildings, health, care, worker protection, housing, energy, and public safety as climate-critical.
But there is a missing compression: **thermal survivability**.

Thermal survivability means people can remain alive and reasonably safe indoors or in reachable public refuge during heat, smoke, cold snaps, or outages, without assuming every household can buy, power, maintain, or safely use mechanical cooling or heating.

This is not a lifestyle comfort category.
Heat is now a direct mortality, labour, school, care, housing, power, and public-safety threat. WHO says heat stress is a leading weather-related killer, and the 2025 Lancet Countdown reports worsening heat-related mortality and large labour-hour losses; WHO / WMO's 2025 workplace-heat guidance treats heat stress as a major worker-health and productivity problem. [S86] [S262] [S419]

A climate programme that decarbonizes buildings but cannot keep people alive during heat and outages is under-specified.
A programme that expands air conditioning without passive demand reduction, peak management, refrigerant discipline, affordability, clean power, and outage-safe refuge is also under-specified.

## Fast rule

**Every building, housing, school, care, shelter, workplace, health, energy, and urban-form packet should state its thermal-survivability floor: maximum safe indoor temperature / exposure, clean-air path, outage duration, reachable refuge, access support, and correction trigger.**

## Thermal-survivability canon

### 1. Name the survivability floor

A formed packet should specify:

- indoor heat threshold or heat-index / wet-bulb-informed trigger;
- maximum duration above threshold;
- smoke / air-quality threshold and clean-air room capability;
- cold-snap threshold where relevant;
- outage duration assumptions;
- people covered, including tenants, children, older adults, disabled people, medically dependent people, workers, prisoners, students, and people without stable housing;
- reachable cooling / warming / clean-air refuge;
- transport and communication support;
- duty to inspect, remedy, relocate, or close.

House rule: **thermal safety cannot be governed if no one names the threshold.**

### 2. Start with passive survivability

The first thermal-resilience resource is a building and urban fabric that reduces exposure before machines run.
Use shade, trees where water-feasible, cool roofs, reflective surfaces, insulation, airtightness where compatible with ventilation, solar control, operable windows where safe, cross-ventilation, thermal mass, exterior shutters, efficient envelopes, cool materials, moisture-safe construction, roof and wall upgrades, and heat-aware urban form.

House rule: **do not make the grid solve heat that design could have reduced.**

### 3. Use efficient mechanical cooling and heating, but do not make it the only safety plan

Efficient AC, heat pumps, fans, district cooling, thermal storage, and smart controls are essential in many places.
But thermal safety also needs affordability, maintenance, clean power, demand response, indoor-air quality, refrigerant management, and backup / refuge for outages.

House rule: **air conditioning without affordability, peak management, and outage fallback is a partial answer.**

### 4. Treat public refuge as critical infrastructure

Cooling centres, clean-air centres, warming centres, libraries, schools, community hubs, shelters, clinics, and resilience hubs should have access hours, transport, disability access, language access, water, toilets, charging, backup power, staff, safety protocols, and trusted outreach.

Global heat-action-plan assessments emphasize structured governance, partnerships, and persistent implementation challenges; the archive's rule is that public refuge must be an operating service, not a press release. [S545]

House rule: **a cooling centre people cannot reach, trust, use, or remain in is not a cooling centre.**

### 5. Make housing habitability heat-aware

Habitability rules often lag climate reality.
The packet should define landlord duties, tenant remedies, rent protections during unsafe heat, cooling-equipment repair timelines, utility-shutoff protections, temporary accommodation triggers, mold / moisture interactions, and no-retaliation rules.

House rule: **a rental unit can be legally occupied and thermally unsafe at the same time unless the law catches up.**

### 6. Make schools, care homes, prisons, and institutions inspectable

People in institutions cannot freely leave.
Thermal-survivability standards should apply to schools, childcare, care homes, hospitals, shelters, prisons, detention centres, group homes, and workplaces with captive or dependent populations.

The standard should cover indoor temperature, air quality, staffing, hydration, medication, evacuation, backup power, shaded outdoor space, activity modification, and closure / relocation.

House rule: **where people cannot self-rescue, the institution owns a higher floor.**

### 7. Protect workers without making heat safety unpaid

Heat rules should include thresholds, work-rest cycles, shade, water, cool rest areas, schedule changes, acclimatization, PPE compatibility, paid pauses, stop-work authority, transport, and wage protection.

WHO / WMO's workplace-heat report emphasizes evidence-based prevention and heat-action programmes; the archive adds that unpaid heat safety becomes non-safety for workers living paycheck to paycheck. [S419]

House rule: **heat safety that workers cannot afford to use is decorative.**

### 8. Couple thermal survivability to energy continuity

A heat plan fails when power fails.
An energy plan fails when it restores general load but misses cooling, elevators, oxygen, refrigeration, fans, pumps, and clean-air spaces.
The packet should name critical cooling loads, restoration priority, resilience hubs, medically dependent power, building-level passive duration, battery / thermal storage, and load-shed safeguards.

House rule: **thermal survivability is one of the tests of energy continuity.**

### 9. Couple thermal survivability to water, air, and health

Heat exposure worsens dehydration, kidney stress, cardiovascular and respiratory disease, pregnancy risks, mental-health crises, medication risks, and worker injury.
Smoke and heat combine through indoor-air quality and ventilation decisions.
The packet should include water access, cooling / clean-air guidance, health surveillance, pharmacy and medicine continuity, wellness checks, and public communication.

House rule: **thermal safety is not only a building metric; it is a health-system trigger.**

### 10. Measure indoor conditions, not only outdoor weather

Outdoor heat warnings are necessary but insufficient.
Thermal survivability needs indoor-temperature data, building archetype risk, utility disconnection data, emergency-call data, school and care closure data, workplace injury data, and tenant / resident complaints.

The data should be privacy-preserving and remedy-linked.

House rule: **people die indoors; measure the indoor risk.**

### 11. Avoid maladaptive cooling

Thermal policy can worsen emissions, peaks, water stress, refrigerant leakage, inequity, and outage risk.
The packet should pair cooling access with efficiency standards, demand response, passive measures, clean power, refrigerant management, heat-island reduction, affordability, and public refuge.

House rule: **thermal safety and mitigation should be designed together, not traded off after the fact.**

### 12. Create a thermal after-action ledger

After heat, smoke, cold, or outage events, the ledger should record:

- indoor temperature and duration where available;
- deaths, emergency calls, hospitalizations, worker injuries, school closures, care-home incidents;
- utility shutoffs and outage duration;
- cooling-centre use and non-use;
- transport barriers;
- tenant complaints and repair times;
- public-housing and informal-settlement failures;
- deaths among socially isolated people;
- communities with no safe refuge;
- corrections funded before the next season.

House rule: **a heat season should leave behind a retrofit, refuge, labour, and energy-continuity correction list.**

## Minimum thermal-survivability ledger

| Question | Evidence required |
|---|---|
| What threshold defines unsafe conditions? | Indoor temperature / heat index / smoke / cold trigger, population group, duration, health basis, legal duty. |
| Who is exposed? | Tenants, public housing, schools, care homes, prisoners, outdoor workers, medically dependent people, older adults, children, unhoused people, informal settlements. |
| What protects them first? | Passive measures, shade, cool roof, envelope, ventilation, efficient cooling, clean-air room, water, refuge, wellness checks, transport. |
| What happens during outage? | Critical load, passive duration, backup / storage, restoration priority, refuge opening, medically dependent support. |
| Who pays? | Landlord, utility, public housing authority, school district, employer, health system, climate finance, emergency funds, social protection. |
| What triggers remedy? | Indoor threshold breach, repair delay, utility shutoff, school / care closure, worker injury, hospitalization, death, complaint cluster, refuge non-access. |

## What this routes to

- use this file when the question is about heat survivability, passive survivability, indoor temperature, cooling access, clean-air spaces, heat and outages, schools / care homes / prisons in heat, worker heat safety, or housing habitability under heat;
- pair with `07`, `16`, `234`, and `239` for cooling, buildings, passive demand reduction, and retrofit design;
- pair with `24`, `279`, `280`, and `283`-supported health files for heat-health surveillance and care;
- pair with `283` / `284` for older adults, disabled people, medically dependent people, care homes, and home care;
- pair with `287` / `288` for housing habitability, rent, repairs, and temporary accommodation;
- pair with `297` / `298` for power, backup, critical load, shutoffs, and energy burden;
- pair with `285` / `286` for worker heat rules and paid safety;
- pair with `293` / `294` and `295` / `296` for warnings, public information, and access to refuge.

## What this rules out

It rules out heat plans that stop at outdoor warnings.
It rules out cooling centres without transport, hours, trust, water, toilets, language access, disability access, and backup power.
It rules out housing policy that ignores indoor heat.
It rules out school and care continuity that counts buildings as open when they are thermally unsafe.
It rules out worker heat rules that cost workers wages.
It rules out AC expansion that ignores efficiency, peak load, refrigerants, affordability, clean power, and outage fallback.

## Compression rule

**Thermal survivability is an inspectable service floor: name safe indoor thresholds, passive duration, clean-air and cooling refuge, outage fallback, access support, worker protection, housing and institutional duties, energy and water dependencies, remedy triggers, and after-action corrections before heat, smoke, cold, or outages turn buildings into exposure sites.**

---
Citations point to `sources/register.md`.
