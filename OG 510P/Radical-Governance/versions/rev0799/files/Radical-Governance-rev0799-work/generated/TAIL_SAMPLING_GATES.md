# Tail sampling gates

Generated for `rev0799` from `metadata/tail_sampling_gates.json`.

Closure-blocking sampling and preservation gates that convert UI claimant and housing household outcome-tail plans into owner-checkable fieldwork prerequisites without collecting private data in the cube.

## Privacy posture

This file contains only sampling frames, cohort gates, fieldwork controls, preservation controls, and closure blockers. It must not contain names, claim numbers, docket numbers, addresses, account IDs, private screenshots, or partner-held case records.

## Closure policy

A tail sampling gate is design readiness, not field validation. It cannot close an affected-person, source-preservation, or material-outcome gap until a privacy-approved sample has been collected, bias risk documented, source passages preserved at an approved level, and only aggregate-safe results are added to the cube.

## Summary

| Metric | Count |
| --- | ---: |
| Gates | 2 |
| Cohort gate rows | 8 |
| Linked source-claim receipts | 10 |

## Gate statuses

| Status | Count |
| --- | ---: |
| `design_ready_not_collected` | 2 |

## Gap blockers

| Gap | Gates |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `TSG-HC-001`, `TSG-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `TSG-HC-001`, `TSG-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `TSG-HC-001`, `TSG-UI-001` |

## Source-claim receipt dependencies

| Receipt | Count |
| --- | ---: |
| `SCR-EVIDENCE-001` | 2 |
| `SCR-HC-001` | 1 |
| `SCR-HC-002` | 1 |
| `SCR-NRBA-001` | 2 |
| `SCR-OES-001` | 2 |
| `SCR-OMB-001` | 1 |
| `SCR-PRIV-001` | 2 |
| `SCR-SAMPLE-001` | 2 |
| `SCR-UI-001` | 1 |
| `SCR-UI-002` | 1 |

## Gates

### `TSG-HC-001` — Housing continuity household outcome-tail sampling gate

Outcome-tail plan: `OTP-HC-001`  
Status: `design_ready_not_collected`

Target population: Households facing arrears, notice, filing, default, representation triage, informal exit, lockout, shelter entry, re-housing, or screening aftereffect during a defined jurisdiction/window.

Sampling frame: Must combine court docket exposure, legal-aid/provider intake, rental-assistance or payment-posting signals, tenant hotline/community organization referrals, shelter or re-housing service signals, and an informal-exit/lockout recruitment route. Court filings or represented cases alone are not a sampling frame.

| Cohort | Minimum observation goal | Denominator audit |
| --- | --- | --- |
| `hc-represented-household` | pilot_tail_present; closure_generalization_requires provider/court frame and follow-up | Representation success cannot stand in for unrepresented, default, informal-exit, or lockout outcomes. |
| `hc-unrepresented-or-default` | pilot_tail_present; closure_generalization_requires eligibility/capacity/default frame | Program capacity failure must remain visible when eligible households did not receive full representation. |
| `hc-informal-exit-or-lockout` | pilot_tail_present; closure_generalization_requires community/hotline/shelter recruitment route | Physical displacement can occur before, outside, or after formal court outcomes. |
| `hc-screening-or-reapplication-tail` | pilot_tail_present; closure_generalization_requires post-case housing-search frame | A dismissed or sealed case is not closure if screening, debt, or lost housing opportunity persists. |

Nonresponse-bias plan: Before any closure claim, record cohort response rates, provider/court/community frame differences, missingness in follow-up, attrition after displacement, and limits of auxiliary data. Unknown informal-exit denominators must be reported as a live bias risk.

Closure blocker: No housing affected-person or material-outcome gap can close from this gate. It only defines the minimum fieldwork and preservation prerequisites for a future privacy-approved household-tail collection.

Next action: Select a jurisdiction/window and partner protocol, then draft a privacy review, retaliation-risk review, and nonresponse-bias plan before any household tail is collected or summarized.

### `TSG-UI-001` — Unemployment insurance claimant outcome-tail sampling gate

Outcome-tail plan: `OTP-UI-001`  
Status: `design_ready_not_collected`

Target population: People who attempted to obtain unemployment benefits through filing, certification, issue-resolution, overpayment/waiver/appeal, staff-assisted, or abandoned/non-user routes during a defined window.

Sampling frame: Must combine agency claim/issue states, survey or observation follow-up consent, legal-aid or community navigator referrals, field-office assisted access, overpayment/appeal records, and a documented non-user recruitment route. A claimant-visible portal population alone is not a sampling frame.

| Cohort | Minimum observation goal | Denominator audit |
| --- | --- | --- |
| `ui-paid-without-hold` | pilot_tail_present; closure_generalization_requires_owner-approved sample size and response-rate justification | Do not use this cohort to represent held, overpaid, appealed, abandoned, or non-user routes. |
| `ui-held-or-identity-friction` | pilot_tail_present; closure_generalization_requires issue-state and hold-resolution frame | Identity, fraud-control, and document-friction holds must remain visible even if the claim is later paid. |
| `ui-overpayment-waiver-appeal` | pilot_tail_present; closure_generalization_requires debt/waiver/appeal frame | A corrected monetary determination is not closure if collection, offset, or hardship persists. |
| `ui-abandoned-or-nonuser` | pilot_tail_present; closure_generalization_requires non-user recruitment and exclusion report | Non-users cannot be inferred from completed claims, survey responders, or portal analytics alone. |

Nonresponse-bias plan: Before any closure claim, record expected response rates by cohort, actual response rates, auxiliary data available for nonresponse analysis, missingness by key outcome field, and mitigation limits. Below-threshold or unknown response requires an explicit nonresponse-bias caveat.

Closure blocker: No UI affected-person or material-outcome gap can close from this gate. It only defines the minimum fieldwork and preservation prerequisites for a future privacy-approved claimant-tail collection.

Next action: Select an owner-approved jurisdiction/window and draft a privacy review plus nonresponse-bias plan before collecting or summarizing any claimant tail.
