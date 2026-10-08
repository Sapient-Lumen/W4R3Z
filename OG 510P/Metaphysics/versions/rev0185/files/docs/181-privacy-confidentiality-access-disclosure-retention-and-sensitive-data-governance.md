# 181. Privacy, Confidentiality, Access, Disclosure, Retention, and Sensitive-Data Governance

## Function of this file

Rev0174 made contestability, dissent, harm review, redress, and stakeholder challenge harder to launder. This file adds the next layer: **a challenge surface can create sensitive records even when the archive has no public complaint service**. Feedback, contestations, harm allegations, review notes, custody rows, and release packets can accidentally collect identifiers, expose confidential material, imply consent, or preserve sensitive information longer than the local purpose warrants.

The operative warning is:

> Contestability is not consent. Intake is not a data-rights service. A local access row is not confidentiality assurance. A disclosure review is not legal publication approval. A retention row is not a statutory schedule. A privacy-risk note is not GDPR, ISO, or NIST compliance.

## Why this layer is needed

The archive now has increasingly operational ledgers: feedback, reliance, remediation, accountability, appeals, dissent, harm review, and redress. Those ledgers are useful, but they create a new failure mode: **governance records can become their own sensitive dataset**. A future maintainer could include names, emails, institutional affiliations, private allegations, credentials, unreleased drafts, or legal assertions simply because a ledger has a slot for evidence.

Rev0175 therefore adds six local surfaces:

- `PRIVACY_MINIMIZATION_POLICY.yml`
- `CONFIDENTIALITY_ACCESS_MATRIX.yml`
- `DISCLOSURE_PUBLICATION_REVIEW.yml`
- `RETENTION_DELETION_LEDGER.yml`
- `SENSITIVE_DATA_CLASSIFICATION.yml`
- `PRIVACY_RISK_REVIEW_LEDGER.yml`

and one executable checker:

- `tools/check_privacy_confidentiality.py`

The checker produces these reports:

- `REGISTERS/privacy-minimization-report-rev0175.yml`
- `REGISTERS/confidentiality-access-report-rev0175.yml`
- `REGISTERS/disclosure-publication-report-rev0175.yml`
- `REGISTERS/retention-deletion-report-rev0175.yml`
- `REGISTERS/sensitive-data-classification-report-rev0175.yml`
- `REGISTERS/privacy-risk-review-report-rev0175.yml`

## Control rule

A governance row may not collect or expose sensitive information merely because the package has a place to record feedback, contestation, harm, remediation, role assignment, evidence custody, or redress. Sensitive or identifying details must be minimized, access-bounded, publication-reviewed, retention-bounded, classified, and privacy-risk-reviewed before they are repeated in current-release language.

## Local limitation

Rev0175 creates local archive hygiene, not a privacy management system. It does not claim legal data-controller status, data-subject request service, GDPR compliance, ISO/IEC 27701 conformance, NIST Privacy Framework implementation, confidentiality guarantee, access-control system, automated deletion, breach-response service, or external privacy review.

## Allowed and forbidden language

Allowed:

- "Rev0175 adds local minimization, confidentiality/access, disclosure, retention, sensitive-data classification, and privacy-risk-review checks."
- "The archive declares that public complaint, legal data-rights, and confidentiality-guarantee services are absent."
- "The checker verifies local references, classification links, role links, retention rows, and privacy-risk boundaries."

Forbidden:

- "The archive is GDPR compliant."
- "The archive has ISO/IEC 27701 certification or conformance."
- "The archive implements the NIST Privacy Framework."
- "The archive provides a data-subject request service."
- "The archive guarantees confidentiality."
- "The archive operates access control, automated deletion, or breach notification."

## Release gate

Rev0175 adds `GATE-0175-013`, which blocks privacy/confidentiality/access/retention claims unless the six new artifacts, checker, current records, and reports are present and locally checked.
