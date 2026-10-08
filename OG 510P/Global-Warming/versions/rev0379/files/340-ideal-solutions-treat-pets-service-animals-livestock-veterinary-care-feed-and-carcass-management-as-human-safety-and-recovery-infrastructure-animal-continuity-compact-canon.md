---
id: '340'
revision_added: rev0274
status: canon
object_type: service_continuity
domain_tags:
- animals
- pets
- service_animals
- livestock
- veterinary
- evacuation
- shelter
- agrifood
service_floor:
- animal_evacuation_and_shelter
- service_animal_continuity
- veterinary_and_feed_access
- carcass_and_waste_management
hazard_tags:
- wildfire
- flood
- storm
- heat
- smoke
- drought
- disease
- evacuation
- power_outage
clock_tags:
- emergency_clock
- recovery_clock
- seasonal_clock
- learning_clock
actor_tags:
- emergency_manager
- animal_control
- veterinarian
- shelter_operator
- agriculture_agency
- farmer
- rancher
- public_health_agency
- waste_operator
instrument_tags:
- evacuate
- shelter
- feed
- vaccinate
- treat
- identify
- transport
- dispose
- reunify
- audit
routes_to:
- '275'
- '276'
- '282'
- '283'
- '287'
- '293'
- '295'
- '299'
- '300'
- '319'
- '329'
- '337'
- '339'
source_ids:
- S612
- S613
upstream_dependencies:
- transport
- shelter_sites
- feed
- water
- veterinary_staff
- identification_records
- public_information
- waste_and_debris_capacity
downstream_consequences:
- evacuation_noncompliance
- family_distress
- livelihood_loss
- zoonotic_or_water_risk
- shelter_conflict
- recovery_delay
equity_lenses:
- low_income_pet_owners
- disabled_people_with_service_animals
- older_adults
- children
- farmworkers
- smallholders
- ranchers
- people_without_private_vehicles
- unhoused_people_with_animals
degraded_modes:
- co_located_pet_shelter
- mobile_veterinary_triage
- buddy_transport
- paper_vaccine_record_substitute
- emergency_feed_distribution
- community_animal_reunification_board
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- pet_shelter_capacity
- animal_transport
- feed_supply
- veterinary_staff
- vaccination_records
- livestock_trailers
- carcass_disposal
- service_animal_policy
failure_modes:
- people_refuse_evacuation_due_to_pets
- service_animal_separated_from_handler
- livestock_welfare_collapse
- feed_or_water_absent
- carcasses_create_health_and_water_risk
- animal_shelter_not_connected_to_human_shelter
proof_ledgers:
- animal_shelter_capacity_log
- pet_service_animal_intake_log
- feed_and_water_inventory
- veterinary_care_log
- livestock_transport_roster
- carcass_management_log
- animal_reunification_log
restoration_conflicts:
- human_shelter_space_vs_pet_space
- biosecurity_vs_reunification
- livestock_evacuation_vs_road_capacity
- carcass_disposal_speed_vs_environmental_protection
assurance_tests:
- pet_inclusive_evacuation_drill
- service_animal_shelter_check
- livestock_feed_water_surge_test
- carcass_management_tabletop
- animal_reunification_test
animal_continuity: include_animals_in_evacuation_mass_care_feed_veterinary_and_waste_plans
---

# 340 — Ideal Solutions: Treat pets, service animals, livestock, veterinary care, feed, and carcass management as human safety and recovery infrastructure

## Claim

Animals are not a side issue in climate shocks. **Pet, service-animal, livestock, veterinary, feed, and carcass systems are human safety, food, livelihood, public-health, and evacuation infrastructure.**

USDA APHIS states the practical lesson plainly: animal safety and well-being during disasters is key to the safety and well-being of people, and post-Katrina experience helped drive the PETS Act mission [S612]. Ready.gov turns that into household practice: evacuation plans, buddy systems, microchips, supplies, and local shelter information matter before the warning [S613].

## Compact rule

**Evacuation and shelter are not ready unless people can bring, protect, or safely transfer the animals that determine whether they leave.**

This includes pets, service animals, emotional-support and working animals where relevant, livestock, backyard poultry, veterinary medicines, feed, water, trailers, records, quarantine / biosecurity, and carcass management. For many households, animals are family. For disabled people, a service animal may be a mobility, safety, seizure, hearing, psychiatric, or independence support. For farmers and pastoralists, livestock are food security, savings, work, identity, and future production.

## Minimum packet

An animal-continuity packet includes:

- pet-inclusive public messaging;
- service-animal non-separation rules;
- co-located or linked animal shelter capacity;
- transport for people without vehicles;
- emergency feed, water, medicines, and veterinary care;
- livestock evacuation or shelter-in-place decision rules;
- vaccination / ownership / microchip substitute records;
- carcass collection, disposal, environmental protection, and worker safety;
- reunification and lost-animal logs.

## Failure modes

The common failure is to make a human evacuation order but no animal plan. People stay behind. Others arrive at shelters and are turned away. A service animal is treated as a pet. Livestock lose feed and water after roads close. Carcasses contaminate waterways or become cleanup hazards. Animal rescue groups absorb public duty without resources or safety.

The archive's rule: **animal planning is a condition for evacuation compliance and dignified recovery.**

## Cube routing

Route this file whenever a packet mentions evacuation, shelter, accessible evacuation, farming, livestock, pets, service animals, veterinary care, carcass disposal, feed, rural households, or household refusal to evacuate. Pair with `275`, `276`, `283`, `287`, `295`, `299`, `329`, `337`, and `339`.

---
Citations point to `sources/register.md`.
