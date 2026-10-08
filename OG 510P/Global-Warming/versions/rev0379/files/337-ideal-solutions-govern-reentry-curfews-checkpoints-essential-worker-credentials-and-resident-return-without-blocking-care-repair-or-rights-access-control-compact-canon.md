---
id: '337'
revision_added: rev0273
status: canon
object_type: service_continuity
domain_tags:
- reentry
- access_control
- credentialing
- curfew
- checkpoints
- essential_workers
- resident_return
- rights
service_floor:
- safe_reentry
- essential_worker_access
- resident_return_rights
hazard_tags:
- evacuation
- wildfire
- flood
- storm
- hazmat
- disease
- civil_unrest
- outage
- smoke
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- law_enforcement
- utility
- healthcare_supplier
- pharmacy
- repair_contractor
- resident
- business
- community_organization
- civil_rights_monitor
instrument_tags:
- credential
- permit
- checkpoint
- curfew
- authorize
- escort
- notify
- appeal
- phase
- audit
routes_to:
- '274'
- '283'
- '284'
- '291'
- '292'
- '295'
- '296'
- '303'
- '316'
- '319'
- '324'
- '327'
- '328'
source_ids:
- S600
- S601
upstream_dependencies:
- credentialing_system
- public_notice
- law_enforcement_training
- identity_substitution_rules
- transport
- communications
- civil_rights_monitoring
- essential_supplier_roster
downstream_consequences:
- medicine_shortage
- home_care_failure
- repair_delay
- unsafe_self_reentry
- rights_violation
- untrusted_recovery
- household_loss_increases
equity_lenses:
- residents_without_documents
- renters
- migrant_workers
- home_care_workers
- disabled_people
- older_adults
- small_businesses
- informal_workers
- language_minority_groups
degraded_modes:
- paper_credential
- employer_letter
- community_verified_identity
- escorted_access
- mobile_reentry_center
- radio_notice
- temporary_resident_pass
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- credential_mismatch
- checkpoint_discretion
- resident_document_loss
- supplier_access_denial
- curfew_blocks_workers
- language_gap
- law_enforcement_overreach
- no_appeal_path
failure_modes:
- care_workers_blocked
- pharmacy_supply_blocked
- repair_crews_blocked
- residents_cannot_check_homes_or_pets
- curfew_exempts_power_but_not_home_care
- checkpoint_bias
- access_permit_becomes_privilege
proof_ledgers:
- reentry_phase_plan
- credential_registry
- checkpoint_decision_log
- denial_and_appeal_log
- essential_supplier_list
- resident_return_notice
- civil_rights_incident_log
- after_action_access_audit
restoration_conflicts:
- safety_vs_return
- security_vs_care_access
- fraud_control_vs_document_loss
- business_reopening_vs_resident_rights
- traffic_control_vs_worker_access
assurance_tests:
- checkpoint_scenario_drill
- lost_document_reentry_test
- home_care_worker_access_test
- pharmacy_supplier_access_test
- language_access_notice_test
- denial_appeal_exercise
---

# 337 — Ideal Solutions: Govern reentry, curfews, checkpoints, essential-worker credentials, and resident return without blocking care, repair, or rights

## Claim

After evacuation, access control becomes climate governance. **Reentry, curfews, checkpoints, and essential-worker credentials can either protect life and restore services or block care, medicine, repairs, resident rights, and local recovery.**

CISA's essential critical-infrastructure workforce guidance is a starting point for identifying workers needed for essential functions [S600]. Healthcare Ready's disaster-access work shows the practical problem for healthcare, pharmacy, and supply-chain access after disasters [S601]. But the archive needs a rights-and-service floor, not only a critical-worker list.

## Compact rule

**Restricted access must be phased, service-based, reviewable, and rights-aware.**

The first phase may need public safety, search and rescue, hazardous-material control, utilities, medical supply, and damage assessment. But the next phases must not forget home care, pharmacies, assistive-technology repair, childcare, food, cash-out, small businesses, tenants, residents checking damage, animal care, document recovery, legal help, and community intermediaries.

## Minimum packet

A reentry packet includes:

- phased access classes tied to service consequences;
- credential types that work offline and across checkpoints;
- substitute-proof rules for people who lost documents;
- worker categories beyond obvious responders, including home care, pharmacies, repair, cleanup, food, cash, legal, translation, and community outreach;
- public notice in accessible and multilingual forms;
- denial and appeal logs;
- civil-rights monitoring;
- sunset and after-action correction.

## Failure modes

The bad version looks orderly but blocks recovery. Utility crews enter but home oxygen suppliers do not. Police recognize large contractors but not local repair workers. A curfew exempts emergency vehicles but not caregivers. A resident cannot retrieve medication because ID burned. A renter cannot document damage before a landlord clears the unit. A checkpoint officer decides access case by case with no log or appeal.

## Cube routing

Route this file whenever a packet involves evacuation, shelter-in-place, curfew, checkpoint, reentry pass, access permit, critical worker, restricted zone, cleanup zone, contaminated area, or post-disaster business reopening. Pair with `274`, `291`, `295`, `303`, `316`, `324`, and `327`.

---
Citations point to `sources/register.md`.
