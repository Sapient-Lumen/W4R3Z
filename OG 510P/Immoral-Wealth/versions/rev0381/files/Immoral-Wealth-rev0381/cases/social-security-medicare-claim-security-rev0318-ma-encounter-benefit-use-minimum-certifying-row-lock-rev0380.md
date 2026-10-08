---
revision_current: rev0380
generated_at: 2026-06-18T22:18:00Z
title: MA encounter, benefit-use, and minimum certifying row lock
status: not_certified_current
case_id: social-security-medicare-claim-security-rev0318
---

# MA encounter, benefit-use, and minimum certifying row lock — rev0380

This bridge blocks the last easy false completion before acquisition: plan benefit design, PBP offerings, encounter records, supplemental-benefit utilization reports, and rebate allocations are all useful, but none proves that a requested service was furnished, paid, restored, and valuable to the beneficiary.

## Required distinction

A certifying row must distinguish: **benefit offered → benefit requested → benefit denied/approved → service furnished → payment/cost sharing → remedy/restoration → actual benefit use/nonuse → public-cost incidence**.

## Minimum certifying row fields

- `contract_id`
- `plan_id`
- `pbp_id`
- `contract_year`
- `service_month`
- `county_fips`
- `beneficiary_privacy_key`
- `beneficiary_subgroup_key`
- `part_c_enrollment_source`
- `plan_characteristics_source`
- `pbp_benefit_source`
- `benefit_category_code`
- `benefit_offered_flag`
- `benefit_eligible_flag`
- `service_request_id`
- `request_received_date`
- `requested_service_category`
- `requested_service_code`
- `coverage_authority_locator`
- `medicare_coverage_rule_locator`
- `internal_criteria_id`
- `delegated_entity_id`
- `algorithmic_review_or_ai_marker`
- `organization_determination_outcome`
- `denial_reason_code`
- `notice_id`
- `reconsideration_id`
- `appeal_filed_flag`
- `appeal_outcome`
- `ire_or_alj_reference`
- `effectuation_deadline`
- `effectuation_completed_date`
- `encounter_file_type`
- `encounter_join_key`
- `claim_control_number`
- `latest_claim_indicator`
- `final_action_indicator`
- `service_from_date`
- `service_through_date`
- `diagnosis_code_set`
- `procedure_hcpcs_or_revenue_or_rug_code`
- `provider_npi`
- `provider_active_accepting_appointment_flag`
- `encounter_no_payment_variables_flag`
- `payment_source_id`
- `plan_paid_amount`
- `member_cost_sharing_amount`
- `provider_payment_restoration_date`
- `beneficiary_service_restoration_date`
- `supplemental_benefit_utilization_count`
- `supplemental_benefit_net_cost`
- `supplemental_benefit_denied_not_in_utilization_flag`
- `rebate_allocation_amount`
- `rebate_actual_use_evidence`
- `part_b_premium_incidence`
- `taxpayer_cost_incidence`
- `risk_score`
- `diagnosis_source_type`
- `service_record_linkage_flag`
- `radv_result_or_recovery_status`
- `source_ids`
- `suppression_or_dua_limitations`

## False-pass blocks

- No encounter-data pass: a MA encounter row can show a furnished service but cannot alone prove payment, denied care, cost sharing, or restoration.
- No PBP/offered-benefit pass: approved benefits and plan design do not prove actual use, access, eligibility, denial, or value.
- No zero-utilization pass: zero or missing supplemental-benefit utilization cannot distinguish no demand from denial or failed access without request/denial evidence.
- No rebate-allocation pass: bid/rebate projections may not reflect actual use and cannot prove beneficiary value.
- No supplemental-benefit-reporting pass: furnished/approved benefit utilization and cost rows exclude denied supplemental-benefit coverage unless separately joined to request/denial records.
- No carrier/SNF encounter-only pass: encounter files lack payment variables and therefore must be joined to payment/cost-sharing/remedy sources.
- No KFF aggregate pass: current plan-level benefit and prior authorization aggregates cannot replace contract/PBP/request/service/subgroup rows.
- No MedPAC projection pass: rebate amounts and allocations are public-cost context, not proof of service delivery or claim restoration.
- No Part C reporting-only pass: organization-determination/reconsideration data must be joined to encounter/payment/remedy and benefit-use rows.
- No independent-review pass: this bridge remains noncertifying until a row is acquired and independently reviewable.

## Status

Not certified current. The bridge only defines the row lock; it does not supply the acquired row.
