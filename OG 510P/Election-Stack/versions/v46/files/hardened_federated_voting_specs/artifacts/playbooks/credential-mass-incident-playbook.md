# Credential mass-incident playbook (theft / malware / rapid reissuance)

Use this playbook when credential compromise impacts many voters or critical roles.

## Actions
- Activate:
  - `CHECK:artifacts/checklists/credential-recovery-checklist.md`
  - `CHECK:artifacts/checklists/credential-lifecycle-and-recovery.md` (if applicable)
  - `CHECK:artifacts/checklists/mass-compromise-response-checklist.md`
- Publish a `SCHEMA:schemas/CredentialLifecycleEvent.json` series for:
  - suspensions, revocations, and reissuance rules

## Evidence obligations
- Publish aggregate metrics (no PII) about incident scope.
- Publish policy decisions that affect eligibility/reissuance.

## Follow-up
- Run a “post-incident audit”: `TEMPLATE:artifacts/templates/after-action-report.md`
