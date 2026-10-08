---
id: '397'
revision_added: rev0281
status: canon
object_type: ledger
domain_tags:
- recovery_outcomes
- longitudinal_recovery
- case_closure
- service_floor_audit
- community_resilience
service_floor:
- functional_recovery_outcome
- long_tail_case_visibility
- public_closure_with_reopen_path
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
- recovery_coordinator
- case_manager
- community_recovery_group
- public_health_agency
- housing_lead
- benefits_agency
- local_government
instrument_tags:
- longitudinal_case_follow_up
- outcome_ledger
- cohort_sample
- public_dashboard
- reopen_rule
- after_action_budget
routes_to:
- '355'
- '356'
- '365'
- '371'
- '389'
- '396'
- '404'
source_ids:
- S699
- S714
- S715
upstream_dependencies:
- survivor_intake
- case_management
- privacy_agreement
- housing_health_school_utility_status
- benefit_stack
- community_outreach
- public_dashboard
downstream_consequences:
- false_recovery
- unseen_homelessness
- medical_decline
- student_absence
- debt_spiral
- trust_loss
- program_capture
equity_lenses:
- renters
- low_income_households
- disabled_people
- older_adults
- limited_english_households
- no_phone_or_no_internet_households
- rural_households
- informal_households
degraded_modes:
- sample_based_follow_up
- community_partner_check
- phone_and_paper_status_update
- anonymous_public_backlog
- reopen_without_new_full_application
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- case_closed_when_referral_made_not_when_outcome_reached
- short_funding_cycles
- survivors_move_or_lose_contact
- aggregate_recovery_masks_household_failure
- privacy_blocks_follow_up_or_follow_up_becomes_surveillance
failure_modes:
- registered_household_marked_recovered_without_housing_income_medicine_school_or_utility_stability
- dashboard_counts_closed_cases_as_success
- unmet_need_becomes_private_debt
- long_tail_trauma_and_displacement_disappear
proof_ledgers:
- functional_recovery_cohort
- case_closure_reason_log
- reopen_request_log
- household_outcome_sample
- service_floor_exception_register
- public_recovery_outcome_dashboard
recovery_outcome_state: closed only when household function is demonstrated or unresolved need is publicly carried
  forward with owner, next action, and reopen path
---

# 397 — Track household functional recovery outcomes before case closure hides long-tail loss

## Core claim

Recovery is not finished when a case is closed, a referral is issued, or a dashboard says a service was restored. It is finished only when the household can function: safe housing, medicine, school, food, utilities, income or benefit path, reachable transport, valid documents, and an appeal/reopen route all survive after the first stabilization window.

FEMA's NDRF organizes recovery across housing, health and social services, economic recovery, infrastructure, natural/cultural resources, and community planning [S699]. FEMA's lifelines toolkit distinguishes stabilization and recovery outcomes [S714]. NIST's community resilience guidance pushes communities to set recovery goals for the functions buildings and infrastructure support [S715]. The archive's addition is a survivor-level proof rule: community recovery claims must be sampled against household function, not only infrastructure status.

## Functional recovery ledger

A long-tail recovery ledger should answer:

- Where is the household living, and is it safe, affordable, and connected to utilities?
- Can children attend school or childcare with transport and meals?
- Are medicines, devices, chronic care, and records continuous?
- Is food access repeatable next cycle rather than one-time distribution?
- Is income, cash, or benefit support active enough to avoid predatory debt?
- Are documents, phone/account access, and notices working?
- Is there an unresolved-need owner, appeal, and reopen path?

## Anti-false-closure rule

A case may close administratively, but the public recovery ledger should preserve the reason: durable outcome, transferred case, unreachable after documented outreach, survivor declined, duplicate, ineligible with appeal notice, or unresolved public need. Anything else is false closure.

## Privacy rule

Longitudinal follow-up must not become surveillance. Publish aggregate backlogs, exceptions, and closure reasons; protect household-level status; permit correction and deletion where legally possible; and use trusted intermediaries for households that cannot safely engage official portals.

## Cube rule

Every stabilization-to-recovery pathway should expose `recovery_outcome_state`. Blank means the archive should assume recovery is being counted at intake, assistance, or closure rather than at functional outcome.

---
Citations point to `sources/register.md`.
