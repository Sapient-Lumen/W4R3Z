# Fieldwork authorization gates

Generated for `rev0799` from `metadata/fieldwork_authorization_gates.json`.

Non-closing owner and custodian authorization gates that sit after field-intake controls and before any claimant/household contact, administrative-data linkage, private-record access, or secure-environment output. They convert research intent into named approvals, custody limits, disclosure review, and stop conditions without collecting private data in the cube.

## Closure policy

A fieldwork authorization gate is authorization readiness, not authorization, fieldwork, source preservation, or outcome proof. No live gap can close from an authorization gate, checklist, meeting note, or data-access request alone.

## Summary counts

| Metric | Count |
| --- | ---: |
| Authorization gates | 2 |
| Gap blockers | 4 |
| Linked field-intake controls | 2 |

## Authorization status counts

| Status | Count |
| --- | ---: |
| `not_authorized_pre_handoff_controls_only` | 2 |

## Gap blockers

| Gap | Authorization gates |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `FWAG-HC-001`, `FWAG-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `FWAG-HC-001`, `FWAG-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `FWAG-HC-001`, `FWAG-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `FWAG-HC-001`, `FWAG-UI-001` |

## Gate details

### `FWAG-HC-001` — Housing household fieldwork authorization and custody handoff gate

Status: `not_authorized_pre_handoff_controls_only`

Field-intake control: `FIC-HC-001`  
Sampling gate: `TSG-HC-001`  
Outcome-tail plan: `OTP-HC-001`

Handoff boundary: No household contact roster, docket linkage, provider record, shelter record, screening record, or secure-environment output may enter the cube. Only redacted authorization status, aggregate-safe metrics, and disclosure-reviewed findings may be referenced later.

Closure blocker: Blocks field validation and material-outcome closure until owner-approved authorization, secure custody, safety/disclosure review, and aggregate-safe output exist outside the cube; this gate is not collection or proof.

| Authorization family | Items |
| --- | --- |
| Required authorizers | housing program or legal-services owner for evaluation question; legal/privacy officer for court, provider, shelter, and assistance-record use; human-subjects or ethics reviewer for household contact and safety posture; data custodian for court docket, representation, assistance, shelter, and screening records; security/privacy control owner for secure environment and audit posture; tenant or community advocate for retaliation and safety review |
| Authorization artifacts | signed owner scope memo; legal/privacy and court-record use determination; human-subjects or non-research determination record; partner data-use agreement decision; SORN/routine-use/matching or equivalent disclosure analysis if applicable; minimum-necessary household outcome data dictionary; secure-environment control selection and audit plan; disclosure-review and small-cell/geography suppression plan; revocation and safety stop rule |
| Custody handoff controls | cube stores only redacted authorization status and aggregate-safe protocol metadata; all identifiers, linkage keys, and private records remain outside the cube; provider/court/community partner holds identifiers and linkage keys; contact roster separated from household outcome extract; secure environment approved before extract; audit logs reviewed by custodian, not archive maintainer alone; outputs leave secure environment only after disclosure and safety review |
| Minimum necessary fields | representation status; case disposition category; rental assistance or arrears cure state; possession/shelter/re-housing state; screening or debt tail; safety/retaliation flag reduced to aggregate-safe category |
| Prohibited cube artifacts | name; address; docket_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; shelter_location; partner_case_record; secure_environment_export_before_disclosure_review |
| Stop conditions | no owner authorization; unclear human-subjects/legal/privacy route; participant refusal might affect representation, shelter, assistance, or services; landlord or adverse-party recruitment proposed; linkage key or contact roster proposed for cube storage; court/provider/shelter data-sharing route unresolved; secure environment absent; disclosure or safety review rejects output; incident or complaint indicates harm risk |

Next action: Owner must nominate responsible authorizers and create a redacted authorization packet template before any housing field-tail pilot.

### `FWAG-UI-001` — Unemployment insurance claimant fieldwork authorization and custody handoff gate

Status: `not_authorized_pre_handoff_controls_only`

Field-intake control: `FIC-UI-001`  
Sampling gate: `TSG-UI-001`  
Outcome-tail plan: `OTP-UI-001`

Handoff boundary: No UI claimant contact, administrative-record linkage, payment/debt/appeal extract, or secure-environment output may enter the cube. Only redacted authorization status, aggregate-safe metrics, and disclosure-reviewed findings may be referenced later.

Closure blocker: Blocks field validation and material-outcome closure until owner-approved authorization, secure custody, disclosure review, and aggregate-safe output exist outside the cube; this gate is not collection or proof.

| Authorization family | Items |
| --- | --- |
| Required authorizers | program owner for UI evaluation question; legal/privacy officer for Privacy Act, PRA, records, and data-sharing route; human-subjects or ethics reviewer for research/service-improvement determination; data custodian for claim, issue, payment, debt, waiver, and appeal records; security/privacy control owner for secure environment and audit posture; participant advocate or claimant-assistance partner for adverse-action firewall |
| Authorization artifacts | signed owner scope memo; legal/privacy determination or issue log; human-subjects or non-research determination record; data-sharing or data-use agreement decision; SORN/routine-use/computer-matching analysis if applicable; minimum-necessary data dictionary; secure-environment control selection and audit plan; disclosure-review and small-cell suppression plan; revocation and incident stop rule |
| Custody handoff controls | cube stores only redacted authorization status and aggregate-safe protocol metadata; all identifiers, linkage keys, and private records remain outside the cube; program or statistical partner holds identifiers and linkage keys; contact roster separated from outcome extract; secure environment approved before extract; audit logs reviewed by custodian, not archive maintainer alone; outputs leave secure environment only after disclosure review |
| Minimum necessary fields | claim status and issue state; payment timing and amount category; hold/cure dates; overpayment/debt/waiver/appeal state; staff-assistance route; cohort and burden fields stripped of direct identifiers |
| Prohibited cube artifacts | name; address; ssn; claim_number; contact_roster; linkage_key; raw_transcript; raw_audio; raw_video; private_screenshot; partner_case_record; secure_environment_export_before_disclosure_review |
| Stop conditions | no owner authorization; unclear human-subjects/legal/privacy route; participant refusal might affect benefits or enforcement; linkage key or contact roster proposed for cube storage; data-sharing or matching analysis unresolved; secure environment absent; disclosure review rejects output; incident or complaint indicates harm risk |

Next action: Owner must nominate responsible authorizers and create a redacted authorization packet template before any UI field-tail pilot.


## Privacy posture

This file may store gate status, role checklists, public source receipts, redacted decision receipts, and aggregate-safe protocol metadata. It must not store names, addresses, claim numbers, docket numbers, contact rosters, linkage keys, raw transcripts, private records, private screenshots, secure-environment outputs before disclosure review, or partner-held reidentification keys.
