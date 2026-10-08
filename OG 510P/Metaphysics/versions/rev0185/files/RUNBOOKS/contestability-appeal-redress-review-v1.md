# Contestability, Appeal, Dissent, Harm Review, Redress, and Stakeholder Challenge Review Runbook v1

## Purpose

Use this runbook when a claim, gate, release decision, remediation closure, role authority row, approval/consent boundary, public-release warning, or downstream reliance boundary is challenged.

## Required sequence

1. Open or update a row in `CONTESTATION_INTAKE_LEDGER.yml`.
2. Identify the stakeholder class and standing boundary in `STAKEHOLDER_CHALLENGE_REGISTER.yml`.
3. Route the row through `APPEAL_REVIEW_POLICY.yml` when a decision or claim is disputed.
4. Preserve minority interpretations in `DISSENT_MINORITY_REPORT_LEDGER.yml` when a gate passes but disagreement remains.
5. Add or update `HARM_IMPACT_REVIEW_LEDGER.yml` when the challenge alleges public misuse, reliance harm, deployment confusion, authority overclaim, or warning failure.
6. Add a row in `REDRESS_REVERSAL_LEDGER.yml` for any local correction, reversal, warning reinforcement, or changed artifact.
7. Run `tools/check_contestability_redress.py .` and retain the six reports for the current version.
8. Do not describe local contestability as public complaint handling, legal remedy, stakeholder consultation, public consent, external adjudication, or downstream recall.

## Forbidden shortcut

Do not close a challenge merely because the main validator passes. Validation shows local structural coherence; it does not resolve objections, provide appeal rights, cure harm, or notify downstream users.
