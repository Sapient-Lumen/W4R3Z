# 180. Contestability, Appeal, Dissent, Harm Review, Redress, and Stakeholder Challenge Governance

## Function of this file

Rev0173 made accountability harder to launder. This file adds the next layer: **accountability is not contestability**. A package can name local roles, assign authority, separate duties, and record approvals while still leaving no disciplined way for a challenged claim, disputed release decision, minority interpretation, harm allegation, or stakeholder objection to be received, routed, preserved, reviewed, reversed, or bounded.

The operative warning is:

> A warning is not a remedy. A role is not an appeal path. A dissent note is not noise. A harm review is not legal adjudication. Local redress is not downstream recall authority. Stakeholder challenge is not public consent.

## Why this layer is needed

The archive now has gates, claims, evidence packets, release decisions, remediation rows, accountability assignments, and approval/consent boundaries. Those controls can still fail by **challenge laundering**:

1. an objection is treated as feedback and never becomes a contestation row;
2. a challenged claim remains releasable because the appeal path is implicit;
3. a minority report is erased by a passing gate;
4. a harm allegation is routed as style feedback rather than impact review;
5. a reversal row is recorded without evidence of what changed;
6. stakeholder standing is either inflated into public consent or denied so broadly that no challenge can be heard;
7. a local correction is described as legal remedy or downstream recall.

Rev0174 therefore adds explicit contestation intake, appeal review, dissent preservation, harm-impact review, redress/reversal, and stakeholder-challenge surfaces.

## New artifacts

Rev0174 introduces six root artifacts:

- `CONTESTATION_INTAKE_LEDGER.yml`
- `APPEAL_REVIEW_POLICY.yml`
- `DISSENT_MINORITY_REPORT_LEDGER.yml`
- `HARM_IMPACT_REVIEW_LEDGER.yml`
- `REDRESS_REVERSAL_LEDGER.yml`
- `STAKEHOLDER_CHALLENGE_REGISTER.yml`

and one executable checker:

- `tools/check_contestability_redress.py`

The checker produces these current reports:

- `REGISTERS/contestation-intake-report-rev0174.yml`
- `REGISTERS/appeal-review-report-rev0174.yml`
- `REGISTERS/dissent-report-rev0174.yml`
- `REGISTERS/harm-impact-report-rev0174.yml`
- `REGISTERS/redress-reversal-report-rev0174.yml`
- `REGISTERS/stakeholder-challenge-report-rev0174.yml`

## Control rule

A disputed claim, release decision, role decision, remediation closure, or public-use warning may not be treated as adequately governed merely because the local package passed validation. Challenge surfaces must remain visible. Appeal and dissent rows must be preserved. Harm-impact rows must be routed to severity and remediation evidence where applicable. Redress/reversal rows must identify the changed artifact, the evidence supporting the change, and the boundary that prevents local correction from being described as legal remedy, public support, downstream recall, or public consent.

## Contestation intake

`CONTESTATION_INTAKE_LEDGER.yml` records challengeable surfaces and local contestations. Rev0174 has one representative local contestation: the risk that public-release warnings could be misread as public consent or downstream authorization. The row is routed to appeal review, claim-language control, accountability review, and public-release attestation boundaries.

## Appeal review

`APPEAL_REVIEW_POLICY.yml` records local appeal paths. It does not create external adjudication, independent board review, legal appeal, user-support obligation, public complaint handling, or regulatory review.

## Dissent and minority reports

`DISSENT_MINORITY_REPORT_LEDGER.yml` preserves a dissent/minority interpretation when a gate passes but residual uncertainty remains. Dissent preservation prevents gate-pass language from erasing unresolved disagreement.

## Harm-impact review

`HARM_IMPACT_REVIEW_LEDGER.yml` records harm hypotheses and their routing to severity, remediation, public-release warnings, and redress. Harm review in this archive is local governance review only. It is not legal review, institutional ethics approval, public impact assessment, medical/safety assessment, or external stakeholder consultation.

## Redress and reversal

`REDRESS_REVERSAL_LEDGER.yml` records local reversal or correction rows. Rev0174 permits local correction of package language and artifacts; it does not claim downstream recall authority, legal remedy, support obligation, compensation, notification duty, or public service operation.

## Stakeholder challenge

`STAKEHOLDER_CHALLENGE_REGISTER.yml` distinguishes stakeholder classes, standing boundaries, and challenge channels. It makes stakeholder challenge legible without converting download, warning visibility, or challenge receipt into consent, approval, public consultation, or external governance.

## Release gate

Rev0174 adds `GATE-0174-012`, which blocks contestability/redress claims unless the six new artifacts, checker, and reports are present and locally checked.

## Allowed and forbidden language

Allowed:

- "Rev0174 includes local contestation, appeal, dissent, harm-review, redress, and stakeholder-challenge ledgers."
- "The contestability/redress checker verifies local references, role links, severity links, and evidence paths."
- "Public consent, legal remedy, external adjudication, downstream recall, and public support remain explicitly unclaimed."

Forbidden:

- "The archive provides a public appeal mechanism."
- "Stakeholders have been consulted or have consented."
- "A local redress row is legal remedy."
- "Dissent has been resolved merely because a gate passed."
- "Harm review proves operational safety or public-use readiness."
- "Local contestability is external adjudication."

## Local limitation

This file creates a stronger local challenge surface, not an institution. It does not create a public helpdesk, independent ombuds function, legal grievance procedure, stakeholder-representation mechanism, right-to-remedy process, or external ethics board.
