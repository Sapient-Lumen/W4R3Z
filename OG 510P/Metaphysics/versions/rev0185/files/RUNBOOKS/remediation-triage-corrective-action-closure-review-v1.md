# Remediation triage, corrective action, and closure review runbook v1

## Scope

This runbook is local to rev0175. It applies when a signal appears through validation, query regression, reference integrity, claim/evidence review, release gates, attestation-boundary checks, observability, feedback, reliance, drift, audit sampling, or exercise drills.

## Steps

1. Identify the signal source and record the source artifact.
2. Assign a severity class from `SEVERITY_CLASSIFICATION_MATRIX.yml`.
3. Apply the local objective from `SERVICE_OBJECTIVE_LEDGER.yml` without representing it as a public SLA.
4. Record corrective action in `CORRECTIVE_ACTION_REGISTER.yml`.
5. Use `COMMUNICATION_ESCALATION_LEDGER.yml` only for local escalation unless a future public-duty gate is explicitly added.
6. Close through `CLOSURE_VERIFICATION_LEDGER.yml` only when evidence artifacts resolve and residual debt is stated.
7. Run `tools/check_remediation_closure.py`, `tools/run_query_regression.py`, and `tools/validate_archive.py`.

## Boundary

This runbook does not create public incident response, emergency remediation, customer support, regulatory reporting, legal notice, or external maintainer duties.
