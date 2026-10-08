# Accountability, Authority, Segregation, Delegation, Approval, and Review Runbook v1

Purpose: prevent role names, assignments, approvals, warnings, and delegated tasks from laundering stronger authority than the archive actually has.

1. Identify the governance surface: release, claim language, custody, observation, remediation, closure, or public-use boundary.
2. Locate the accountable role in `ROLE_AUTHORITY_MATRIX.yml` and `ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml`.
3. Confirm the role's forbidden authorities do not include the authority being claimed.
4. Check `SEGREGATION_OF_DUTIES_POLICY.yml` for prohibited pairings and independence boundaries.
5. Check `DELEGATION_HANDOFF_LEDGER.yml` if execution was delegated; verify retained accountability and nondelegable duties.
6. Check `APPROVAL_CONSENT_LEDGER.yml` before using approval, consent, permission, signoff, authorization, or reliance language.
7. Record an accountability review in `ACCOUNTABILITY_REVIEW_LEDGER.yml` when new release, public-use, delegation, or closure language is introduced.
8. Run `tools/check_accountability_authority.py .` and write the six resulting reports to `REGISTERS/`.
9. Re-run release-gate, fixture, query-regression, reference-integrity, and archive validation checks.

Forbidden shortcuts:

- Do not treat a validator as an approver.
- Do not treat a maintainer as an independent reviewer.
- Do not treat a warning as public consent.
- Do not treat local release approval as operational deployment approval.
- Do not treat delegation as accountability transfer.
- Do not treat local duty separation as institutional independence.
