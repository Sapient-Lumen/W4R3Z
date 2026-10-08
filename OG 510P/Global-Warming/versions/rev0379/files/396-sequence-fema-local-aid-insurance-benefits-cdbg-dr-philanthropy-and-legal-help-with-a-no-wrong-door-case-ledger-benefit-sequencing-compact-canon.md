---
id: '396'
revision_added: rev0280
status: canon
object_type: integrity_gate
domain_tags:
- benefit_sequencing
- no_wrong_door
- case_management
- duplication_of_benefits
- unmet_needs
- legal_aid
- recovery_finance
service_floor:
- no_wrong_door_recovery_navigation
- benefit_stack_without_drop
- case_closure_or_reopen
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
- case_manager
- FEMA_or_national_assistance
- local_government
- voluntary_agency
- philanthropy
- insurer
- legal_aid
- benefits_agency
- housing_recovery_program
instrument_tags:
- case_management
- referral_acceptance
- benefit_stack
- duplication_of_benefits_review
- unmet_needs_table
- appeal
- closure
- reopen
routes_to:
- '325'
- '348'
- '351'
- '355'
- '380'
- '385'
- '389'
- '390'
- '391'
- '392'
- '393'
- '394'
- '395'
source_ids:
- S699
- S712
- S713
upstream_dependencies:
- survivor_intake
- privacy_agreement
- identity_or_substitute_documents
- legal_help
- payment_rails
- program_eligibility_map
- trusted_intermediaries
downstream_consequences:
- unmet_needs
- wrongful_denial
- delayed_repair
- housing_loss
- medical_decline
- debt
- trust_loss
equity_lenses:
- low_income_households
- renters
- no_ID_households
- limited_english_households
- disabled_people
- older_adults
- undocumented_or_mixed_status_households
- rural_households
- informal_workers
degraded_modes:
- paper_case_ledger
- community_case_conference
- phone_no_wrong_door
- single-page_program_map
- manual_referral_acceptance
- public_queue_without_private_data
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- programs_require_same_proof_differently
- duplication_rules_freeze_help
- case_manager_overload
- data_sharing_blocked_or_overbroad
- philanthropy_not_visible
- aid_sequence_not_explained
failure_modes:
- household_denied_everywhere_for_missing_wrong_document
- aid_delayed_because_programs_wait_on_each_other
- duplication_of_benefits_fear_blocks_needed_help
- case_closed_without_durable_outcome
- survivor_pays_a_scammer_to_navigate_free_programs
proof_ledgers:
- case_plan
- referral_acceptance_log
- benefit_stack_table
- duplication_of_benefits_decision_log
- unmet_needs_table
- appeal_and_reopen_log
- closure_reason_log
- public_queue_status
benefit_stacking_no_wrong_door: case ledger shows referrals accepted, benefits sequenced, duplication rules resolved,
  denials/appeals tracked, unmet needs tabled, and closure/reopen reason recorded
---

# 396 — Sequence FEMA, local aid, insurance, benefits, CDBG-DR, philanthropy, and legal help with a no-wrong-door case ledger

## Core claim

No-wrong-door recovery is an integrity gate. If survivors have to know the difference between FEMA, SBA, insurance, local relief, D-SNAP, LIHEAP, Medicaid, legal aid, CDBG-DR, philanthropy, voluntary organizations, and utility assistance while displaced, the system has shifted recovery work onto the harmed person.

FEMA's Disaster Case Management resources define case management as a recovery support function that helps survivors develop plans and connect with resources [S712]. DisasterAssistance.gov provides application and status channels [S713]. The NDRF frames recovery as a coordinated, locally led process across support functions [S699]. The archive's addition is a proof rule: coordination is real only when the case ledger shows accepted handoffs and resolved benefit sequencing.

## The no-wrong-door packet

A case ledger should track:

- the survivor's stated goals and constraints;
- verified and unverified needs;
- documents available and substitutes accepted;
- referrals sent and accepted;
- benefits applied for, approved, denied, appealed, paid, or exhausted;
- insurance, public aid, philanthropic aid, and voluntary-agency contributions;
- duplication-of-benefits decisions;
- legal issues and deadlines;
- unresolved needs and reopening conditions;
- closure reason.

## Anti-maze rule

No programme may satisfy its own paperwork while leaving the household without a path. If the case cannot be served by one programme, the owner must show where it was accepted next or why it remains an unresolved public need.

## Privacy rule

No-wrong-door does not mean no-boundary data sharing. The ledger should share the minimum needed to complete handoffs, protect sensitive status, and maintain consent, correction, and deletion rules.

## Cube rule

All survivor-facing recovery packets should expose `benefit_stacking_no_wrong_door`. Blank means the archive should assume the system has an assistance menu but not a recovery pathway.

## Rev0281 addendum — no-wrong-door includes balance sheets, documents, and closeout

The no-wrong-door ledger should now include household-function fields: balance-sheet repair, renter stability, wage-loss / DUA route, recovery mobility, essential property and device replacement, document / account recovery, and closeout / reopen status. Otherwise the case manager may sequence programmes correctly while the household still loses credit, housing, work, access, or rights.

---
Citations point to `sources/register.md`.
