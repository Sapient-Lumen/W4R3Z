# 994 — Cloudtainer redress verification controls, follow-through ledgers, internal-control repair, and no outcome by redress route

## One-line thesis

Rev0795 made post-release correction safer to describe without correcting anything. Rev0796 adds the missing follow-through layer: even after a future correction, withdrawal, redress route, or notification, the cube must require separate verification that affected claimants or households were actually made whole.

## Why this matters

A redress route can become another theater surface. A claimant can receive a correction notice but no payment. A debt can be marked for review but remain collectible. A hold can be lifted in one system and persist in another. A tenant can win a dismissal yet still move out, face screening harm, or re-enter instability. A corrected public table can make the program look repaired while the harmed cohort still waits outside the official narrative.

The archive has been steadily adding gates from source receipts to fieldwork intake, authorization, execution, release, and correction. The next risk is **redress-route theater**: the moment a ticket, referral, corrected dashboard, or public apology becomes the endpoint instead of a bridge to verified repair.

Rev0796 adds `metadata/fieldwork_redress_verification_controls.json`. It sits after `metadata/fieldwork_correction_controls.json` and remains non-closing. It records what must be verified outside the cube before anyone can rely on a public correction as aligned with actual remedy.

The governing rule is **no outcome by redress route**.

## Pattern pack

1. **A remedy route is not a remedy.** Routing a claimant or household to an office, ticket, complaint, or correction queue proves only that a route exists.
2. **Public correction and private repair must stay separate.** A table correction can be complete while claimant payment, waiver, appeal correction, possession retention, or screening repair is still incomplete.
3. **Actual outcome fields must be named.** UI needs payment, hold, debt, waiver, appeal, assisted access, and burden-repair checks. Housing needs possession or safe move, lockout repair, arrears or subsidy cure, rehousing, screening repair, retaliation risk, and durable stability checks.
4. **Unresolved exceptions are evidence, not mess.** Nonresponse, unreachable cases, partial remedies, disputes, deceased or withdrawn cases, informal exits, and recurrence windows must remain visible as blockers.
5. **Internal control repair must be tested.** A corrective action is not effective until it is tracked, tested, verified, documented, and tied to responsible owners and dates.
6. **The cube must not hold the remedy file.** Payment records, court files, address records, linkage keys, redress case files, private complaints, and administrative extracts remain outside the cube.
7. **Aggregate verification still needs disclosure control.** Even exception counts can expose rare cohorts, buildings, docket paths, or claimant pathways.
8. **A verified control still does not end material analysis.** Program repair for a sample does not prove distributional justice, power shift, non-user recovery, or durable community-level effects.

## What changed

### Fieldwork redress verification controls

Rev0796 adds two non-closing verification controls.

`FRV-UI-001` covers unemployment-insurance claimant redress follow-through. It requires outside-cube verification of payment or backpay, identity/access/fraud hold removal, overpayment waiver or refund, appeal or reconsideration correction, representative or assisted-access restoration, burden reduction, and recurrence-window checks. It tracks unresolved exceptions as blockers instead of omitting them.

`FRV-HC-001` covers housing household redress follow-through. It requires outside-cube verification of possession retention or safe move, lockout or exclusion repair, rehousing or shelter stability, arrears or subsidy cure, screening or record-harm correction, retaliation/coercion risk checks, and durable-stability windows. It also blocks reliance when informal exits, default cases, doubled-up households, shelter returns, or nonresponse make the verified tail unrepresentative.

Both controls inherit the correction → release → execution → authorization → intake → sampling → outcome-tail chain. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither closes them.

### Internal-control repair receipts

Rev0796 adds locator-level receipts for OMB Circular A-123 (2026) and the GAO 2025 Green Book. These sources support corrective-action and internal-control follow-through: responsible owners, timelines, validation, evidence, monitoring, and reporting. They do not prove a remedy occurred.

### Audit/refactor

The bounded refactor extends `tools/fieldwork_lint_helpers.py` with a post-correction chain validator. A redress-verification row must inherit the full chain through the matching correction control and cannot invent a parallel release, execution, authorization, intake, sampling, or outcome-tail lineage.

`tools/build_fieldwork_redress_verification_controls.py`, `schema/fieldwork_redress_verification_controls.schema.json`, `tools/build_steps.py`, `Makefile`, and `tools/lint_archive.py` make the redress-verification surface part of the normal build and lint chain.

## What this still does not do

It does not verify a claimant or household outcome.

It does not approve fieldwork, authorize data access, perform linkage, issue payment, waive debt, correct an appeal, retain possession, repair screening harm, rehouse anyone, or prove durable stability.

It does not store private redress files, payment records, court files, administrative extracts, linkage keys, addresses, claim numbers, docket numbers, or household compositions.

It does not close any live gap.

## Anti-theater tests

1. Pick `FRV-UI-001`. Does it require actual payment, hold, debt, appeal, access, and burden checks rather than a route or notice?
2. Pick `FRV-HC-001`. Does it require possession/safe move, lockout repair, rehousing, arrears/subsidy cure, screening repair, and durable stability checks rather than court filing outcomes alone?
3. Pick either control. Does it treat unresolved exceptions and nonresponse as blockers rather than omissions?
4. Pick either control. Does it prohibit private remedy records from the cube?
5. Pick either control. Does it inherit the matching correction, release, execution, authorization, intake, sampling, and outcome-tail records?
6. Pick `generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md`. Does it show verification blockers rather than verified outcomes?
7. Pick `SCR-A123-2026-001` or `SCR-GAO-GREENBOOK-2025-001`. Do they support corrective-action discipline without proving repair?
8. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the redress-verification layer?

## Source posture

Use OMB Circular A-123 (2026) as a corrective-action and internal-control verification discipline: track, test, validate, document, and report remediation. Use the GAO 2025 Green Book as an internal-control framework for operations, reporting, compliance, improper-payment, information-security, and significant-change risks. Use OMB A-11 Section 280 and the information-quality receipts as service-feedback and public-correction context only.

The practical rule is: **the cube can preserve redress verification boundaries, but it must not become the redress file, remedy authority, administrative extract, or outcome proof.**
