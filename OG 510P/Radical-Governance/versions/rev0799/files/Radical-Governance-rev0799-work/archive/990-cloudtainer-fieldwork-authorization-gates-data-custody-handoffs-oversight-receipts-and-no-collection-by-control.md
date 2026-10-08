# 990 — Cloudtainer fieldwork authorization gates, data-custody handoffs, oversight receipts, and no collection by control

## One-line thesis

Rev0791 made field-intake controls safe enough to name a possible UI or housing tail, but intake controls still do not name who may authorize contact, who may hold linkage keys, where private records may live, or when outputs may leave a secure environment; rev0792 adds fieldwork authorization gates so collection cannot begin merely because the cube has a design, consent floor, or control checklist.

## Why this matters

The riskiest remaining failure is a subtle one: the archive can become more dangerous exactly as it becomes more practical. A future maintainer may see outcome-tail plans, sampling gates, and field-intake controls and infer that the hard part is done. It is not done. The hard part is the owner-approved handoff between public doctrine and private evidence.

Unemployment-insurance claimant evidence can involve eligibility states, benefit payments, identity holds, debts, waivers, appeals, fraud-control flags, hardship narratives, and administrative records about living people. Housing household evidence can involve court records, representation, arrears, assistance, shelter, re-housing, screening, lockout risk, retaliation risk, domestic safety, immigration sensitivity, and household narratives. These are not archive inputs. They are private operational evidence that only authorized owners, partners, custodians, or secure environments may hold.

The new `metadata/fieldwork_authorization_gates.json` sits after `metadata/field_intake_controls.json`. It is a pre-handoff authorization layer. It says that the archive may store only redacted status and aggregate-safe protocol metadata, while the private evidence path must be approved, held, audited, and disclosure-reviewed outside the cube.

The governing rule is **no collection by control**.

## Pattern pack

1. **A control checklist is not approval.** Field-intake controls can block unsafe work; they cannot authorize contact, record access, matching, linkage, disclosure, or publication.
2. **A data handoff needs named authorizers.** Program owner, legal/privacy reviewer, ethics or human-subjects reviewer, data custodian, security/privacy control owner, and participant/community advocate roles must be named before fieldwork.
3. **Custody is a constitutional fact.** The same field result means different things depending on whether identifiers, linkage keys, and private records are held by the cube, a program office, a statistical unit, a legal-aid partner, a court, or a secure environment.
4. **Minimum necessary is not a slogan.** Claim, payment, debt, waiver, appeal, possession, shelter, re-housing, and screening fields must be listed before extraction, and direct identifiers must be excluded from the cube.
5. **Disclosure review comes before reader value.** A vivid hardship quote, rare cohort, building, provider, shelter, geography, or staff fact may be more harmful than useful if it can reidentify someone.
6. **Administrative-data reuse requires law and stewardship.** Evaluation need does not override Privacy Act, matching, PRA, records, consent, confidentiality, statistical-access, or data-sharing constraints.
7. **Stop conditions must defeat momentum.** If owner authority, legal/privacy route, secure environment, linkage custody, refusal safety, or disclosure review is unresolved, no result is accepted.
8. **The cube records the boundary, not the private life.** It can say what was authorized, blocked, or aggregate-safe; it must not become the claimant or household dossier.

## What changed

### Fieldwork authorization gates

Rev0792 adds two non-closing gates.

`FWAG-UI-001` covers unemployment-insurance claimant fieldwork. It requires a signed owner scope memo, legal/privacy route, human-subjects or non-research determination, data-sharing or data-use decision, SORN/routine-use/computer-matching analysis where applicable, secure-environment controls, disclosure review, revocation path, and participant/claimant advocate review before any claimant contact or administrative-record linkage.

`FWAG-HC-001` covers housing household fieldwork. It requires a housing/legal-services owner, legal/privacy and court-record use determination, human-subjects or non-research determination, partner data-use decision, safe recruitment posture, no-landlord/adverse-party route, secure-environment controls, disclosure and safety review, and revocation path before any household contact or court/provider/shelter/screening-record linkage.

Both gates link to the relevant field-intake controls, sampling gates, and outcome-tail plans. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither can close them.

### Custody handoff

The new gates define the custody boundary: identifiers, linkage keys, contact rosters, private records, raw recordings, screenshots, partner case records, and pre-review secure-environment outputs stay outside the cube. The cube may later store redacted authorization status, aggregate-safe metrics, disclosure-reviewed findings, and non-identifying protocol metadata.

That distinction matters because the cube is a public governance archive, not a research data enclave, benefits system, case-management platform, court repository, shelter database, or secure statistical environment. If the cube ever starts holding the private records, it has changed constitutional character.

### Authorization receipts

Rev0792 adds locator-level source receipts for OMB A-108, OMB M-14-06, OMB M-01-05, CIPSEA/statistical data access resources, the Standard Application Process / secure-environment model, and NIST SP 800-53 Rev. 5. These receipts do not authorize anything. They force specific review questions: Is this a system of records? Is a routine use needed? Is a matching analysis needed? Is administrative-data reuse lawful? Is the statistical or evidence-building confidentiality route actually available? Who is an approved user? What secure environment and controls apply?

### Audit/refactor

The bounded refactor is twofold. First, `FIELDWORK_AUTHORIZATION_GATES` is built through the existing generated-surface helper, extending the shared surface pattern instead of adding another bespoke renderer. Second, the Makefile dependency chain now includes `tail_sampling_gates`, `field_intake_controls`, and `fieldwork_authorization_gates` as explicit targets before common test matrices. That corrects a risky drift where `build_all.py` had the complete order but individual make targets could lag behind newer fieldwork surfaces.

This is not a doctrine expansion. It is an operational guard: the current highest-risk path now has to clear owner authorization, custody, disclosure, and stop-rule gates before any future maintainer can claim fieldwork is ready.

## What this still does not do

It does not approve fieldwork.

It does not name actual human participants.

It does not create a consent form, IRB approval, non-research determination, Privacy Act determination, data-sharing agreement, matching agreement, secure environment, system authorization, statistical access approval, or disclosure review.

It does not collect claim records, court records, provider records, shelter records, screening records, hardship narratives, raw recordings, screenshots, transcripts, addresses, contact rosters, linkage keys, or secure-environment outputs.

It does not prove payment, waiver, debt relief, appeal success, possession retention, shelter exit, re-housing, screening correction, or durable stability.

It does not close any live gap.

## Anti-theater tests

1. Pick `FWAG-UI-001`. Does it require program-owner, legal/privacy, ethics/human-subjects, data-custodian, security/privacy, and claimant-advocate review before collection?
2. Pick `FWAG-HC-001`. Does it require safety review and forbid landlord or adverse-party recruitment paths?
3. Pick either gate. Does it prohibit linkage keys, contact rosters, names, addresses, private screenshots, raw recordings, and partner case records from entering the cube?
4. Pick either gate. Does it require disclosure review before any secure-environment output becomes a public reader surface?
5. Pick an OMB, NIST, CIPSEA, or SAP receipt. Is it only a locator and review trigger, not collection authority?
6. Pick `generated/FIELDWORK_AUTHORIZATION_GATES.md`. Does it show `not_authorized` status rather than fieldwork results?
7. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the new authorization surface?
8. Run `make fieldwork_authorization_gates`. Does the individual target build the prerequisites in order rather than relying only on `build_all.py`?

## Source posture

Use OMB A-108 as a SORN, routine-use, matching-notice, and records-system review trigger, not as a fieldwork permission slip. Use OMB M-14-06 and M-01-05 as administrative-data and personal-data-sharing caution surfaces, not as approvals for linkage. Use CIPSEA and Standard Application Process resources to distinguish approved confidential-data access and secure environments from ordinary archive custody. Use NIST SP 800-53 Rev. 5 to require security/privacy control selection and audit posture, not to certify any system as adequate.

The practical rule is: **the cube can maintain the authorization boundary, but it must not become the authorization, the secure environment, or the private evidence store.**
