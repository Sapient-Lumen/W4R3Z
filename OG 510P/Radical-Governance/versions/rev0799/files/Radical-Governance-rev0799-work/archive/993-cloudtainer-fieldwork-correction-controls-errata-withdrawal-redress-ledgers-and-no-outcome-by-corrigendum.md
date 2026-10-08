# 993 — Cloudtainer fieldwork correction controls, errata/withdrawal/redress ledgers, and no outcome by corrigendum

## One-line thesis

Rev0794 made public release safer to describe without releasing anything. Rev0795 adds the missing post-release layer: if a future public output is later found wrong, harmful, misleading, disclosure-risky, denominator-defective, or source-stale, the cube must know how to correct, withdraw, notify, version, and preserve the correction trail without treating the correction packet as the lived outcome.

## Why this matters

A fieldwork-derived public output can fail after release. A suppressed cell may still be inferable. A de-identified quote may identify a household through local context. A method appendix may omit nonresponse bias. A denominator may exclude non-users. A claimant cohort may be misclassified. A table may be reproduced after a withdrawal. A corrected dashboard can look more authoritative than the first version while still proving only that a public artifact changed.

The archive already blocks collection, execution, and release theater. The next risk is **correction theater**: an erratum, withdrawal notice, updated table, redress ticket, or retraction page is presented as if it proves payment, waiver, appeal correction, housing stability, screening repair, retaliation reduction, or material redistribution.

The new `metadata/fieldwork_correction_controls.json` sits after `metadata/fieldwork_release_controls.json`. It is still non-closing. It defines the minimum post-release correction posture: defect intake, information-quality correction routing, withdrawal/retraction clocks, affected-party notification and redress routing, version/citation hygiene, public harm review, and a public-safe correction ledger.

The governing rule is **no outcome by corrigendum**.

## Pattern pack

1. **A correction is a public-artifact event.** It does not by itself prove that the underlying person or household outcome changed.
2. **Defect intake must be plural.** Public complaints, affected-person reports, source drift, partner notice, audit finding, disclosure-risk discovery, replication failure, and maintainer review must all have a route.
3. **Information-quality requests need clocks and ownership.** A correction mechanism without a named owner, timeliness classification, and response path is a courtesy inbox, not a control.
4. **Withdrawal is not deletion.** A withdrawn public output needs a tombstone, replacement pointer, citation warning, and preservation boundary.
5. **Retraction must travel downstream.** If an output was cited in notes, dashboards, matrices, public summaries, or partner pages, the correction route must identify affected surfaces.
6. **Redress is not publication.** Notifying an agency, reviewer, or public page is not the same as restoring benefits, correcting debt, preserving possession, removing a screening mark, or repairing harm.
7. **The correction ledger must be public-safe.** It may store status, scope, version, and public locator data. It must not store private claimant facts, household details, linkage keys, incident narratives, or raw audit records.
8. **A corrected finding can still be wrong about the world.** Updated public facts still need source receipts, field-tail evidence, denominator explanation, and material outcome proof.

## What changed

### Fieldwork correction controls

Rev0795 adds two non-closing correction controls.

`FCC-UI-001` covers future unemployment-insurance claimant public outputs. It requires correction intake for analytic error, denominator defect, source drift, disclosure risk, claimant harm report, cohort misclassification, downstream citation drift, and remedy confusion. It requires information-quality correction routing, withdrawal or republication decisions, public version warnings, affected-office and participant-safety notification where appropriate, and a redress path that does not confuse public correction with claimant payment or waiver.

`FCC-HC-001` covers future housing household public outputs. It adds the same controls with housing-specific sensitivity for address/building inference, docket reuse, landlord/provider/shelter retaliation risk, informal displacement, screening harms, court-record corrections, downstream advocacy/policy citation drift, and household safety.

Both controls link back to release controls, execution controls, authorization gates, field-intake controls, sampling gates, and outcome-tail plans. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither can close them.

### Correction artifact boundaries

The correction packet also has two halves. Outside-cube owners may hold private complaints, participant reports, reviewer workpapers, raw tables, audit logs, secure-environment outputs, legal/privacy analysis, breach records, and redress case files. The cube may only carry public-safe correction status, defect class, version pointers, source-claim locator receipts, and a statement of what remains unproven.

The cube must not store claimant names, addresses, claim numbers, docket numbers, household composition, linkage keys, private screenshots, incident details, breach details, audit logs, reviewer workpapers, or confidential correction-request submissions.

### Public correction receipts

Rev0795 adds locator-level receipts for OMB's 2002 Information Quality Guidelines, OMB M-19-15, OMB's 2023 IQA FAQ, DOL's Information Quality Guidelines, and the Statistical Policy Directive No. 4 addendum/self-review logic. These receipts support correction routes. They do not certify any correction as sufficient, any public product as accurate, or any claimant/household outcome as repaired.

### Audit/refactor

The bounded refactor extends `tools/fieldwork_lint_helpers.py` again. Correction controls now use a dedicated post-release helper that validates the whole chain through release control → execution control → authorization gate → field-intake control → sampling gate → outcome-tail plan. This removes the chance that a correction row creates a parallel lineage or points to a stale predecessor.

The Makefile and `tools/build_steps.py` now run `fieldwork_correction_controls` after `fieldwork_release_controls` and before common test matrices. That makes post-release correction a normal generated-surface dependency rather than an optional appendix.

## What this still does not do

It does not publish a correction.

It does not withdraw or retract any output.

It does not approve an information-quality response.

It does not notify affected people, courts, agencies, partners, or downstream users.

It does not preserve private correction submissions, redress files, audit logs, source snapshots, or secure-environment output.

It does not prove payment, waiver, appeal success, overpayment cure, possession retention, re-housing, screening correction, durable stability, coercion reduction, or material redistribution.

It does not close any live gap.

## Anti-theater tests

1. Pick `FCC-UI-001`. Does it say no UI public correction is activated?
2. Pick `FCC-HC-001`. Does it prohibit address, docket, landlord, shelter, provider, and household-specific correction material from the cube?
3. Pick either correction control. Does it require defect intake and correction-request routing rather than a generic errata link?
4. Pick either correction control. Does it require withdrawal/retraction, version, citation, and downstream-surface checks?
5. Pick either correction control. Does it distinguish public correction from individual redress and material repair?
6. Pick either correction control. Does it inherit the matching release/execution/authorization/intake/sampling/outcome-tail chain?
7. Pick `generated/FIELDWORK_CORRECTION_CONTROLS.md`. Does it show blockers and correction limits rather than outcome results?
8. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the correction layer?

## Source posture

Use OMB's Information Quality Guidelines and M-19-15 as public-information quality and correction-route disciplines, not as proof that a fieldwork output exists or that correction has occurred. Use the 2023 IQA FAQ for correction-level and privacy/confidentiality caution, not as a universal formula. Use DOL's information-quality guidance as an agency correction mechanism example, not as a claimant remedy. Use Statistical Policy Directive No. 4 and its self-review addendum as a statistical product review discipline, not as proof of any particular public output.

The practical rule is: **the cube can preserve correction boundaries, but it must not become the complaint file, correction adjudication, retraction authority, redress record, or outcome proof.**
