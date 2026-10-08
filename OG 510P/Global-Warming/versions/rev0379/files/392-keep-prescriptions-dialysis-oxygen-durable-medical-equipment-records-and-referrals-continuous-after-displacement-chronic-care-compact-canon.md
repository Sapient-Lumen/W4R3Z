---
id: '392'
revision_added: rev0280
status: canon
object_type: service_continuity
domain_tags:
- chronic_care
- prescriptions
- dialysis
- oxygen
- DME
- medical_records
- health_referral
- power_dependent_care
service_floor:
- medication_and_device_continuity
- chronic_care_referral
- medical_record_portability
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
- clinical_clock
- learning_clock
actor_tags:
- public_health
- hospital
- clinic
- pharmacy
- dialysis_provider
- oxygen_supplier
- home_health_agency
- insurer_or_payer
- case_manager
instrument_tags:
- EPAP
- patient_registry
- emPOWER_map
- pharmacy_override
- record_release
- referral
- transport
- backup_power
- clinical_outreach
routes_to:
- '279'
- '283'
- '316'
- '317'
- '323'
- '342'
- '385'
- '389'
- '396'
source_ids:
- S703
- S704
- S705
upstream_dependencies:
- power
- telecom
- pharmacies
- medical_cold_chain
- transport
- payment_rails
- privacy_controls
- patient_registries
downstream_consequences:
- avoidable_hospitalization
- death
- shelter_medical_surge
- caregiver_burnout
- evacuation_failure
- public_health_trust_loss
equity_lenses:
- older_adults
- disabled_people
- medically_dependent_people
- uninsured_people
- rural_patients
- people_without_caregivers
- limited_english_patients
- institutionalized_or_recently_discharged_people
degraded_modes:
- paper_prescription_reconciliation
- mobile_pharmacy
- generator_supported_charging_site
- field_clinic
- manual_referral_roster
- community_health_worker_outreach
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- pharmacy_closed
- prescription_records_unavailable
- electricity_dependent_equipment_unpowered
- dialysis_slot_lost
- insurance_prior_authorization
- medical_record_privacy_overblocking
- transport_to_care_unavailable
failure_modes:
- survivor_has_shelter_but_no_medicine
- oxygen_or_DME_fails_due_to_outage
- dialysis_missed_after_evacuation
- chronic_condition_decompensates_after_intake
- privacy_rules_misapplied_as_no_help
proof_ledgers:
- power_dependent_patient_outreach_log
- EPAP_activation_log
- pharmacy_access_map
- dialysis_slot_and_transport_log
- oxygen_supplier_log
- record_request_log
- clinical_referral_status
chronic_care_continuity: patient/device registries, EPAP or pharmacy overrides, dialysis/oxygen/DME referrals, power
  support, transport, records, and clinical follow-up are maintained
---

# 392 — Keep prescriptions, dialysis, oxygen, durable medical equipment, records, and referrals continuous after displacement

## Core claim

For medically dependent people, recovery failure can happen quietly after the headline emergency ends. A person may be sheltered but miss dialysis, lose insulin, run out of oxygen, lack a CPAP or wheelchair charger, lose durable medical equipment, or be unable to prove a prescription. That is not a private inconvenience; it is a climate service-floor failure.

The HHS emPOWER Program provides data and tools to help communities protect at-risk Medicare beneficiaries, including people who rely on electricity-dependent durable medical and assistive equipment or essential health services [S703]. ASPR's Emergency Prescription Assistance Program can help eligible uninsured disaster survivors replace prescriptions, vaccines, medical supplies, and some equipment [S704]. Emergency-preparedness requirements for ESRD facilities explicitly include plans for hazards such as water-supply interruption, power failures, and natural disasters [S705].

## The chronic-care packet

Minimum continuity requires:

- patient and equipment risk mapping before impact;
- pharmacy, prescription, and payer override rules;
- EPAP or equivalent activation criteria;
- dialysis slot, transport, water, and power coordination;
- oxygen, DME, assistive technology, and charging / battery support;
- medical cold chain and clinic referral;
- privacy-safe but actionable record sharing;
- follow-up after shelter, hotel, relocation, or facility discharge.

## Anti-abandonment rule

A care-dependent person should not be counted as safe because they are inside a shelter if their device, medicine, dialysis, oxygen, caregiver, transport, or records have failed.

## Cube rule

All health, care, shelter, energy, transport, and intake packets should expose `chronic_care_continuity`. Blank means the archive should assume the recovery system has not tested chronic-care survival after the first 72 hours.

---
Citations point to `sources/register.md`.
