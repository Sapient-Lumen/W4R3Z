# Fieldwork release controls

Generated for `rev0799` from `metadata/fieldwork_release_controls.json`.

Non-closing public-output release controls for future UI claimant and housing household fieldwork outputs. These controls govern disclosure-limited publication posture only; they do not authorize release, de-identify data, or prove outcomes.

## Closure policy

A release-control row cannot close a live gap. It can block premature reliance on public outputs until disclosure limitation, de-identification/re-identification review, method integrity, harm review, and errata/retraction controls are complete outside the cube.

## Summary counts

| Metric | Count |
| --- | ---: |
| Release controls | 2 |
| Gap blockers | 4 |
| Execution controls linked | 2 |

## Release status counts

| Status | Count |
| --- | ---: |
| `not_released_disclosure_review_required_no_public_outcome` | 2 |

## Gap blockers

| Gap | Release controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `FRC-HC-001`, `FRC-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `FRC-HC-001`, `FRC-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `FRC-HC-001`, `FRC-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `FRC-HC-001`, `FRC-UI-001` |

## Control details

### `FRC-HC-001` — Housing household public-output release, disclosure-limitation, method-integrity, and no-output-by-release control

Status: `not_released_disclosure_review_required_no_public_outcome`

Execution control: `FEC-HC-001`  
Authorization gate: `FWAG-HC-001`  
Field-intake control: `FIC-HC-001`  
Sampling gate: `TSG-HC-001`  
Outcome-tail plan: `OTP-HC-001`

Closure blocker: Blocks closure because a disclosure-reviewed housing public output would still need outcome-tail evidence, source preservation, steward approval, and material-distribution interpretation; release review alone is not possession, re-housing, screening correction, or durable-stability proof.

| Release family | Items |
| --- | --- |
| Required release artifacts | disclosure-review memo held outside the cube; public-output locator and version stamp if a release later exists; small-cell, rare-geography, rare-household-trajectory, and rare-provider review status; suppression, aggregation, rounding, perturbation, noise, synthetic, or formal privacy method note where applicable; nonresponse, denominator, excluded-cohort, follow-up-window, and unresolved-harm statement; public-narrative and quote-permission review status; errata, withdrawal, and retraction route |
| Disclosure limitation | apply disclosure limitation before public release, including suppression or aggregation for small-cell and rare-cohort housing outputs; check complementary disclosure risk where totals, geographies, providers, shelters, courts, or landlords could reveal a suppressed household cohort; document whether rounding, perturbation, noise infusion, synthetic output, or formal privacy methods change interpretation; do not publish cells or combinations that identify an individual, household, building, address, shelter, provider, landlord, court docket, or rare housing trajectory |
| De-identification | de-identification is treated as risk reduction, not elimination; review re-identification risk from address, building, provider, shelter, docket, landlord, geography, time sequence, and narrative detail; do not call an output anonymous merely because names and docket numbers were removed; publish de-identification limits and residual risk where public conclusions rely on suppressed or transformed data |
| Public narrative | no household quote, address, building, shelter, provider, landlord, docket, court, or rare trajectory detail without permission and re-identification review; narrative examples must not reveal domestic safety, immigration-risk, disability, child household, shelter location, arrears, screening record, or possession status through context; aggregate represented, unrepresented, default, informal exit, re-housed, and unstable households separately from durable-stability claims; avoid converting compelling anecdotes into denominator claims |
| Quality/integrity | publish method, nonresponse, denominator exclusions, weighting or no-weighting choice, follow-up window, and uncertainty with any finding; separate process metrics from outcome metrics and label both clearly; state which cohorts were suppressed, excluded, or too sparse for public release; pre-register or version the release claims so later edits are visible |
| Participant/community harm review | harm review considers lockout, retaliation, landlord/adverse-party exposure, domestic safety, disability, immigration, child household, and shelter risks before release; participant-facing, advocate, or community review may be required for quotes or sensitive narrative claims; release does not imply household endorsement or housing stability; community or tenant feedback is logged as review status only, not raw private narrative |
| Errata/retraction | errata route corrects method, denominator, suppression, nonresponse, or interpretation errors; withdraw or retract output when disclosure risk, re-identification risk, participant harm, source drift, or analytic error defeats safe reliance; notify owner, privacy/security, data custodian, and affected partner when output changes alter risk or interpretation; archive records public-safe correction status and not raw error details |
| Allowed cube artifacts | public-output title and locator if released; version stamp and release status; aggregate-safe method limits; suppression/disclosure review status without reviewer workpapers; public-safe errata status |
| Prohibited public outputs | name; address; docket_number; case_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; shelter_location; provider_name; landlord_name; building_identifier; incident_report_detail; breach_detail; audit_log; secure_environment_raw_output; reviewer_workpaper; small_cell; rare_cohort_narrative |
| Pause/stop conditions | disclosure review unresolved; suppression or complementary suppression unresolved; small-cell or rare-cohort risk unresolved; re-identification risk unresolved; withdrawal or quote permission unresolved; PII breach or incident review unresolved; audit-log or retention authority failure unresolved; errata, withdrawal, or retraction trigger present; method or nonresponse limit missing from release |

Next action: Draft a public-output checklist and errata template for any future housing household pilot; keep it non-releasing until an owner-approved project exists outside the cube.

### `FRC-UI-001` — Unemployment-insurance claimant public-output release, disclosure-limitation, method-integrity, and no-output-by-release control

Status: `not_released_disclosure_review_required_no_public_outcome`

Execution control: `FEC-UI-001`  
Authorization gate: `FWAG-UI-001`  
Field-intake control: `FIC-UI-001`  
Sampling gate: `TSG-UI-001`  
Outcome-tail plan: `OTP-UI-001`

Closure blocker: Blocks closure because a disclosure-reviewed UI public output would still need outcome-tail evidence, source preservation, steward approval, and material-distribution interpretation; release review alone is not payment, waiver, appeal, debt, or hardship proof.

| Release family | Items |
| --- | --- |
| Required release artifacts | disclosure-review memo held outside the cube; public-output locator and version stamp if a release later exists; small-cell and rare-cohort review status; suppression, aggregation, rounding, perturbation, noise, synthetic, or formal privacy method note where applicable; nonresponse, denominator, excluded-cohort, follow-up-window, and unresolved-harm statement; public-narrative and quote-permission review status; errata, withdrawal, and retraction route |
| Disclosure limitation | apply disclosure limitation before public release, including suppression or aggregation for small-cell and rare-cohort UI claimant outputs; check complementary disclosure risk where totals or subtotals could reveal a suppressed claimant cohort; document whether rounding, perturbation, noise infusion, synthetic output, or formal privacy methods change interpretation; do not publish cells or combinations that identify an individual, household, employer, office worker, local office, or rare claimant trajectory |
| De-identification | de-identification is treated as risk reduction, not elimination; review re-identification risk from linkage, geography, rare benefit path, employer context, time sequence, and narrative detail; do not call an output anonymous merely because direct identifiers were removed; publish de-identification limits and residual risk where public conclusions rely on suppressed or transformed data |
| Public narrative | no claimant quote, local office detail, adjudicator detail, employer detail, chronology, or rare-cohort vignette without permission and re-identification review; narrative examples must not reveal claim number, employer, location, disability, domestic safety, immigration-risk, fraud-control status, or unique payment/debt path; aggregate successful cases separately from unresolved hardship, refusal, withdrawal, unreachable, and nonresponse cases; avoid converting compelling anecdotes into denominator claims |
| Quality/integrity | publish method, nonresponse, denominator exclusions, weighting or no-weighting choice, follow-up window, and uncertainty with any finding; separate process metrics from outcome metrics and label both clearly; state which cohorts were suppressed, excluded, or too sparse for public release; pre-register or version the release claims so later edits are visible |
| Participant/community harm review | harm review considers benefit, fraud-control, employer, domestic safety, disability, immigration, and retaliation risks before release; participant-facing or advocate review may be required for quotes or sensitive narrative claims; release does not imply participant endorsement or service improvement; community or claimant feedback is logged as review status only, not raw private narrative |
| Errata/retraction | errata route corrects method, denominator, suppression, nonresponse, or interpretation errors; withdraw or retract output when disclosure risk, re-identification risk, participant harm, source drift, or analytic error defeats safe reliance; notify owner, privacy/security, data custodian, and affected partner when output changes alter risk or interpretation; archive records public-safe correction status and not raw error details |
| Allowed cube artifacts | public-output title and locator if released; version stamp and release status; aggregate-safe method limits; suppression/disclosure review status without reviewer workpapers; public-safe errata status |
| Prohibited public outputs | name; address; claim_number; case_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; employer_name; local_office_detail; incident_report_detail; breach_detail; audit_log; secure_environment_raw_output; reviewer_workpaper; small_cell; rare_cohort_narrative |
| Pause/stop conditions | disclosure review unresolved; suppression or complementary suppression unresolved; small-cell or rare-cohort risk unresolved; re-identification risk unresolved; withdrawal or quote permission unresolved; PII breach or incident review unresolved; audit-log or retention authority failure unresolved; errata, withdrawal, or retraction trigger present; method or nonresponse limit missing from release |

Next action: Draft a public-output checklist and errata template for any future UI claimant pilot; keep it non-releasing until an owner-approved project exists outside the cube.


## Privacy posture

Raw private records, identifiers, linkage keys, audit logs, incident details, breach details, reviewer workpapers, and secure-environment raw outputs stay outside the cube. The archive may store only public-safe release status, method limits, and locator-level public receipts.
