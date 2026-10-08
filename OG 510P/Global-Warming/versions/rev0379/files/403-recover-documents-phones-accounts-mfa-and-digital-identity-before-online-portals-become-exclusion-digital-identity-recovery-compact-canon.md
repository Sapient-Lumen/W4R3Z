---
id: '403'
revision_added: rev0281
status: canon
object_type: integrity_gate
domain_tags:
- digital_identity
- document_replacement
- account_recovery
- MFA
- phones
- benefit_portals
- fraud_prevention
service_floor:
- document_and_account_recovery
- digital_identity_access
- portal_fallback
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
- identity_provider
- benefits_agency
- FEMA_or_assistance_agency
- telecom_provider
- library_or_community_anchor
- legal_aid
- case_manager
- privacy_officer
instrument_tags:
- document_replacement
- account_recovery
- MFA_fallback
- phone_or_SIM_replacement
- in_person_proofing
- helpdesk
- fraud_control
- paper_fallback
routes_to:
- '291'
- '292'
- '342'
- '365'
- '377'
- '385'
- '395'
- '396'
source_ids:
- S723
- S724
- S725
upstream_dependencies:
- vital_records
- telecom_restoration
- connectivity
- privacy_rules
- legal_help
- in_person_service_point
- trusted_intermediary
- paper_records
downstream_consequences:
- benefit_exclusion
- identity_theft
- missed_deadline
- appeal_failure
- unsafe_disclosure
- no_wrong_door_failure
equity_lenses:
- people_without_ID
- people_without_phones
- older_adults
- disabled_people
- limited_english_households
- people_fleeing_abuse
- unhoused_people
- mixed_status_households
- rural_households
degraded_modes:
- paper_application
- in_person_identity_proofing
- trusted_referee
- temporary_account_hold
- voice_or_mail_status
- public_terminal_with_privacy
- offline_authentication
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- lost_phone_locks_out_MFA
- documents_destroyed
- portal_requires_email_or_SMS
- fraud_controls_block_real_survivors
- replacement_ID_requires_address_that_was_lost
- connectivity_outage_blocks_status
failure_modes:
- survivor_cannot_apply_upload_check_status_or_appeal
- fraudsters_capture_accounts
- benefits_missed
- deadline_missed
- privacy_or_abuser_risk
proof_ledgers:
- document_replacement_log
- account_recovery_queue
- MFA_exception_log
- phone_SIM_replacement_status
- portal_fallback_log
- fraud_and_correction_log
digital_identity_account_recovery: document, phone, SIM, authenticator, email, portal, and status access have degraded-mode
  recovery with anti-fraud controls that do not exclude legitimate survivors
---

# 403 — Recover documents, phones, accounts, MFA, and digital identity before online portals become exclusion

## Core claim

Modern recovery often assumes a survivor can receive SMS, open email, remember passwords, use a smartphone, upload documents, pass identity proofing, and check a portal. Disasters break exactly those assumptions. Phones are lost, SIMs fail, chargers are gone, accounts are compromised, addresses no longer work, documents are destroyed, and connectivity is intermittent.

FEMA provides guidance for replacing vital documents after disaster [S723]. NIST's SP 800-63-4 updates digital identity guidance around risk management, continuous evaluation, fraud controls, and identity-proofing roles [S724]. FCC's wireless resilience work aims to reduce wireless outages and support faster restoration after hurricanes, wildfires, and other disasters [S725]. The archive's addition is an exclusion rule: account security and fraud control must include disaster-mode recovery, or portals become a denial mechanism.

## Digital recovery packet

The packet should include:

- vital document replacement and substitute-proof paths;
- phone, SIM, charger, and connectivity support;
- MFA fallback for lost devices;
- in-person and trusted-referee identity proofing;
- paper / phone / community-anchor alternatives to portals;
- privacy and safety checks for people fleeing abuse;
- fraud, account-takeover, and correction logs;
- accessible language and disability support.

## Portal fallback rule

No essential disaster benefit, appeal, medical referral, school enrollment, or housing step should require a single digital channel. Online access can accelerate recovery only when offline and assisted channels remain real.

## Cube rule

Every survivor-facing service should expose `digital_identity_account_recovery`. Blank means the archive should assume digital systems may be functioning for administrators while excluding the people they serve.

---
Citations point to `sources/register.md`.
