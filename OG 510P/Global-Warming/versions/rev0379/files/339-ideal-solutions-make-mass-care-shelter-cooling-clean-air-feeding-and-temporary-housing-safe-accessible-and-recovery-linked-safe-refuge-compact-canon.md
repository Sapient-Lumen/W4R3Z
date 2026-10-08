---
id: '339'
revision_added: rev0274
status: canon
object_type: service_continuity
domain_tags:
- mass_care
- shelter
- temporary_housing
- feeding
- cooling
- clean_air
- human_services
- safe_refuge
service_floor:
- safe_refuge
- accessible_shelter
- feeding_and_basic_needs
- non_congregate_option
- recovery_routing
hazard_tags:
- heat
- smoke
- flood
- storm
- wildfire
- outage
- evacuation
- disease
- displacement
- compound_shock
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- mass_care_lead
- voluntary_organization
- public_health_agency
- housing_agency
- school_district
- transport_operator
- community_organization
instrument_tags:
- shelter
- feed
- transport
- register
- refer
- inspect
- protect
- route
- audit
routes_to:
- '252'
- '281'
- '283'
- '287'
- '288'
- '293'
- '303'
- '304'
- '313'
- '314'
- '319'
- '328'
- '335'
- '337'
- '345'
source_ids:
- S603
- S605
upstream_dependencies:
- buildings
- power
- water
- sanitation
- transport
- food
- medical_support
- casework
- communications
- security_without_coercion
- pet_service_animal_capacity
downstream_consequences:
- heat_death
- smoke_exposure
- family_separation
- infection
- violence
- homelessness
- lost_documents
- aid_exclusion
- untrusted_recovery
equity_lenses:
- disabled_people
- older_adults
- children
- pregnant_people
- survivors_of_violence
- people_with_pets_or_service_animals
- people_without_ID
- language_minority_groups
- unhoused_people
- LGBTQ_people
- people_in_custody_release_pathways
degraded_modes:
- cooling_clean_air_room
- mobile_shelter_transport
- paper_intake
- community_verified_identity
- non_congregate_motel_or_host_path
- accessible_supply_cache
- casework_by_phone_radio_or_in_person
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- shelter_space
- staffing
- transport
- accessible_cots_showers_toilets
- generator_fuel
- HVAC_filtration
- casework_capacity
- non_congregate_contracts
- pet_capacity
failure_modes:
- shelter_open_but_unreachable
- refuge_without_cooling_or_clean_air
- congregate_shelter_infection_or_violence_risk
- accessible_needs_unmet
- people_displaced_from_shelter_to_paperwork_queue
- temporary_housing_becomes_dead_end
proof_ledgers:
- shelter_capacity_and_accessibility_log
- indoor_temperature_and_air_log
- feeding_distribution_log
- FNSS_or_access_needs_log
- referral_and_casework_log
- complaint_and_safeguarding_log
- non_congregate_room_log
- shelter_exit_outcome_log
restoration_conflicts:
- congregate_speed_vs_safety
- short_shelter_stay_vs_housing_reality
- centralized_shelter_vs_accessibility
- privacy_vs_casework
- public_order_vs_dignity
assurance_tests:
- heat_smoke_outage_shelter_test
- accessible_transport_to_shelter_drill
- no_ID_no_phone_shelter_intake
- non_congregate_contract_activation
- shelter_exit_casework_audit
shelter_standard: Sphere_rights_dignity_access_protection_plus_ESF6_mass_care_operations
---

# 339 — Ideal Solutions: Make mass care, shelter, cooling, clean air, feeding, and temporary housing safe, accessible, and recovery-linked

## Claim

Climate refuge is not a cot count. **A shelter or temporary-housing programme is a service floor only if it keeps people alive, reachable, safe, fed, connected, protected, and routed toward recovery.**

Mass care sits at the junction of almost every continuity packet. A shelter may need cooling, clean air, WASH, feeding, medicines, mental-health support, disability access, child protection, charging, records, legal help, payment access, transport, pet / service-animal accommodation, and a path to temporary or permanent housing. FEMA's ESF #6 frame puts mass care, emergency assistance, temporary housing, and human services in one operating lane [S603]. Sphere adds the rights-based minimum: assistance, dignity, protection, participation, WASH, shelter, food, and health belong together, not as separate checklists [S605].

## Compact rule

**A safe refuge packet must be climate-safe, accessible, protection-aware, and exit-linked.**

Climate-safe means the indoor temperature, indoor air, power, water, sanitation, food, and health conditions are measured. Accessible means transport, intake, sleeping, toilets, showers, communication, devices, medicines, and service animals work for people with functional needs. Protection-aware means the site reduces violence, abuse, harassment, family separation, trafficking, theft, coercion, and privacy harms. Exit-linked means shelter is connected to claims, documents, legal help, temporary housing, repairs, rental support, school continuity, work continuity, and transportation.

## Minimum packet

A refuge packet needs:

1. site list with heat, smoke, flood, outage, WASH, accessibility, backup-power, and transport checks;
2. capacity model for general shelter, cooling / clean-air refuge, non-congregate shelter, family units, and pet / service-animal support;
3. intake that works without ID, broadband, English, literacy, or a smartphone;
4. protection protocol for children, disabled people, older adults, survivors of violence, LGBTQ people, and people without documents;
5. referral links to health, medicines, mental health, legal help, cash, claims, schools, housing, and reunification;
6. complaint and safeguarding logs;
7. exit outcome tracking, not just nightly occupancy.

## Failure modes

The bad version opens a gym, counts beds, and declares success. Then smoke enters, cooling fails, accessible toilets are absent, pets are refused, a survivor of violence has no safe sleeping option, a child misses medication, people cannot charge phones, casework is online only, and families exit into homelessness or repair scams.

The stricter rule: **no refuge is ready until a person can arrive with no car, no phone, a wheelchair, a pet or service animal, medication needs, limited English, lost ID, trauma, and children — and still be safe.**

## Cube routing

Route this file whenever a packet says shelter, refuge, mass care, temporary housing, non-congregate shelter, cooling centre, clean-air centre, feeding, emergency supplies, family assistance, or evacuation centre. Pair with `287`, `288`, `293`, `303`, `304`, `313`, `319`, `328`, `335`, `337`, and `345`.

---
Citations point to `sources/register.md`.
