# 987 — Cloudtainer claim-passage receipts, outcome-tail plans, source-health taxonomy-alias refactor, and no source by URL

## One-line thesis

The riskiest next failure is that the cube now knows it needs field proof, but still lacks a disciplined bridge from public source claims to privacy-bounded person or household tails; a URL, field signal, or aggregate chart must become a claim-passage receipt and a case-tail plan before it can support closure.

## Why this matters

Rev0786 and rev0787 made evidence receipts block premature closure. Rev0788 raised the floor by adding field signals and material-outcome dimensions. That still leaves two live risks.

First, the source-preservation gap can be postponed forever because the archive has many source keys and currentness rows but few claim-to-passage receipts. A source key tells a reader where to start. It does not say which passage supported which claim, whether the passage can be reconstructed after page drift, or whether the source was being used for more than it can prove.

Second, the affected-person gap can be postponed forever because the archive now knows that claimant observations, satisfaction surveys, eviction filings, and right-to-counsel aggregates are useful but insufficient. The next move has to be a bounded sampling plan: which cohorts, which material outcome fields, which non-users, which privacy constraints, and which closure floors would turn field signals into outcome tails.

This pass therefore adds two narrow operational surfaces. `metadata/source_claim_receipts.json` records a small set of claim-to-source locators with short anchor phrases, paraphrased passage summaries, and explicit evidence limits. `metadata/outcome_tail_plans.json` records two privacy-bounded sampling plans: unemployment insurance and housing continuity. Neither surface closes a gap. Both make it harder to hide behind a URL, an aggregate, or a survey.

The governing rule is **no source by URL**.

## Pattern pack

1. **A URL is identity, not evidence.** The source key identifies a public source, but the claim needs a locator, a short anchor, a passage summary, an evidence limit, and a preservation step.
2. **A locator is not a snapshot.** A section reference and anchor phrase are better than a raw URL but still fail if the page changes, the PDF is replaced, or the quoted claim is disputed.
3. **A short anchor is a navigation aid, not a republication.** The receipt stores only minimal phrases and paraphrases so the cube does not become a shadow copy of public sources.
4. **A field signal needs a tail plan.** Direct observation and surveys show burden and friction; they do not prove payment, debt relief, possession, re-housing, care, safety, or durable stability.
5. **Cohorts must include the uncomfortable denominator.** Paid claims and represented households are not enough. The sample must name holds, overpayments, abandoned applications, unrepresented tenants, defaults, informal exits, lockouts, and screening aftereffects.
6. **Closure floors must be negative until privacy is solved.** The archive can specify what a closure-ready tail would require without storing private records or pretending consent, legal basis, or partner capacity exists.
7. **Source-health taxonomy belongs in data, not hidden code.** Normalization rules now live in `metadata/source_health_taxonomy.json` so the raw ledger remains intact while comparison rules become reviewable.
8. **The refactor must reduce drift.** The pass moves hard-coded source-health alias logic out of the builder and adds generated surfaces for receipts and tail plans, because the risky work should be inspectable and reproducible.

## What changed

### Claim-passage receipt pilot

The new source-claim receipt surface starts with seven high-risk claims already doing work in the affected-person pilot:

- DOL/Illinois direct observation of UI claimants;
- DOL/Illinois UI survey design and its limits;
- OMB A-11 customer-experience feedback guidance;
- NYC Comptroller right-to-counsel implementation and capacity findings;
- Eviction Lab 2025 filing-pattern evidence;
- NARA web-records guidance; and
- Library of Congress web-archiving ephemerality guidance.

Each row stores a source key, note references, a claim family, a supported claim, locator type, source locator, short anchor phrase, paraphrased passage summary, preservation status, evidence limit, closure blockers, and next preservation step. The repeated preservation status is deliberate: these are locator receipts, not snapshots, content fingerprints, or archival receipts.

### Outcome-tail plans

The new outcome-tail plan surface makes the next field move concrete without collecting private data.

For unemployment insurance, the plan splits the sample into paid-without-hold, held or identity-friction, overpayment/waiver/appeal, and abandoned/non-user cohorts. The material tail asks for money received, payment delay, debt status, appeal or waiver result, time burden, staff assistance, non-user denominator, and hardship tail.

For housing continuity, the plan splits the sample into represented households, unrepresented/default households, informal-exit/lockout households, and screening/reapplication tails. The material tail asks for possession, physical displacement, informal eviction, shelter or re-housing, durable stability, debt or arrears, counsel access, and screening aftereffects.

The plans are intentionally not evidence. They are a denial of closure until such evidence exists under a privacy-approved protocol.

### Source-health taxonomy refactor

Rev0788 exposed taxonomy pressure in generated output, but the comparison rules were still embedded in `tools/build_source_health.py`. Rev0789 moves those aliases to `metadata/source_health_taxonomy.json` and teaches the builder to normalize from that metadata. This converts a hidden code convention into an inspectable maintenance object while preserving the original raw health and volatility labels.

This is not a full controlled vocabulary. It is a safer intermediate step: raw labels remain; generated counts become comparable; future owners can revise aliases without rewriting source history.

## Claim receipt floors

The current source-claim receipt floor is `section_locator_with_short_anchor_no_snapshot`. That means the archive can tell a future maintainer where the evidence was seen and what claim it supported, but it cannot yet prove the exact bytes.

A closure-ready source receipt would need at least one of the following:

- a lawful archived copy or archival URI;
- a content fingerprint for a fixed PDF or page capture;
- a stable page/line/section locator plus retrieval timestamp and page hash;
- a citation to an official versioned document with immutable release metadata; or
- a no-capture rationale and replacement source if capture is not permitted.

Until then, `GAP-031` remains live.

## Case-tail floors

The current outcome-tail floor is `planned_privacy_bounded_sample`. That means the archive can define cohorts and material fields, but it cannot yet claim field validation.

A closure-ready unemployment tail would need to join filing burden to eligibility, payment, debt, waiver/appeal, continuing certification, and hardship outcomes across both official users and people blocked outside the channel.

A closure-ready housing tail would need to join filing or threat to counsel access, payment posting, possession, informal exit, lockout, shelter or re-housing, screening aftereffects, and durable stability across represented and unrepresented households.

Until then, `GAP-029` and `GAP-033` remain live or in progress, not repaired.

## Audit/refactor

The refactor target was intentionally small and risk-based. Source-health normalization is useful, but hidden matching rules in a builder are a drift risk. They make generated output look like a stable classification while the classification logic sits outside the data under review.

The new `metadata/source_health_taxonomy.json` makes the alias rules reviewable, schema-validated, and included in the manifest. `tools/build_source_health.py` now loads normalization labels from that file. Lint checks that the taxonomy file exists, uses the current revision, includes both normalized fields, and is identified in generated `SOURCE_HEALTH.json`.

This pass also adds builders and lint for `SOURCE_CLAIM_RECEIPTS.*` and `OUTCOME_TAIL_PLANS.*`. The intent is not to add bureaucracy. It is to create two places where future work can fail honestly: one if source claims are not preserved beyond URLs, and one if field signals do not become person or household outcome tails.

## What remains deliberately open

`GAP-029` remains open because the cube still has no privacy-approved claimant or household sample.

`GAP-031` remains open because the new receipts are locator-level and do not include lawful snapshots, hashes, or archival receipts.

`GAP-033` remains in progress because the tail plans name material outcomes but do not yet test budgets, staffing, ownership, coercion, redistribution, or capture across more than UI and housing.

`GAP-030` remains in progress because an alias file is not a complete controlled vocabulary and one historical-preserved route is not a mature retirement system.

`GAP-032` remains open because licensing, contribution rules, maintainer authority, and succession require owner decisions.

## Failure modes

- **URL theater:** a source key is treated as if it proves the quoted claim.
- **Locator theater:** a section heading and anchor phrase are treated as if they preserve the source.
- **Anchor laundering:** a short navigation quote becomes a substitute for lawful passage capture or content fingerprinting.
- **Plan theater:** a sampling plan is treated as if field evidence has been collected.
- **Representative-only bias:** housed or paid successes are sampled while failures, non-users, defaults, and informal exits disappear.
- **Privacy collapse:** the cube starts storing private person or household data instead of boundary plans and aggregate-safe receipts.
- **Taxonomy laundering:** alias-normalized counts are mistaken for an owner-approved controlled vocabulary.
- **Refactor distraction:** builder cleanup consumes the session while the source and outcome gaps remain unadvanced.

## Anti-theater tests

1. Pick a source claim. Can the reader find the source key, locator, short anchor, passage summary, evidence limit, and next preservation step?
2. Pick a claim receipt. Does it avoid storing long quotations, private data, or source copies?
3. Pick a source receipt level. Does it clearly distinguish locator-level evidence from snapshot or fingerprint evidence?
4. Pick a UI tail plan. Does it include held claims, identity friction, overpayments, appeals/waivers, abandonments, and non-users?
5. Pick a housing tail plan. Does it include unrepresented/default households, informal exits, lockouts, shelter/re-housing, and screening aftereffects?
6. Pick a live gap. Do claim receipts and tail plans block closure rather than repairing the gap by plan existence?
7. Pick source-health taxonomy output. Can the alias rules be inspected in metadata rather than reverse-engineered from Python code?
8. Pick the build. Are the new generated receipt and tail-plan surfaces reproducible and included in the manifest?

## Source posture

Use the DOL direct-observation and survey-design pages as field-signal examples, not as outcome validation. Use OMB A-11 Section 280 as support for customer feedback and service-journey measurement, not for completed benefit proof. Use NYC Comptroller and Eviction Lab sources as aggregate housing signals, not household tails. Use NARA and Library of Congress web-records/web-archiving guidance to ground the source-preservation gap, not as preservation of any specific UI or housing claim.
