# 995 — Cloudtainer closure dossiers, attestation matrix, gap reopen triggers, and no outcome by attestation

## One-line thesis

Rev0796 made redress-verification follow-through explicit, but a verified redress control can still become another theater surface. Rev0797 adds non-private closure-dossier controls so the cube can say exactly what would be needed before any future gap closure while preserving unresolved exceptions, reopening triggers, and the rule that attestation is not the outcome.

## Why this matters

The archive now has a long fieldwork chain: source receipt → outcome-tail plan → sampling gate → intake control → authorization gate → execution control → release control → correction control → redress verification. That is useful, but it creates a new risk. Once the chain is long enough, a maintainer can point to the chain itself and say the work is effectively complete.

That would reproduce the archive's central failure mode in miniature. A signed attestation, closure memo, evaluation plan, correction package, disclosure-reviewed table, or remedy-owner status can be valuable. It still does not prove that the person or household got the material outcome, that unresolved exceptions are immaterial, that nonresponse bias is controlled, that source receipts are preserved, or that the archive has authority to close the gap.

Rev0797 adds `metadata/fieldwork_closure_dossiers.json`. The new surface sits after redress-verification controls and names what a future closure package must contain without collecting private data or closing anything now.

The governing rule is **no outcome by attestation**.

## Pattern pack

1. **Closure has a burden of proof.** A live gap can close only when a public-safe dossier ties the original gap, the material outcome fields, the verified cohort coverage, unresolved exceptions, and source receipts together.
2. **Attestation is not evidence unless it has a basis.** A signature, management assertion, or independent review statement must identify what was reviewed, what was not reviewed, and what remains outside the cube.
3. **Exceptions must survive closure pressure.** Nonresponse, unreachable cases, partial remedies, disputed remedies, rare cohorts, informal exits, recurrence windows, and withdrawn cases must remain blocker classes unless the closure dossier explicitly proves they do not change the finding.
4. **The dossier must include a reopen trigger.** If later evidence shows recurrence, source drift, disclosure risk, private-data leakage, material distribution failure, or cohort undercoverage, the gap reopens rather than relying on finality theater.
5. **Public-safe evidence is not private custody.** The cube may hold closure status, counts after disclosure review, source-claim receipt IDs, and attestation class. It must not hold names, addresses, claim numbers, docket numbers, contact rosters, linkage keys, payment files, court files, transcripts, recordings, or partner case records.
6. **Evidence standards are floors, not approvals.** Program evaluation standards, learning agendas, capacity assessments, and evidence-use practices support rigorous closure discipline. They do not certify any UI or housing tail as complete.
7. **A closed gap can still be partially wrong.** Closure must carry scope limits, denominator limits, and reopen clocks so future maintainers can challenge it without first proving misconduct.
8. **The gap ledger remains the truth surface.** A closure dossier can recommend closure only if the gap ledger records the decision, evidence level, unresolved exceptions, owner decision, and reopen trigger.

## What changed

### Fieldwork closure dossiers

Rev0797 adds two non-ready closure-dossier controls.

`FCD-UI-001` covers unemployment-insurance claimant closure readiness. It requires a public-safe closure package showing verified payment/backpay, hold removal, overpayment/waiver/refund, appeal correction, assisted or representative access, burden reduction, recurrence windows, unresolved exception counts, nonresponse-bias handling, source-preservation posture, and owner attestation class. It cannot close `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033` unless future maintainers add actual outside-cube verification and owner-approved closure entries.

`FCD-HC-001` covers housing household closure readiness. It requires a public-safe closure package showing possession or safe move, lockout repair, rehousing or shelter stability, arrears/subsidy cure, screening/record repair, retaliation/coercion checks, durable stability, informal-exit coverage, rare-cohort suppression, unresolved exceptions, source-preservation posture, and owner attestation class. It also remains non-closing.

Both controls inherit the full redress-verification chain. Neither collects evidence, authorizes fieldwork, stores private records, proves outcomes, or closes gaps.

### Closure evidence receipts

Rev0797 adds source-claim receipts for OMB A-11 Section 290, OMB M-20-12, OMB M-21-27, and GAO evidence-building practices. These sources support the discipline of rigorous, useful, transparent, and actionable evidence-building. They do not prove claimant payment, housing stability, source snapshots, or gap closure.

### Audit/refactor

The bounded refactor adds `validate_fieldwork_post_redress_links` to `tools/fieldwork_lint_helpers.py`. Closure-dossier rows must inherit the matching redress-verification, correction, release, execution, authorization, intake, sampling, and outcome-tail records. This removes one more parallel-chain loophole from the cube.

`tools/build_fieldwork_closure_dossiers.py`, `schema/fieldwork_closure_dossiers.schema.json`, `tools/build_steps.py`, `Makefile`, and `tools/lint_archive.py` make the closure-dossier surface part of normal build and lint.

## What this still does not do

It does not close a gap.

It does not verify a claimant or household outcome.

It does not create an approved evaluation, fieldwork authorization, source snapshot, secure-environment export, disclosure-reviewed output, correction, remedy, payment, waiver, appeal correction, possession retention, rehousing, screening repair, or durable-stability finding.

It does not store private evidence, contact rosters, linkage keys, claim numbers, docket numbers, addresses, court files, payment records, transcripts, recordings, partner case records, or raw audit logs.

## Anti-theater tests

1. Pick `FCD-UI-001`. Does it require material UI outcome fields and unresolved-exception handling rather than accepting a redress-verification row?
2. Pick `FCD-HC-001`. Does it require durable household outcome fields and informal-exit coverage rather than accepting a representation or filing count?
3. Pick either closure dossier. Does it inherit the matching redress-verification chain without inventing a parallel pathway?
4. Pick either closure dossier. Does it list allowed public-safe cube artifacts and prohibited private artifacts?
5. Pick either closure dossier. Does it require owner attestation class and independent review posture while warning that attestation does not prove outcome?
6. Pick either closure dossier. Does it include explicit reopen triggers?
7. Pick `generated/FIELDWORK_CLOSURE_DOSSIERS.md`. Does it show closure readiness as `not_ready` rather than `closed`, `approved`, or `validated`?
8. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the closure-dossier surface?

## Source posture

Use OMB A-11 Section 290 to ground evidence planning, capacity assessment, evaluation standards, and evaluation-policy posture. Use OMB M-20-12 and M-21-27 to ground rigorous, useful, and agency-embedded evaluation practice. Use GAO evidence-building practices to ground planning for results, assessing and building evidence, using evidence, and continuous improvement.

These sources support the closure-dossier method floor. They do not supply claimant or household evidence, authorize private-data custody, preserve source snapshots, or close any gap.

The practical rule is: **the cube may hold a public-safe closure dossier, but it must not become the private evidence room, the owner attestation itself, or the material outcome.**
