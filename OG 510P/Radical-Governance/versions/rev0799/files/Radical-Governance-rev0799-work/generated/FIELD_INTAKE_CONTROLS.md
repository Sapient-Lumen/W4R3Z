# Field-intake controls

Generated for `rev0799` from `metadata/field_intake_controls.json`.

Pre-collection controls that must pass before UI claimant or housing household outcome-tail fieldwork can start. These controls convert sampling gates into lawful-basis, consent/waiver, privacy, linkage, adverse-action, and publication safeguards without collecting private data in the cube.

## Closure policy

A field-intake control is a pre-collection safety gate, not fieldwork and not proof. It cannot close affected-person, source-preservation, stewardship, or material-outcome gaps. It blocks fieldwork until owner-approved legal/ethics/privacy authority and data-linkage safeguards exist outside the cube.

## Summary counts

| Metric | Count |
| --- | ---: |
| Controls | 2 |
| Gap blockers | 4 |
| Linked sampling gates | 2 |

## Status counts

| Status | Count |
| --- | ---: |
| `pre_collection_controls_required_not_collected` | 2 |

## Gap blockers

| Gap | Field-intake controls |
| --- | --- |
| `GAP-029-affected-person-outcome-validation` | `FIC-HC-001`, `FIC-UI-001` |
| `GAP-031-source-evidence-preservation-and-claim-capture` | `FIC-HC-001`, `FIC-UI-001` |
| `GAP-032-license-maintainer-contribution-governance` | `FIC-HC-001`, `FIC-UI-001` |
| `GAP-033-power-distribution-and-material-outcome-theory` | `FIC-HC-001`, `FIC-UI-001` |

## Controls

### `FIC-HC-001` — Housing household field-intake and displacement-linkage firewall

Status: `pre_collection_controls_required_not_collected`

Linked sampling gate: `TSG-HC-001`

Human-subjects boundary: Treat household interviews, hotline/community referrals, shelter or re-housing follow-up, court/provider record linkage, screening-aftereffect follow-up, and any identifiable or linkable housing records as requiring owner-approved human-subjects/legal/ethics screening before use.

Closure blocker: This housing control blocks fieldwork and gap closure until legal/ethics/privacy authority, partner-held key custody, consent/waiver posture, adverse-action firewall, safety plan, and publication controls exist outside the cube. Passing the control would still be design readiness, not household outcome proof.

| Control family | Items |
| --- | --- |
| Lawful basis floor | owner-approved evaluation question; documented human-subjects determination or non-research/service-improvement determination; documented consent, waiver, exemption, or lawful-basis route; provider/court/community partner agreement before linkage; public-benefit/service-program research route not self-certified by archive maintainer |
| Consent/notice floor | plain-language purpose and expected duration; voluntary participation with no effect on services, representation, rental assistance, shelter, or court posture; confidentiality and mandated-disclosure limits; contacts for questions, rights, complaints, and service referrals; future-use statement for de-identified or non-used data; withdrawal path that does not disrupt services or representation |
| Data-linkage controls | partner-held identifiers only; linkage key never enters cube; separate contact roster from court/provider/shelter/rental-assistance extracts; minimum necessary fields for possession, displacement, debt, re-housing, screening, and durable stability; no reidentification by cube maintainer; retention and destruction schedule outside cube |
| Adverse-action firewall | participation refusal cannot affect representation, shelter, rental assistance, court support, or service access; field researcher cannot be landlord, opposing counsel, eligibility worker, or adjudicator; safety plan exists for retaliation, lockout, domestic violence, or immigration-risk disclosures |
| Prohibited cube artifacts | name; address; docket_number; case_number; phone_number; email; shelter_location; immigration_status; private_screenshot; raw_audio; raw_video; contact_roster; linkage_key; partner_case_record |

Next action: Draft an owner-approved housing field-intake protocol, safety plan, and data-linkage firewall memo before any household contact or partner record linkage.

### `FIC-UI-001` — Unemployment insurance claimant field-intake and linkage firewall

Status: `pre_collection_controls_required_not_collected`

Linked sampling gate: `TSG-UI-001`

Human-subjects boundary: Treat direct claimant contact, observation, interviews, surveys, follow-up calls, and any identifiable or linkable private claimant records as requiring owner-approved human-subjects/legal/ethics screening before use.

Closure blocker: This UI control blocks fieldwork and gap closure until legal/ethics/privacy authority, partner-held key custody, consent/waiver posture, adverse-action firewall, and publication controls exist outside the cube. Passing the control would still be design readiness, not field validation.

| Control family | Items |
| --- | --- |
| Lawful basis floor | owner-approved evaluation question; documented human-subjects determination or non-research/service-improvement determination; documented consent, waiver, exemption, or lawful-basis route; data-sharing or partner agreement before linkage; public-benefit/service-program research route not self-certified by archive maintainer |
| Consent/notice floor | plain-language purpose and expected duration; voluntary participation with no effect on benefit entitlement or claim handling; confidentiality and limits of confidentiality; contacts for questions, rights, and complaints; future-use statement for de-identified or non-used data; withdrawal path that does not disrupt benefits |
| Data-linkage controls | partner-held identifiers only; linkage key never enters cube; separate contact roster from outcome extract; minimum necessary fields for payment, hold, debt, waiver, appeal, and hardship tail; no reidentification by cube maintainer; retention and destruction schedule outside cube |
| Adverse-action firewall | participation refusal cannot reduce benefits, delay claim handling, trigger fraud review, affect waiver or appeal, or alter debt collection posture; field researcher cannot be the adjudicator or debt collector; complaint/escalation route exists if participant reports retaliation or benefit interference |
| Prohibited cube artifacts | name; address; ssn; claim_number; phone_number; email; bank_account; login_credentials; private_screenshot; raw_audio; raw_video; contact_roster; linkage_key; partner_case_record |

Next action: Draft an owner-approved UI field-intake protocol and data-linkage firewall memo before any claimant contact or partner record linkage.


## Privacy posture

The cube may store control status, source receipts, cohort mappings, aggregate-safe protocol metadata, and redacted decision receipts. It must not store names, addresses, claim numbers, docket numbers, account identifiers, contact lists, raw recordings, private records, private screenshots, linkage keys, or partner-held reidentification keys.
