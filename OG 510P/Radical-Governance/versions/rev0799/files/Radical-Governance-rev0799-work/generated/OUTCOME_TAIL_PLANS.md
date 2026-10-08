# Outcome-tail sampling plans

Generated for `rev0799` from `metadata/outcome_tail_plans.json`.

Privacy-bounded case-tail sampling plans for moving from aggregate field signals to closure-ready affected-person outcome evidence.

## Privacy posture

This file specifies cohorts, fields, limits, and closure floors. It does not contain names, claim numbers, addresses, case numbers, account identifiers, or private records.

## Summary

| Metric | Count |
| --- | ---: |
| Plans | 2 |
| Cohorts | 8 |
| Outcome-tail fields | 16 |

## Gap coverage

| Gap | Plans |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `OTP-HC-001`, `OTP-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `OTP-HC-001`, `OTP-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `OTP-HC-001`, `OTP-UI-001` |

## Outcome-tail fields

| Field | Count |
| --- | ---: |
| `appeal_or_waiver_result` | 1 |
| `counsel_access` | 1 |
| `debt_or_arrears` | 1 |
| `debt_status` | 1 |
| `durable_stability` | 1 |
| `hardship_tail` | 1 |
| `informal_eviction` | 1 |
| `money_received` | 1 |
| `non_user_denominator` | 1 |
| `payment_delay_days` | 1 |
| `physical_displacement` | 1 |
| `possession` | 1 |
| `screening_aftereffect` | 1 |
| `shelter_or_rehousing` | 1 |
| `staff_assistance` | 1 |
| `time_burden` | 1 |

## Plans

### `OTP-HC-001` — `housing_continuity_household_outcome_tail`

Closure floor: A privacy-approved household sample must join filing or threat to counsel access, payment posting, possession, informal exit, lockout, shelter/re-housing, screening consequences, and durable stability.

| Cohort | Denominator role | Exclusion risk |
| --- | --- | --- |
| `hc-represented-household` | counsel-success route | Represented households can overstate program success if unrepresented or informal exits are omitted. |
| `hc-unrepresented-or-default` | capacity-failure route | Capacity failure becomes invisible if only full-representation cases are followed. |
| `hc-informal-exit-or-lockout` | outside-docket route | Physical displacement can occur without a formal eviction outcome. |
| `hc-screening-or-reapplication-tail` | future-access route | A corrected record may not restore a lost housing opportunity. |

First next action: Use metadata/tail_sampling_gates.json to pick a jurisdiction/window, privacy posture, sample frame, nonresponse-bias plan, and source-preservation route before any field-tail collection.

### `OTP-UI-001` — `unemployment_insurance_claimant_outcome_tail`

Closure floor: A privacy-approved sample must join filing burden and channel access to eligibility, payment timing, overpayment/debt status, waiver/appeal outcome, continuing certification, and hardship tail.

| Cohort | Denominator role | Exclusion risk |
| --- | --- | --- |
| `ui-paid-without-hold` | baseline claimant route | Can make the system look functional by excluding people blocked before payment. |
| `ui-held-or-identity-friction` | access and fraud-control failure route | Fraud-control friction may disappear if only completed claims are sampled. |
| `ui-overpayment-waiver-appeal` | debt and remedy route | Debt harm may persist even after a correction route exists. |
| `ui-abandoned-or-nonuser` | outside-channel route | The most burdened people may never appear in portal or survey data. |

First next action: Use metadata/tail_sampling_gates.json to pick a jurisdiction/window, privacy posture, sample frame, nonresponse-bias plan, and source-preservation route before any field-tail collection.
