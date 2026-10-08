---
id: '402'
revision_added: rev0281
status: canon
object_type: service_continuity
domain_tags:
- essential_property
- appliances
- assistive_technology
- durable_medical_equipment
- contents
- safe_return
service_floor:
- essential_property_device_replacement
- functional_home_restart
- assistive_device_restoration
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
- FEMA_or_national_assistance
- case_manager
- health_agency
- disability_service_provider
- appliance_repair_market
- voluntary_agency
- insurer
instrument_tags:
- personal_property_assistance
- device_replacement
- appliance_repair
- DME_replacement
- voucher
- inspection
- donation_matching
- warranty_or_repair
routes_to:
- '283'
- '284'
- '316'
- '339'
- '390'
- '392'
- '393'
- '398'
source_ids:
- S704
- S721
upstream_dependencies:
- housing_status
- power
- water
- insurance_claim
- benefit_casework
- device_supplier
- delivery_transport
- document_substitution
downstream_consequences:
- unsafe_return
- nutrition_failure
- medical_decline
- education_loss
- debt
- institutionalization
- caregiver_burden
equity_lenses:
- disabled_people
- medically_dependent_people
- families_with_children
- renters
- low_income_households
- older_adults
- people_without_insurance
- limited_english_households
degraded_modes:
- attestation_of_loss
- community_verified_inventory
- loaner_device_pool
- repair_before_replacement
- voucher_or_cash_choice
- mobile_delivery
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- structure_repaired_but_contents_absent
- device_loss_not_seen_as_housing_issue
- donations_supply_wrong_items
- appliance_backlog_blocks_food_medicine_or_heat
- proof_of_loss_impossible
failure_modes:
- safe_return_fails_despite_habitable_structure
- medicine_spoils
- food_storage_impossible
- disabled_person_loses_independence
- child_lacks_school_device
- household_takes_debt_for_basics
proof_ledgers:
- essential_property_inventory
- DME_device_status
- appliance_replacement_log
- donation_match_log
- inspection_photo_or_attestation
- appeal_log
essential_property_device_replacement: safe return requires essential appliances, medical and assistive devices,
  communications devices, school/work devices, and basic household contents to be repaired, replaced, loaned, or
  substituted
---

# 402 — Replace essential personal property, appliances, devices, and assistive technology before safe return is fiction

## Core claim

A home is not functionally restored merely because walls, roof, and utilities pass inspection. Households need appliances, room furnishings, refrigeration, communications devices, school/work devices, assistive technology, oxygen or dialysis supplies, chargers, batteries, and other basic contents. Otherwise safe return is formal but daily life remains broken.

FEMA's housing and other-needs assistance materials include personal property and other categories such as transportation, medical/dental, childcare, and funeral assistance [S721]. ASPR's Emergency Prescription Assistance Program can support replacement of prescriptions, vaccines, medical supplies, and some medical equipment for eligible uninsured people after federally declared disasters [S704]. The archive's addition is a function rule: contents are not private decoration when they provide food safety, medicine, learning, work, communication, disability access, and thermal safety.

## Essential-property packet

The packet should include:

- basic appliance and furniture loss inventory;
- refrigeration, cooking, heating/cooling, filtration, and communications needs;
- durable medical equipment and assistive-device replacement;
- school/work device replacement;
- donation matching that avoids unsafe, unusable, or inequitable distribution;
- appeal and document-substitution paths;
- delivery and installation support.

## Function-before-category rule

The question is not whether an item fits a narrow assistance category. The question is what service floor fails without it: medicine, food, heat, cooling, clean air, communication, school, work, mobility, or care.

## Cube rule

Housing, health, school, nutrition, and no-wrong-door packets should expose `essential_property_device_replacement`. Blank means the archive should assume the structure may reopen before the household can function.

---
Citations point to `sources/register.md`.
