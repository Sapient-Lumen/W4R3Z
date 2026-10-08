---
project: Immoral Wealth
revision: rev0381
title: social-security-medicare-claim-security-rev0318-ma-steering-lock-in-broker-incentive-exit-rights-bridge-rev0381
status: current
---

# Rev0381 MA steering, lock-in, broker incentive, and exit-rights bridge

Revision: `rev0381`  
Base: `rev0380`  
Status: **not certified current**  

This bridge prevents the MA branch from certifying a denial/remedy/payment row while ignoring how the beneficiary entered the plan or whether the beneficiary can exit after illness or claim failure.

## Minimum row fields

- `beneficiary_id_or_anonymized_join_key`
- `enrollment_event_id`
- `application_channel`
- `broker_or_agent_npn`
- `tpmo_or_lead_generator_id`
- `hcp_referral_source_id`
- `compensation_amount_initial`
- `renewal_compensation_amount`
- `bonus_or_marketing_payment_marker`
- `financial_incentive_or_bonus_marker`
- `marketing_or_hcp_referral_payment_marker`
- `written_consent_to_share_lead_data`
- `plan_universe_presented`
- `plans_not_presented_or_blocked`
- `beneficiary_need_profile_at_enrollment`
- `beneficiary_disability_status`
- `dual_lis_or_complex_care_marker`
- `plan_suitability_rationale`
- `misleading_marketing_complaint_id`
- `cms_complaint_tracking_module_or_ctm_id`
- `special_enrollment_period_or_correction_right`
- `correction_or_reinstatement_outcome`
- `medigap_guaranteed_issue_status`
- `medigap_underwriting_barrier`
- `medigap_premium_feasibility`
- `exit_to_traditional_medicare_feasibility`
- `serious_illness_or_cancer_diagnosis_after_enrollment`
- `post_enrollment_denial_or_access_problem`
- `claim_security_row_join_key`
- `service_request_id`
- `organization_determination_outcome`
- `beneficiary_service_restoration_date`
- `payment_or_cost_sharing_restoration`
- `independent_review_or_adjudication_status`

## False pass blocks

- No enrollment-neutral pass: the MA row must preserve how the beneficiary entered the plan and who was paid or otherwise incentivized.
- No broker-disclosure pass: commission disclosure or capped compensation does not prove neutral plan selection.
- No compensation-cap pass: a compensation rule cannot substitute for row-level proof that financial incentives did not distort plan presentation.
- No complaint-only pass: a complaint or CTM entry must be joined to correction, coverage, restoration, and exit outcomes.
- No Medigap-exit pass: exit feasibility requires guaranteed-issue status, underwriting barrier, premium feasibility, and timing, not just the theoretical option to switch.
- No DOJ-allegation pass: DOJ allegations create contradiction-risk evidence but not final proof for a specific row.
- No OIG-work-plan pass: an active work-plan item identifies unresolved risk and cannot certify a current case.
- No marketing-compliance pass: plan/broker compliance documentation must be joined to beneficiary need, plan universe, and post-enrollment claim outcomes.
- No plan-universe pass: a list of available plans does not prove which plans were actually presented or withheld.
- No independent-review pass: plan selection and exit rights require independent review or adjudication where allegations or complaints are material.

## Source boundary

New sources: `S628, S629, S630, S631, S632, S633, S634, S635`. Reused sources: `S599, S603, S604, S626, S627`.

Rev0381 is a noncertifying bridge. It requires a joined enrollment-to-claim-to-exit row before any Medicare Advantage claim-security certification.
