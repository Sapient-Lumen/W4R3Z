# Release Gate, Decision, Risk-Acceptance, Waiver, and Assurance Review Runbook v1

## Scope

Use this runbook when a release candidate, package handoff, public-use statement, waiver request, residual-risk acceptance, or assurance claim is introduced or revised.

## Steps

1. Confirm `RELEASE_GATE_POLICY.yml` lists every blocking gate needed for the current release surface.
2. Confirm each gate has concrete rows in `ACCEPTANCE_CRITERIA_MATRIX.yml`.
3. Run `tools/check_release_gates.py .` and inspect failures before any release wording is repeated.
4. Confirm `WAIVER_EXCEPTION_LEDGER.yml` has no unbounded active waiver and that blocked gates remain blocked unless explicitly scoped.
5. Confirm `RISK_ACCEPTANCE_LEDGER.yml` accepts only archive-local residual risks and refuses public-use or operational risks.
6. Confirm `RELEASE_DECISION_LEDGER.yml` records gate results, waiver references, risk-acceptance references, assurance-case references, and allowed/forbidden decision language.
7. Confirm `ASSURANCE_CASE_SKELETON.yml` links top claims to gates, arguments, evidence artifacts, doubts, and forbidden upgrade claims.
8. Re-run the full validator and regenerate `MANIFEST.sha256` after reports are updated.

## Stop conditions

Stop the release if a blocking gate fails, an acceptance criterion lacks evidence, an active waiver lacks risk acceptance, a decision claims external approval, a risk acceptance covers operational or domain-authoritative use, or the assurance case claims more than local package readiness.
