# Post-Incident Learning Review Runbook v1

## Scope

Use this runbook after an incident, near miss, warning failure, deployment-boundary breach, public-reliance failure, derivative misuse, validation misclaim, or recovery dispute has been handled or partially handled under `166-incident-response-harm-review-near-miss-and-recovery-governance.md`.

This runbook does **not** provide public incident infrastructure, legal/medical/engineering/financial/safety advice, affected-party notice, independent root-cause review, or domain remediation. It is a local archive procedure for deciding what the archive should learn and what recurrence controls it can honestly claim.

## Entry criteria

Run this review when any of the following is true:

1. an incident is above INC2 or H2;
2. a near miss is above INC3;
3. a warning, status, source-boundary, validation, review-warrant, deployment, or public-use failure recurs;
4. a rollback, correction, withdrawal, deprecation, migration, or release fix closed the visible issue but may not prevent recurrence;
5. a steward, reviewer, derivative author, fork maintainer, teacher, or public relying user asks whether the same pattern can happen again.

## Stage order

1. **Link the source event.** Identify the governing incident record, reception packet, deployment-boundary record, or continuity-register signal.
2. **Freeze the learning target.** State whether the target is a file, output format, term, status, source boundary, public-use permission, deployment boundary, tool action, runbook, validator, release note, derivative, or cross-version pattern.
3. **Separate recovery from learning.** Record what has already been contained, corrected, rolled back, withdrawn, or closed, and what remains unexplained.
4. **Assign learning status.** Use LRN0–LRN9.
5. **Assign root-cause profile(s).** Use RCA0–RCA9 and distinguish isolated execution error from wording, compression, status, propagation, deployment, automation, source/domain, or systemic governance failure.
6. **Assign recurrence-risk class.** Use RR0–RR8.
7. **State corrective action.** Say what repaired the present event.
8. **State preventive action.** Say what prevents recurrence.
9. **Define verification.** Identify inspection, regression, semantic, workflow, deployment, public/derivative, or domain verification.
10. **Update affected artifacts.** Touch the relevant files, registers, schemas, runbooks, validator, release notes, or public/derivative notices.
11. **Set successor memory.** Record owner/steward, due trigger, closure evidence, residual risk, and reopen trigger.
12. **Check claim language.** Make sure the release note does not claim public safety, independent root-cause review, domain closure, external remediation, or future incident prevention unless those conditions exist.

## Exit criteria

A learning review may close only when it states:

- learning status;
- root-cause profile(s);
- recurrence-risk class;
- corrective action or no-action explanation;
- preventive action or unresolved-prevention statement;
- verification evidence or verification debt;
- affected artifacts;
- residual risk;
- successor-memory trigger.

If root cause is unknown, recurrence risk is unbounded, or preventive action is unverified, the packet should close as **open learning debt**, not as solved prevention.

## Forbidden shortcuts

- Do not treat "fixed" as "learned."
- Do not treat no visible harm as no recurrence risk.
- Do not treat domain handoff as archive-local learning closure.
- Do not treat a checklist addition as verified prevention.
- Do not treat a successful local validation as independent root-cause review.
- Do not treat a corrected current package as corrected public derivatives, forks, citations, or teaching copies.


## Rev0162 successor note

A closed post-incident learning packet should not be treated as durably effective unless `168` monitoring has stated monitoring status, effectiveness class, residual-risk trend, review trigger, escalation route, and sunset or renewal condition. CAPA closure is not the same as longitudinal effectiveness.
