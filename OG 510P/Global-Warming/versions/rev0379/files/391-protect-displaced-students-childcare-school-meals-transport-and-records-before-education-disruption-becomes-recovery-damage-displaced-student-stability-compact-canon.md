---
id: '391'
revision_added: rev0280
status: canon
object_type: service_continuity
domain_tags:
- education
- displaced_students
- childcare
- school_transport
- school_meals
- records
- youth_recovery
service_floor:
- immediate_school_access
- school_origin_or_best_interest_path
- childcare_and_meal_continuity
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
- school_year_clock
- learning_clock
actor_tags:
- local_education_agency
- homeless_education_liaison
- school_district
- childcare_provider
- transport_provider
- family
- case_manager
- nutrition_program
instrument_tags:
- immediate_enrollment
- school_origin_transport
- records_substitution
- meal_continuity
- childcare_referral
- attendance_support
- case_handoff
routes_to:
- '281'
- '282'
- '275'
- '339'
- '390'
- '393'
- '396'
source_ids:
- S702
upstream_dependencies:
- housing_transition
- transport_access
- identity_or_records_substitution
- school_staff
- nutrition_benefits
- communications
downstream_consequences:
- learning_loss
- caregiver_work_loss
- child_protection_risk
- nutrition_loss
- family_displacement_duration
- youth_mental_health_harm
equity_lenses:
- children
- unaccompanied_youth
- students_with_disabilities
- limited_english_families
- migrant_students
- rural_students
- families_in_hotels_or_shelters
- children_without_documents
degraded_modes:
- paper_enrollment
- temporary_bus_route
- school_meal_pickup_or_delivery
- remote_records_request
- community_childcare_hub
- liaison_case_table
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- records_lost
- transport_unfunded
- temporary_address_not_recognized
- childcare_provider_closed
- school_meals_not_portable
- IEP_or_disability_support_interrupted
failure_modes:
- child_misses_weeks_due_to_documents
- family_declines_safe_housing_to_keep_school
- school_transfer_harms_learning
- meal_access_lost_during_displacement
- youth_becomes_invisible_to_recovery_casework
proof_ledgers:
- displaced_student_roster
- school_enrollment_exception_log
- school_origin_transport_log
- meal_continuity_log
- childcare_slot_register
- records_replacement_log
- attendance_recovery_log
displaced_student_stability: immediate enrollment, school-origin/best-interest decision, transport, records substitution,
  meals, childcare, disability supports, and attendance recovery are owned
---

# 391 — Protect displaced students, childcare, school meals, transport, and records before education disruption becomes recovery damage

## Core claim

Disaster displacement is an education shock. Children can lose school access because a lease, immunization record, transcript, proof of address, bus route, device, meal card, uniform, caregiver job, or childcare slot disappeared. The climate service floor is not simply reopening a school building. It is keeping displaced children attached to learning, meals, care, disability supports, and trusted adults.

The National Center for Homeless Education explains that children and youth displaced by disasters generally may qualify under McKinney-Vento protections, and that the local homeless education liaison is a key contact [S702]. That matters because disaster recovery often treats school as secondary, even though school stabilizes families.

## The displaced-student packet

The minimum packet includes:

1. immediate enrollment or continued school-of-origin decision;
2. substitute documents when records are lost;
3. transport to the school of origin or a best-interest alternative;
4. disability, IEP, medication, language, and counseling handoffs;
5. school meals and nutrition continuity;
6. childcare continuity for younger siblings and caregivers who must work or attend recovery appointments;
7. attendance recovery and tutoring after interruption;
8. safe pickup / dropoff from shelters, hotels, host-family homes, temporary units, and relocated neighborhoods.

## Family-stability rule

Housing recovery should not force families to choose between a safe place to sleep and a child's school. If temporary housing is distant, the housing path must carry the education transport cost or make an explicit best-interest decision.

## Cube rule

All child, school, shelter, housing, transport, and food-service packets should expose `displaced_student_stability`. Blank means the archive should assume children are present but not separately protected.

---
Citations point to `sources/register.md`.
