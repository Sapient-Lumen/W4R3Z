# Privacy, Confidentiality, Access, Disclosure, Retention, and Sensitive-Data Review Runbook v1

1. Identify the governance surface that may contain sensitive, identifying, confidential, or stakeholder-submitted material.
2. Assign or confirm a sensitive-data classification in `SENSITIVE_DATA_CLASSIFICATION.yml`.
3. Apply `PRIVACY_MINIMIZATION_POLICY.yml`: record the issue, affected artifact, and route; avoid personal identifiers, credentials, secrets, legal claims, health/safety details, and unnecessary affiliations.
4. Check `CONFIDENTIALITY_ACCESS_MATRIX.yml`: local access rows are boundaries, not a confidentiality guarantee or access-control system.
5. Check `DISCLOSURE_PUBLICATION_REVIEW.yml`: publication of a package artifact is not legal publication approval or privacy clearance.
6. Check `RETENTION_DELETION_LEDGER.yml`: local review triggers are not statutory retention schedules or automated deletion.
7. Check `PRIVACY_RISK_REVIEW_LEDGER.yml`: privacy-risk review is local archive hygiene only, not GDPR, ISO/IEC 27701, NIST Privacy Framework, breach-response, or data-subject-rights service.
8. Run `tools/check_privacy_confidentiality.py` and regenerate the six current reports.
9. Update the release gate, cube, query suite, reference map, fixture corpus, manifest, and validation transcript.

Forbidden upgrade language: compliance, certification, legal privacy review, confidentiality guarantee, public data-rights channel, automated deletion, breach notification, or external privacy authority.
