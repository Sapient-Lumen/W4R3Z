---
id: '371'
revision_added: rev0277
status: canon
object_type: integrity_gate
domain_tags:
- public_ledgers
- open_government
- audit
- appeals
- ombuds
- correction
- public_participation
service_floor:
- contestable_public_service_ledger
- independent_correction_path
hazard_tags:
- all_hazards
- fraud
- stale_data
- exclusion
- capture
- misinformation
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- public_auditor
- ombuds
- civil_society
- data_steward
- service_owner
- inspector_general
- court
- community_organization
instrument_tags:
- disclose
- audit
- appeal
- correct
- protect_privacy
- publish
- archive
- investigate
routes_to:
- '04'
- '19'
- '40'
- '259'
- '260'
- '291'
- '350'
- '365'
- '421'
- '424'
- '428'
source_ids:
- S297
- S638
- S653
- S666
- S667
upstream_dependencies:
- open_data_policy
- privacy_rule
- appeals_process
- audit_capacity
- data_dictionary
- ombuds_authority
- record_retention
downstream_consequences:
- legitimacy_loss
- uncorrected_exclusion
- corruption
- repeated_failure
- court_backlog
- household_harm
equity_lenses:
- low_literacy_users
- language_access
- disability_access
- renters
- undocumented_people
- small_businesses
- remote_communities
degraded_modes:
- paper_appeal_path
- phone_complaint_log
- community_auditor_packet
- offline_public_records_snapshot
- anonymized_case_summary
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- dashboard_without_underlying_data
- no_appeal_path
- no_change_log
- privacy_used_as_blanket_secrecy
- independent_audit_unfunded
- complaint_not_tied_to_correction
failure_modes:
- dashboard_becomes_propaganda
- public_cannot_challenge_wrong_status
- excluded_households_disappear_from_metrics
- procurement_or_claims_capture_hidden_by_aggregate_data
- correction_not_archived
proof_ledgers:
- public_data_dictionary
- change_log
- appeal_and_correction_log
- independent_audit_report
- privacy_suppression_log
- complaint_resolution_log
restoration_conflicts:
- transparency_vs_privacy
- speed_vs_due_process
- security_vs_public_right_to_know
- aggregate_metrics_vs_case_specific_harm
assurance_tests:
- dashboard_cell_pull_audit
- appeal_mystery_shop
- public_records_request_test
- community_audit_walkthrough
- correction_log_replay
public_ledger_contestability: public_status_must_be_open_enough_to_audit_private_enough_to_protect_and_contestable_enough_to_correct
---

# 371 — Ideal Solutions: Make climate service ledgers open, contestable, and correctable before dashboards become propaganda

## Claim

A public ledger is not trustworthy merely because it is public. It must be open enough to audit, private enough to protect people, and contestable enough to correct wrong or harmful status.

Open Contracting Data Standard sources already in the archive show how common structured data can make contracting easier to monitor and analyze [S297]. UNDRR scorecards and Sendai monitoring show the value of comparable risk and loss indicators [S638][S653]. Open Data for Resilience emphasizes collaborative risk-data practices, while OECD open-government principles emphasize transparency, integrity, accountability, and participation [S666][S667].

House rule: **every public climate ledger needs a correction path as visible as its status claim.**

## Fast rule

For every public dashboard, scorecard, map, register, claim portal, procurement list, or recovery ledger, ask: can an affected person see the basis, challenge an error, protect sensitive data, and track correction?

## The compact canon

### 1. Public data must have provenance

Each status claim should identify source, date, owner, method, confidence, suppression rule, and update cadence. Without provenance, the public cannot tell the difference between measurement, estimate, self-report, model, aspiration, and politics.

### 2. Contestability protects truth

People should be able to challenge a wrong denial, unsafe clearance, missing road closure, incorrect shelter status, bad contractor listing, false reentry permission, broken-language access, or missing household from a registry.

### 3. Privacy is a design constraint, not a secrecy excuse

Protective registries, health data, payment records, immigration-sensitive information, custody status, GBV referrals, and household vulnerability lists need strict privacy. But aggregate performance, owner identity, correction status, and audit results still need public visibility.

### 4. Independent audit must be funded

Inspection, internal audit, inspector general review, community monitoring, ombuds authority, courts, media, and civil society cannot correct the cube if they are unfunded, locked out, or denied records.

### 5. Correction is the final public metric

The most important dashboard line may be not the current status, but how many known errors, exclusions, unsafe returns, delayed claims, fraud reports, and unresolved needs were corrected before the next hazard season.

## Minimum packet

A contestable-ledger packet includes: data dictionary; source and method; update cadence; suppression rule; change log; appeal path; ombuds / audit owner; correction deadline; anonymized case examples; and public report on corrected errors.

## Bottom line

Dashboards help only if they make power visible and correctable. The public should be able to see not only what the system says, but how the system can be challenged when it is wrong.

## Rev0278 ledger addition — trigger contestability

Public ledgers should make trigger decisions contestable: who activated, who did not, what signal was used, what uncertainty was known, which action was funded, which users were excluded, and how the threshold changed afterward. False alarms and missed alarms belong in the public learning record.

---
Citations point to `sources/register.md`.
