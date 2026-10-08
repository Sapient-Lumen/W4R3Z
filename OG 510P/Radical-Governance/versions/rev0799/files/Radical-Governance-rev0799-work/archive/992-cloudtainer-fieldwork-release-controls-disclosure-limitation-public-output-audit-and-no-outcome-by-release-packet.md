# 992 — Cloudtainer fieldwork release controls, disclosure limitation, public-output audit, and no outcome by release packet

## One-line thesis

Rev0793 made fieldwork execution safe enough to describe without collecting anything. Rev0794 adds the missing release layer: even after future lawful approval, collection, incident handling, audit review, and retention checks, no public output may be treated as claimant or household outcome proof unless disclosure limitation, de-identification limits, method integrity, harm review, and errata/retraction controls have passed outside the cube.

## Why this matters

The archive has been moving deliberately from doctrine to operational proof. It now has source-claim locators, outcome-tail plans, sampling gates, intake controls, authorization gates, and execution controls. That sequence is useful only if the last public-facing step does not launder process into proof.

The riskiest next failure is subtle. A release packet can look clean: a public table, a de-identified excerpt, a disclosure-reviewed quote, a dashboard row, a methods appendix, or a one-page public summary. Each can be safer than raw data, but none proves that benefits were paid, holds lifted, waivers granted, appeals corrected, households stayed housed, screening harms stopped, or coercion fell. A release packet can prove that an output was reviewed for public release. It is not the outcome itself.

The new `metadata/fieldwork_release_controls.json` sits after `metadata/fieldwork_execution_controls.json`. It is still non-closing. It defines what a future public output must show before it can even be considered usable evidence: disclosure-limitation method, small-cell and rare-cohort review, de-identification and re-identification risk posture, public-narrative controls, quality/integrity and nonresponse statements, participant/community harm review where applicable, and an errata/withdrawal/retraction path.

The governing rule is **no outcome by release packet**.

## Pattern pack

1. **A released output is not a field record.** The cube may carry a disclosure-reviewed, aggregate-safe public artifact; it must not carry raw private evidence.
2. **A public artifact is not an outcome.** A table, quote, summary, dashboard, or appendixed method proves publication posture, not material repair.
3. **De-identification is not disappearance.** Removing identifiers can reduce risk; it does not abolish re-identification, small-cell, linkage, or rare-cohort risk.
4. **Disclosure limitation is a release control, not a truth machine.** Suppression, aggregation, rounding, perturbation, noise infusion, and complementary suppression protect confidentiality but can also reduce resolution.
5. **Public narrative has its own risk.** A quote, office, building, landlord, shelter, employer, rare geography, or sequence of events can identify someone even when a table does not.
6. **Methods and denominators must travel with the output.** Nonresponse, exclusions, follow-up windows, unresolved harms, suppressed cells, and limits must be published with the finding.
7. **Errata and withdrawal are part of release.** A public output needs a correction, withdrawal, and notification path if disclosure risk, analytic error, participant harm, or source drift is later found.
8. **Archive custody remains bounded.** The release-control surface may store review status and public-safe claims; it may not store raw transcripts, audit logs, secure-environment output, incident details, or linkage keys.

## What changed

### Fieldwork release controls

Rev0794 adds two non-closing release controls.

`FRC-UI-001` covers any future unemployment-insurance claimant public output. It requires disclosure limitation, small-cell review, de-identification risk review, public-narrative controls, nonresponse and denominator publication, disclosure-reviewed quote controls, and an errata/withdrawal path before the archive can rely on the output.

`FRC-HC-001` covers any future housing household public output. It adds the same protections with housing-specific sensitivity for addresses, buildings, landlords, shelters, providers, court dockets, rare household trajectories, domestic safety, and retaliation risk.

Both controls link back to execution controls, authorization gates, field-intake controls, sampling gates, and outcome-tail plans. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither can close them.

### Release artifact boundaries

The release packet has two halves. Outside-cube owners may hold disclosure-review memos, suppression decisions, secure-environment output checks, de-identification risk reviews, participant quote permissions, reviewer notes, and raw analytic tables. The cube may only carry public-safe release status, source-claim receipts, aggregate-safe methodological limits, and a locator to the public artifact if one later exists.

The cube must not store raw rows, claim numbers, docket numbers, addresses, link keys, private screenshots, incident details, breach details, audit logs, reviewer workpapers, or secure-environment raw exports. It also must not publish rare-cohort narratives that can re-identify people through context.

### Public-output receipts

Rev0794 adds locator-level receipts for OMB Statistical Policy Directive No. 4, NIST SP 800-188, NIST IR 8053, DOL STRUDL statistical disclosure control, FCSM Statistical Policy Working Paper 22, and Census disclosure-avoidance practice. These receipts support release controls. They do not certify any output as safe, accurate, or outcome-proving.

### Audit/refactor

The bounded refactor extends `tools/fieldwork_lint_helpers.py` with a follow-on fieldwork link helper. Release controls now reuse the same chain check used by execution controls and add one more boundary: the release control must point to an execution control that points to the same authorization, intake, sampling, and outcome-tail records. This reduces cross-surface drift.

The Makefile and `tools/build_steps.py` now run `fieldwork_release_controls` after `fieldwork_execution_controls` and before common test matrices. That makes public-output release controls part of the normal build path, not a sidecar.

## What this still does not do

It does not publish any public output.

It does not approve disclosure review.

It does not de-identify data.

It does not certify any suppression, rounding, perturbation, noise, synthetic, differential privacy, or de-identification method.

It does not collect field evidence, access private records, store secure-environment outputs, or preserve source snapshots.

It does not prove payment, waiver, debt relief, appeal success, possession retention, re-housing, screening correction, durable stability, coercion reduction, or material redistribution.

It does not close any live gap.

## Anti-theater tests

1. Pick `FRC-UI-001`. Does it say no UI claimant output is released?
2. Pick `FRC-HC-001`. Does it prohibit address, docket, shelter, provider, landlord, building, and rare-household narrative disclosure?
3. Pick either release control. Does it require small-cell, rare-cohort, and re-identification review before public use?
4. Pick either release control. Does it require nonresponse, denominator exclusions, suppressed cells, and uncertainty to travel with any finding?
5. Pick either release control. Does it have an errata, withdrawal, and harm-response path?
6. Pick either release control. Does it link to the matching execution control and inherit the earlier authorization/intake/sampling/outcome-tail chain?
7. Pick `generated/FIELDWORK_RELEASE_CONTROLS.md`. Does it show blockers and release limits rather than field results?
8. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the new release layer?

## Source posture

Use OMB Statistical Policy Directive No. 4 as a quality, integrity, objectivity, transparency, and public-release discipline for statistical products, not as proof that a UI or housing output exists. Use NIST SP 800-188 and NIST IR 8053 to recognize that de-identification can reduce risk while requiring governance and re-identification caution, not as a magic anonymization switch. Use DOL STRUDL statistical disclosure control, FCSM Working Paper 22, and Census disclosure-avoidance material for suppression, aggregation, rounding, noise, and table/microdata disclosure practice, not as proof that a future archive output has passed review.

The practical rule is: **the cube can preserve release boundaries, but it must not become the raw output, disclosure review file, de-identification certificate, or outcome proof.**
