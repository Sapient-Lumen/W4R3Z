# Fieldwork post-closure monitoring controls

Generated for `rev0799` from `metadata/fieldwork_postclosure_monitoring_controls.json`.

Non-private post-closure monitoring controls after closure dossiers. These rows define what must be watched after any future public-safe closure decision, but they do not activate monitoring, collect private evidence, verify outcomes, preserve source snapshots, or keep a gap closed forever.

## Monitoring policy

A closure dossier is not permanent finality. Any future closed or partially closed gap must retain post-closure monitoring for recurrence, source decay, denominator drift, policy/process change, unresolved exception growth, privacy/disclosure failure, and later affected-person evidence. Monitoring can reopen or qualify a gap; it cannot by itself prove the original outcome or keep closure valid without fresh evidence.

## Summary counts

| Metric | Count |
| --- | ---: |
| Post-closure monitoring controls | 2 |
| Gap blockers | 5 |
| Closure dossiers linked | 2 |

## Monitoring status counts

| Status | Count |
| --- | ---: |
| `not_running_no_dossier_or_monitoring_authority` | 2 |

## Gap blockers

| Gap | Monitoring controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `PCM-HC-001`, `PCM-UI-001` |
| `GAP-030-active-route-retirement-and-taxonomy-control` | `PCM-HC-001`, `PCM-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `PCM-HC-001`, `PCM-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `PCM-HC-001`, `PCM-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `PCM-HC-001`, `PCM-UI-001` |

## Control details

### `PCM-HC-001` — Housing household post-closure monitoring and no-closure-forever control

Status: `not_running_no_dossier_or_monitoring_authority`

Closure dossier: `FCD-HC-001`  
Redress verification control: `FRV-HC-001`  
Correction control: `FCC-HC-001`  
Release control: `FRC-HC-001`  
Execution control: `FEC-HC-001`  
Authorization gate: `FWAG-HC-001`  
Field-intake control: `FIC-HC-001`  
Sampling gate: `TSG-HC-001`  
Outcome-tail plan: `OTP-HC-001`

Monitoring blocker: Blocks any future housing closure from being treated as permanent. Post-closure monitoring may support reopen, qualification, or continued reliance decisions, but it does not itself prove possession retention, safe move, rehousing, arrears/subsidy cure, screening repair, durable stability, source preservation, or material power shift. Future closure remains conditional and reopenable.

| Monitoring family | Items |
| --- | --- |
| Cadence classes | initial_post_closure_recheck_window; durable_stability_recurrence_window; source_receipt_integrity_review_clock; policy_or_provider_change_triggered_review; exception_rate_threshold_review |
| Drift triggers | new household evidence contradicts possession, safe move, rehousing, subsidy, or screening repair findings; lockout, shelter return, doubled-up instability, arrears/subsidy failure, retaliation, or provider-dependence risk recurs after apparent repair; source locator, archival receipt, hash, or passage mapping fails integrity review; law, court practice, provider contract, screening vendor, rental-assistance rule, or shelter/housing pathway changes the verified route; informal exit, default, unrepresented, rare-cohort, or nonresponse rates cross the public-safe threshold recorded in the closure dossier; monitoring output creates privacy, disclosure, immigration, family-safety, or retaliation risk |
| Recheck evidence required | outside-cube public-safe review that household outcome classes remain stable through the durable-stability window; outside-cube verification that lockout, shelter return, arrears/subsidy failure, screening harm, or retaliation risk did not reappear in monitored cohorts; source-claim receipt recheck for every locator or snapshot class used in the closure dossier; public-safe unresolved-exception trend review with informal-exit, default, rare-cohort, and nonresponse limits preserved; gap owner review that determines whether the closure remains valid, becomes qualified, or reopens |
| Gap reopen rules | reopen if recurrence evidence contradicts the original household outcome finding; qualify if source preservation, informal-exit, nonresponse, or rare-cohort limits weaken but do not overturn the finding; pause reliance if privacy/disclosure review finds private artifact leakage, reidentification risk, retaliation risk, or adverse-action risk; reopen source-preservation work if any receipt relied on for closure lacks preserved locator integrity; record continued in-progress status if monitoring authority, owner, or cadence has not been approved |
| Allowed cube artifacts | public-safe monitoring status; linked closure dossier and control identifiers; source-claim receipt identifiers; drift trigger classes; cadence class; exception class counts after disclosure review; reopen decision class; scope limitation statement |
| Prohibited cube artifacts | name; address; docket_number; household_composition; contact_roster; linkage_key; court_file; provider_record; shelter_record; administrative_extract; raw_monitoring_log; raw_transcript; private_screenshot; partner_case_record; redress_case_file |

Next action: Draft the public-safe housing post-closure monitoring template: closure dossier id, cadence class, drift trigger class, source receipt recheck status, unresolved exception trend, owner reopen decision class, and limitation. Do not collect household records.

### `PCM-UI-001` — Unemployment-insurance claimant post-closure monitoring and no-closure-forever control

Status: `not_running_no_dossier_or_monitoring_authority`

Closure dossier: `FCD-UI-001`  
Redress verification control: `FRV-UI-001`  
Correction control: `FCC-UI-001`  
Release control: `FRC-UI-001`  
Execution control: `FEC-UI-001`  
Authorization gate: `FWAG-UI-001`  
Field-intake control: `FIC-UI-001`  
Sampling gate: `TSG-UI-001`  
Outcome-tail plan: `OTP-UI-001`

Monitoring blocker: Blocks any future UI closure from being treated as permanent. Post-closure monitoring may support reopen, qualification, or continued reliance decisions, but it does not itself prove payment, hold removal, overpayment debt, waiver/refund, appeal correction, burden reduction, source preservation, or material power shift. Future closure remains conditional and reopenable.

| Monitoring family | Items |
| --- | --- |
| Cadence classes | initial_post_closure_recheck_window; recurrence_window_for_payment_hold_debt_or_appeal_friction; source_receipt_integrity_review_clock; policy_or_system_change_triggered_review; exception_rate_threshold_review |
| Drift triggers | new claimant complaints or appeal patterns contradict the closure finding; payment delay, identity hold, overpayment debt, waiver, appeal, or representative-access friction recurs after apparent repair; source locator, archival receipt, hash, or passage mapping fails integrity review; law, policy, vendor, model, fraud-control, or case-management process changes the verified pathway; nonresponse, rare-cohort suppression, or unresolved exception rates cross the public-safe threshold recorded in the closure dossier; monitoring output creates privacy, disclosure, or adverse-action risk |
| Recheck evidence required | outside-cube public-safe review that claimant outcome classes remain stable through the recurrence window; outside-cube verification that new holds, debts, appeal friction, or representative-access failures did not reappear in monitored cohorts; source-claim receipt recheck for every locator or snapshot class used in the closure dossier; public-safe unresolved-exception trend review with nonresponse and rare-cohort limits preserved; gap owner review that determines whether the closure remains valid, becomes qualified, or reopens |
| Gap reopen rules | reopen if recurrence evidence contradicts the original claimant outcome finding; qualify if source preservation, nonresponse, or rare-cohort limits weaken but do not overturn the finding; pause reliance if privacy/disclosure review finds private artifact leakage or adverse-action risk; reopen source-preservation work if any receipt relied on for closure lacks preserved locator integrity; record continued in-progress status if monitoring authority, owner, or cadence has not been approved |
| Allowed cube artifacts | public-safe monitoring status; linked closure dossier and control identifiers; source-claim receipt identifiers; drift trigger classes; cadence class; exception class counts after disclosure review; reopen decision class; scope limitation statement |
| Prohibited cube artifacts | name; claim_number; social_security_number; contact_roster; linkage_key; payment_record; debt_record; appeal_file; administrative_extract; raw_monitoring_log; raw_transcript; private_screenshot; partner_case_record; redress_case_file |

Next action: Draft the public-safe UI post-closure monitoring template: closure dossier id, cadence class, drift trigger class, source receipt recheck status, unresolved exception trend, owner reopen decision class, and limitation. Do not collect claimant records.


## Privacy posture

The cube may hold public-safe monitoring status, linked control identifiers, source-claim receipt identifiers, cadence classes, drift trigger classes, exception classes, and reopen-decision classes. It must not hold private claimant or household evidence, linkage keys, contact rosters, claim numbers, docket numbers, addresses, payment records, court files, partner case records, transcripts, recordings, raw audit logs, monitoring extracts, or reidentification material.
