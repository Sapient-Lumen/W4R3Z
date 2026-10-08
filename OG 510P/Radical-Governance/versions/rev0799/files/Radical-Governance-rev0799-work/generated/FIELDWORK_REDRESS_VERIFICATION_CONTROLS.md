# Fieldwork redress verification controls

Generated for `rev0799` from `metadata/fieldwork_redress_verification_controls.json`.

Non-closing post-correction redress-verification controls for future UI claimant and housing household fieldwork. These controls define how to verify follow-through after correction or redress routing without storing private remedy files or treating a ledger as outcome proof.

## Closure policy

A redress-verification control row cannot close a live gap. It can only block premature reliance until outside-cube owners verify whether the person or household was actually made whole, whether unresolved exceptions remain, and whether any corrected public artifact is aligned with the separate remedy record.

## Summary counts

| Metric | Count |
| --- | ---: |
| Redress verification controls | 2 |
| Gap blockers | 4 |
| Correction controls linked | 2 |

## Verification status counts

| Status | Count |
| --- | ---: |
| `not_verified_redress_review_required_no_outcome` | 2 |

## Gap blockers

| Gap | Redress verification controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `FRV-HC-001`, `FRV-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `FRV-HC-001`, `FRV-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `FRV-HC-001`, `FRV-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `FRV-HC-001`, `FRV-UI-001` |

## Control details

### `FRV-HC-001` — Housing household redress follow-through verification and no-outcome-by-redress-route control

Status: `not_verified_redress_review_required_no_outcome`

Correction control: `FCC-HC-001`  
Release control: `FRC-HC-001`  
Execution control: `FEC-HC-001`  
Authorization gate: `FWAG-HC-001`  
Field-intake control: `FIC-HC-001`  
Sampling gate: `TSG-HC-001`  
Outcome-tail plan: `OTP-HC-001`

Closure blocker: Blocks housing affected-person and material-outcome closure until outside-cube evidence verifies possession or safe move, lockout repair, rehousing, arrears/subsidy cure, screening correction, and durable stability for required cohorts, including unresolved exceptions and nonresponse bias; a redress route, ticket, correction, or ledger is not outcome proof.

| Verification family | Items |
| --- | --- |
| Required verification artifacts | outside-cube remedy-owner record for each verified household cohort and housing remedy class; public-safe redress verification ledger with status, remedy class, due-window class, and exception class only; separate proof that possession retention, lockout repair, re-housing, arrears cure, subsidy restoration, or screening correction occurred where applicable outside the cube; negative-result and unresolved-exception ledger that cannot be suppressed by publication of a corrected output; follow-up window and recertification clock for post-case displacement, screening recurrence, retaliation, or renewed instability |
| Remedy verification | verify actual possession retention or safe move outcome, not merely representation, filing disposition, or dismissal; verify lockout repair, re-entry, repairs, subsidy restoration, arrears cure, or relocation assistance when those were the harmed pathway; verify screening, debt, judgment, or record-correction follow-through separately from public-output correction; verify durable stability at required follow-up windows without storing address or household composition in the cube; verify non-user and informal-exit cohorts rather than relying only on court-recorded households |
| Exception follow-up | track unresolved, partially remedied, disputed, nonresponsive, unreachable, doubled-up, sheltered, relocated, and informal-exit cohorts as blockers rather than omissions; escalate retaliation, landlord/provider coercion, shelter access, immigration, disability, or family-safety risk before any household-specific follow-up is attempted; require nonresponse-bias review before claiming the verified tail represents default, informal displacement, unrepresented, or non-user cohorts; keep remedy disputes, court files, shelter/provider records, and household communications outside the cube with only public-safe blocker status retained |
| Material outcome fields | possession_retained_or_safe_move; lockout_or_exclusion_repaired; rehousing_or_shelter_stability_verified; arrears_or_subsidy_cure_completed; screening_or_record_harm_corrected; retaliation_or_coercion_risk_checked; durable_stability_window_checked |
| Escalation controls | assign redress owner, due date, and senior escalation path for every unresolved housing remedy class; treat repeated displacement, unworked emergency assistance, failed counsel handoff, or screening repair failure as potential internal-control deficiencies; require corrective-action tracking, testing, and validation before marking the redress control as verified outside the cube; surface aggregate unresolved-exception counts only after disclosure review and suppression checks |
| Allowed cube artifacts | public-safe verification status; remedy class; due-window class; exception class; aggregate blocker count after disclosure review; source-claim receipt identifiers; non-closing closure blocker statement |
| Prohibited cube artifacts | name; address; docket_number; contact_roster; linkage_key; administrative_extract; court_file; possession_record; shelter_record; screening_record; landlord_or_provider_record; raw_transcript; raw_audio; private_screenshot; partner_case_record; incident_report_detail; breach_detail; audit_log; redress_case_file; household_composition |
| Pause/stop conditions | pause reliance when possession, rehousing, subsidy, screening, lockout, coercion, or durable-stability verification is incomplete; pause reliance when unresolved exceptions or nonresponse bias could change the redress conclusion; pause reliance when a corrected output is not aligned with the separate remedy record; pause reliance when retaliation, landlord/provider coercion, shelter access, or family-safety risk is unresolved; pause reliance when aggregate counts would expose a rare cohort, building, docket path, or household location |

Next action: Draft the public-safe housing redress verification ledger columns for remedy class, due-window class, exception class, and blocker status without addresses, docket numbers, or household records.

### `FRV-UI-001` — Unemployment-insurance claimant redress follow-through verification and no-outcome-by-redress-route control

Status: `not_verified_redress_review_required_no_outcome`

Correction control: `FCC-UI-001`  
Release control: `FRC-UI-001`  
Execution control: `FEC-UI-001`  
Authorization gate: `FWAG-UI-001`  
Field-intake control: `FIC-UI-001`  
Sampling gate: `TSG-UI-001`  
Outcome-tail plan: `OTP-UI-001`

Closure blocker: Blocks UI affected-person and material-outcome closure until outside-cube evidence verifies actual payment, hold removal, debt cure, appeal correction, and burden repair for required cohorts, including unresolved exceptions and nonresponse bias; a redress route, ticket, correction, or ledger is not outcome proof.

| Verification family | Items |
| --- | --- |
| Required verification artifacts | outside-cube remedy-owner record for each verified claimant cohort and remedy class; public-safe redress verification ledger with status, remedy class, due-window class, and exception class only; separate proof that payment, hold removal, overpayment waiver, appeal correction, or burden repair occurred where applicable outside the cube; negative-result and unresolved-exception ledger that cannot be suppressed by publication of a corrected output; follow-up window and recertification clock for late reversals, offsets, overpayment notices, or recurrent access barriers |
| Remedy verification | verify actual payment disbursement, not merely eligibility correction or notice issuance; verify identity, access, or fraud hold removal without storing identifiers in the cube; verify overpayment waiver, refund, offset reversal, or repayment-plan correction when debt harm was present; verify appeal, reconsideration, or hearing correction separately from public-output correction; verify burden repair including reduced repeat submissions, channel switching, and representative access where those were the harmed pathway |
| Exception follow-up | track unresolved, partially remedied, disputed, nonresponsive, deceased, unreachable, and withdrawn cohorts as blockers rather than omissions; escalate adverse-action, retaliation, fraud-referral, or debt-collection risk before any participant-specific follow-up is attempted; require nonresponse-bias review before claiming the verified tail represents abandoned, denied, delayed, or non-user cohorts; keep remedy disputes and claimant communications outside the cube with only public-safe blocker status retained |
| Material outcome fields | actual_payment_or_backpay; hold_removed; overpayment_waived_or_refunded; appeal_or_reconsideration_corrected; representative_or_assisted_access_restored; burden_reduced; reversal_or_recurrence_window_checked |
| Escalation controls | assign redress owner, due date, and senior escalation path for every unresolved remedy class; treat systemic nonpayment, repeated holds, unworked waivers, or appeal noncompliance as potential internal-control deficiencies; require corrective-action tracking, testing, and validation before marking the redress control as verified outside the cube; surface aggregate unresolved-exception counts only after disclosure review and suppression checks |
| Allowed cube artifacts | public-safe verification status; remedy class; due-window class; exception class; aggregate blocker count after disclosure review; source-claim receipt identifiers; non-closing closure blocker statement |
| Prohibited cube artifacts | name; address; claim_number; contact_roster; linkage_key; administrative_extract; payment_record; overpayment_file; waiver_file; appeal_record; fraud_referral; raw_transcript; raw_audio; private_screenshot; partner_case_record; incident_report_detail; breach_detail; audit_log; redress_case_file; household_composition |
| Pause/stop conditions | pause reliance when payment, waiver, appeal, hold, burden, or representative-access verification is incomplete; pause reliance when unresolved exceptions or nonresponse bias could change the redress conclusion; pause reliance when a corrected output is not aligned with the separate remedy record; pause reliance when adverse-action, fraud-referral, retaliation, or debt-collection risk is unresolved; pause reliance when aggregate counts would expose a rare cohort or identifiable claimant path |

Next action: Draft the public-safe redress verification ledger columns for UI remedy class, due-window class, exception class, and blocker status without claimant identifiers or payment records.


## Privacy posture

Names, addresses, claim numbers, docket numbers, case files, linkage keys, administrative extracts, private complaint details, redress determinations, payment records, waiver files, appeal records, possession records, screening files, and household follow-up evidence stay outside the cube. The cube may store only public-safe verification status, remedy class, due-window class, blocker status, source-receipt identifiers, and non-closing summary counts after disclosure review.
