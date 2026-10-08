# Fieldwork execution controls

Generated for `rev0799` from `metadata/fieldwork_execution_controls.json`.

Post-authorization but pre-result operating controls for any future UI claimant or housing household field-tail pilot. These controls describe how approved fieldwork would be logged, paused, corrected, reviewed, retained, and disclosure-cleared outside the cube; they do not authorize, collect, store, or validate private evidence.

## Closure policy

A fieldwork execution control is not execution, outcome proof, source preservation, or closure. Operating logs, incident clocks, audit reviews, or retention memos cannot close live gaps unless paired later with authorized, privacy-bounded, disclosure-reviewed claimant or household outcome evidence and preserved claim receipts.

## Summary counts

| Metric | Count |
| --- | ---: |
| Execution controls | 2 |
| Gap blockers | 4 |
| Authorization gates linked | 2 |

## Execution status counts

| Status | Count |
| --- | ---: |
| `not_executed_authorization_required_no_fieldwork` | 2 |

## Gap blockers

| Gap | Execution controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `FEC-HC-001`, `FEC-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `FEC-HC-001`, `FEC-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `FEC-HC-001`, `FEC-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `FEC-HC-001`, `FEC-UI-001` |

## Control details

### `FEC-HC-001` — Housing household fieldwork execution ledger, pause, incident, retention, and publication control

Status: `not_executed_authorization_required_no_fieldwork`

Authorization gate: `FWAG-HC-001`  
Field-intake control: `FIC-HC-001`  
Sampling gate: `TSG-HC-001`  
Outcome-tail plan: `OTP-HC-001`

Closure blocker: Blocks affected-person and material-outcome closure until authorized fieldwork is actually executed outside the cube, incidents and withdrawals are handled, retention/disclosure controls pass, and aggregate-safe or de-identified outcome evidence is reviewed without private data entering the archive.

| Execution family | Items |
| --- | --- |
| Required artifacts | signed authorization release before first contact; date-bounded fieldwork start/stop register; authorized recruitment-channel ledger with aggregate-safe counts only; consent/refusal/withdrawal event register held outside cube; incident and unanticipated-problem triage register held outside cube; PII breach pause and response contact tree; audit-log review and audit-failure escalation memo; retention/disposition and litigation-hold check; disclosure and safety review before any public output |
| Operating log floor | log approved fieldwork window, operator role, approved channel, and aggregate contact-attempt counts; log cohort cell, refusal, withdrawal, and unreachable status only as aggregate-safe counts in the cube; log protocol deviations and corrective-action status outside the cube with only redacted status available to the archive; log disclosure-review outcome before any quote, geography, provider, shelter, building, or rare-cohort statement is published |
| Participant safety | refusal and withdrawal cannot affect representation, shelter, rental assistance, court posture, or service access; participant can pause or withdraw without explaining and without adverse action; retaliation, lockout, domestic safety, immigration-risk, or landlord/adverse-party exposure triggers immediate pause and safety review; field staff may not request unnecessary narrative detail when aggregate status is enough |
| Incident response | triage adverse events, unanticipated problems, protocol deviations, and serious or continuing noncompliance outside the cube; promptly notify owner, ethics/human-subjects reviewer, legal/privacy reviewer, and custodian when reporting thresholds may be met; record initial, follow-up, and corrective-action status without placing private event details in the cube; pause publication and further contact until required incident review is resolved |
| Breach response | suspected PII breach pauses contact, linkage, extraction, and publication; owner, privacy, security, and custodian run risk-of-harm and notification analysis outside the cube; secure logs and evidence are preserved outside the cube for investigation; cube stores only redacted breach-response status and no private facts |
| Audit controls | audit logs exist for authorized access, extract creation, linkage key use, secure-environment query, and output review; audit log failure pauses fieldwork and output release; audit logs are reviewed by custodian/security, not archive maintainer alone; audit evidence remains outside the cube except aggregate-safe status |
| Retention/destruction | no destruction without approved records schedule, disposition authority, and litigation-hold clearance; temporary records are destroyed only by authorized custodian outside the cube; permanent or hold-subject records are not culled into the cube; retention exceptions and destruction attestations are recorded outside the cube with redacted status only |
| Publication release | no public output before disclosure, safety, and small-cell review; no quote or narrative detail without permission, de-identification, and reidentification review; no building, landlord, shelter, provider, docket, household, or address-level detail when reidentification risk remains; publish uncertainty, nonresponse, excluded cohorts, and unresolved harm separately from successful cases |
| Prohibited cube artifacts | name; address; docket_number; case_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; shelter_location; partner_case_record; incident_report_detail; breach_detail; audit_log; secure_environment_raw_output |
| Pause/stop conditions | missing or expired owner authorization; privacy/legal route unresolved; ethics or human-subjects concern unresolved; withdrawal or refusal not honored; possible adverse action or retaliation risk; unanticipated problem or incident threshold may be met; PII breach suspected; audit log failure or missing audit trail; linkage key exposure or custodian boundary failure; retention/destruction authority unclear; disclosure review unresolved |

Next action: Create a redacted execution-log template and pause/incident clock before any housing household pilot is proposed to an owner or partner.

### `FEC-UI-001` — Unemployment-insurance claimant fieldwork execution ledger, pause, incident, retention, and publication control

Status: `not_executed_authorization_required_no_fieldwork`

Authorization gate: `FWAG-UI-001`  
Field-intake control: `FIC-UI-001`  
Sampling gate: `TSG-UI-001`  
Outcome-tail plan: `OTP-UI-001`

Closure blocker: Blocks affected-person and material-outcome closure until authorized fieldwork is actually executed outside the cube, incidents and withdrawals are handled, retention/disclosure controls pass, and aggregate-safe or de-identified outcome evidence is reviewed without private data entering the archive.

| Execution family | Items |
| --- | --- |
| Required artifacts | signed authorization release before first claimant contact; date-bounded fieldwork start/stop register; approved recruitment-channel ledger with aggregate-safe counts only; consent/refusal/withdrawal event register held outside cube; incident and unanticipated-problem triage register held outside cube; PII breach pause and response contact tree; audit-log review and audit-failure escalation memo; retention/disposition and litigation-hold check; disclosure review before any public output |
| Operating log floor | log approved fieldwork window, operator role, approved channel, and aggregate contact-attempt counts; log cohort cell, refusal, withdrawal, unreachable, and nonresponse state only as aggregate-safe counts in the cube; log benefit, debt, identity-hold, waiver, appeal, and payment-tail deviations outside the cube with only redacted status available to the archive; log disclosure-review outcome before any claimant quote, local office, employer, adjudicator, or rare-cohort statement is published |
| Participant safety | refusal and withdrawal cannot affect benefit claim, adjudication, payment, waiver, appeal, identity review, or fraud-control posture; participant can pause or withdraw without explaining and without adverse action; hardship, domestic safety, immigration-risk, disability-access, or retaliation concern triggers immediate pause and referral-safe review; field staff may not solicit extra hardship narrative when status fields answer the evaluation question |
| Incident response | triage adverse events, unanticipated problems, protocol deviations, and serious or continuing noncompliance outside the cube; promptly notify owner, ethics/human-subjects reviewer, legal/privacy reviewer, and custodian when reporting thresholds may be met; record initial, follow-up, and corrective-action status without placing private event details in the cube; pause publication and further contact until required incident review is resolved |
| Breach response | suspected PII breach pauses contact, linkage, extraction, and publication; owner, privacy, security, and custodian run risk-of-harm and notification analysis outside the cube; secure logs and evidence are preserved outside the cube for investigation; cube stores only redacted breach-response status and no private facts |
| Audit controls | audit logs exist for authorized access, extract creation, linkage key use, secure-environment query, and output review; audit log failure pauses fieldwork and output release; audit logs are reviewed by custodian/security, not archive maintainer alone; audit evidence remains outside the cube except aggregate-safe status |
| Retention/destruction | no destruction without approved records schedule, disposition authority, and litigation-hold clearance; temporary records are destroyed only by authorized custodian outside the cube; permanent or hold-subject records are not culled into the cube; retention exceptions and destruction attestations are recorded outside the cube with redacted status only |
| Publication release | no public output before disclosure, safety, and small-cell review; no quote or narrative detail without permission, de-identification, and reidentification review; no claimant, employer, adjudicator, local-office, case-number, or rare-cohort detail when reidentification risk remains; publish uncertainty, nonresponse, excluded cohorts, and unresolved harm separately from successful cases |
| Prohibited cube artifacts | name; address; claim_number; case_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; employer_name; partner_case_record; incident_report_detail; breach_detail; audit_log; secure_environment_raw_output |
| Pause/stop conditions | missing or expired owner authorization; privacy/legal route unresolved; ethics or human-subjects concern unresolved; withdrawal or refusal not honored; possible adverse action or retaliation risk; unanticipated problem or incident threshold may be met; PII breach suspected; audit log failure or missing audit trail; linkage key exposure or custodian boundary failure; retention/destruction authority unclear; disclosure review unresolved |

Next action: Create a redacted execution-log template and pause/incident clock before any UI claimant pilot is proposed to an owner or partner.


## Privacy posture

The cube may store only redacted control status, aggregate-safe execution metrics, and disclosure-reviewed findings. Contact rosters, identifiers, linkage keys, raw field notes, private records, raw recordings, incident details, breach details, and audit logs stay with authorized owners/custodians outside the cube.
