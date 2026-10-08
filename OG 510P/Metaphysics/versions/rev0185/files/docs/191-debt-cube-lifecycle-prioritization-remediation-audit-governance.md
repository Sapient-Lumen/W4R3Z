# 191 — DebtCube lifecycle, prioritization, remediation, and audit governance

Version: rev0185  
Date: 2026-05-26 05:18 UTC  
Codename: debt-cube-lifecycle-prioritization-audit-refactor

## Purpose

This layer audits and refactors the DebtCube. Earlier cube work made concepts, sources, and claims more visible, but debt still behaved mostly like extracted prose: open debt phrases were collected, yet lifecycle state, priority, family recurrence, blocked claims, and remediation evidence were not sufficiently queryable.

rev0185 therefore treats debt as a first-class governance object. The release adds a debt observation index, debt lifecycle policy, relation map, debt-audit ledger, and generated debt relation/audit observations. It does not close debt. It makes open debt harder to hide.

## What changed

- Debt observations now carry lifecycle, priority, evidence, blocked-claim, recurrence, and closure-evidence fields.
- Debt relations expose links from each debt to its source artifact, debt family, lifecycle state, priority class, and blocked-claim class.
- Debt audit rows check row coverage, family coverage, lifecycle coverage, priority coverage, relation coverage, owner-assignment boundaries, and closure-evidence boundaries.
- The expanded cube now includes `DebtRelationCube` and `DebtAuditCube`.
- Query surfaces can ask after debt observations, debt relations, debt audit rows, and debt lifecycle policy.

## Allowed claim

rev0185 may claim that local debt observations, relation rows, lifecycle fields, and debt-audit rows are present and locally checked.

## Forbidden upgrades

rev0185 must not claim:

- all debt is closed;
- debt owners have been assigned;
- remediation has been externally verified;
- debt severity has been independently reviewed;
- public release is unblocked;
- legal, accessibility, source-currentness, claim-truth, or public-support debts are resolved;
- the priority model is authoritative.

## Boundary

The layer is a local structural refactor. It improves visibility and queryability of debt. It does not create external assurance, public readiness, or semantic correctness.
