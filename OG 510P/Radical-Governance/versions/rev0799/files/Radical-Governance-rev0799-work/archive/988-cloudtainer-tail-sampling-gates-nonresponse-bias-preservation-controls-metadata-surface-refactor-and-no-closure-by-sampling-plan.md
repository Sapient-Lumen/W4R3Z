# 988 — Cloudtainer tail-sampling gates, nonresponse-bias floors, preservation controls, metadata-surface refactor, and no closure by sampling plan

## One-line thesis

The archive now knows which UI claimant and housing household tails it needs, but the riskiest next failure is calling that plan field validation; rev0790 turns the plans into sampling, nonresponse-bias, privacy, and source-preservation gates while keeping them non-closing.

## Why this matters

Rev0789 made a necessary move from aggregate signals to outcome-tail plans. That move still leaves a dangerous soft spot. A plan can look concrete because it names cohorts, material fields, and privacy exclusions. But a plan is not a sample frame, a sample frame is not a completed sample, and a completed convenience sample is not automatically representative or safe to publish.

The archive therefore needs a new kind of gate between `metadata/outcome_tail_plans.json` and any future claim that affected-person proof exists. The gate has to answer four questions before the cube can move forward:

1. Who is in the target population, including people outside the successful official route?
2. What sampling frame reaches paid users, blocked users, debt/remedy cases, represented households, unrepresented households, informal exits, lockouts, and non-users?
3. What nonresponse-bias and missingness posture prevents a survey or partner intake list from becoming false certainty?
4. What privacy and source-preservation controls prevent the archive from storing private lives or relying on live URLs?

The new `metadata/tail_sampling_gates.json` answers those questions for two pilot families: unemployment insurance and housing continuity. It deliberately does not collect data. It says what must be true before data collection can begin and what would disqualify a later closure claim.

The governing rule is **no closure by sampling plan**.

## Pattern pack

1. **A tail plan is not a sampling frame.** Cohorts and fields name what must be learned; they do not show who can be reached or who remains invisible.
2. **A sample frame is not field validation.** A portal population, docket set, survey-response pool, legal-aid intake set, or community referral list is only one capture route unless exclusions are named.
3. **Successful cases are not the denominator.** Paid claimants and represented tenants are necessary cohorts, but they are the easiest cases to overcount.
4. **Nonresponse is substantive evidence.** Unknown, low, or skewed response is not a footnote. It is a live claim about who the archive still cannot hear.
5. **Privacy gates precede proof gates.** The cube may store sample design, cohort requirements, and aggregate-safe summaries. It must not store private claimant or household records.
6. **Source preservation is part of fieldwork.** A future field-tail result still needs preserved method and source receipts; otherwise it inherits the same URL fragility the archive is trying to defeat.
7. **Disqualifiers must be explicit.** A gate should say what makes a future result non-closing: missing non-users, no follow-up after cure, no nonresponse-bias posture, private identifiers in the cube, or source locators without preservation plan.
8. **Refactor only where it reduces drift.** The session should not sprawl into another doctrine layer. The limited refactor centralizes generated metadata-surface helpers used by evidence receipts, source-claim receipts, outcome-tail plans, and sampling gates.

## What changed

### Tail sampling gates

The new `metadata/tail_sampling_gates.json` defines two design-ready, non-collected gates.

`TSG-UI-001` covers unemployment insurance claimant outcome tails. It requires a target population that includes filing, certification, issue resolution, overpayment, waiver, appeal, staff-assisted, abandoned, and non-user routes. Its sampling frame cannot be a claimant portal population alone. It must combine agency claim or issue states, survey or observation follow-up consent, legal-aid or community navigator referrals, field-office assisted access, overpayment and appeal records, and a documented non-user route.

The UI gate keeps four cohorts visible: paid without hold, held or identity-friction, overpayment/waiver/appeal, and abandoned or non-user. It requires material fields for money received, payment delay, debt status, appeal or waiver result, time burden, staff assistance, non-user denominator, and hardship tail.

`TSG-HC-001` covers housing continuity household outcome tails. It requires a target population that includes arrears, notice, filing, default, representation triage, informal exit, lockout, shelter entry, re-housing, and screening aftereffect. Its sampling frame cannot be court filings or represented cases alone. It must combine court docket exposure, legal-aid or provider intake, rental-assistance or payment-posting signals, tenant hotline or community organization referrals, shelter or re-housing service signals, and an informal-exit or lockout route.

The housing gate keeps four cohorts visible: represented households, unrepresented/default households, informal exit or lockout, and screening or reapplication tail. It requires material fields for possession, physical displacement, informal eviction, shelter or re-housing, durable stability, debt or arrears, counsel access, and screening aftereffect.

Neither gate closes anything. Both are blockers.

### Nonresponse-bias floor

Rev0790 adds source-claim receipts for the method floor behind the sampling gates.

`SCR-SAMPLE-001` points to OMB statistical survey standards for target population, sampling frame, sampling design, data-collection method, and justification of nonprobability methods.

`SCR-NRBA-001` points to FCSM nonresponse-bias reporting guidance. Its role is to prevent survey counts, claimant feedback, legal-aid intake, or household follow-up from becoming false certainty when response rates, missingness, or auxiliary-data limits are not known.

The archive is not pretending that the UI and housing pilots will necessarily be statistical surveys. Some evidence may be qualitative, administrative, or partner-held. The point is narrower: if future maintainers make claims about a population, they must name the population, the frame, response limits, bias risks, and what cannot be generalized.

### Evidence-building and privacy floor

`SCR-EVIDENCE-001` points to OMB Evidence Act guidance for evaluation planning, capacity assessment, stakeholder engagement, and planned evaluation activities. Its role is to stop the field-tail work from becoming an ad hoc evidence grab without an owner, question, data-access basis, and publication posture.

`SCR-PRIV-001` points to the NIST Privacy Framework as a privacy-risk management anchor. Its role is to block a tempting but dangerous shortcut: storing private claimant or household details directly in the cube. The only acceptable cube artifacts are design gates, receipts, aggregate-safe summaries, redacted descriptions, and owner-approved preservation records.

`SCR-OES-001` points to GSA OES Evidence Act toolkits as practical planning support for learning agendas, annual evaluation plans, and capacity assessment materials. It helps turn the tail gate from a static checklist into a future workplan, without pretending that a toolkit is evidence.

### Source-preservation controls

Each tail gate now carries source-preservation controls. Future work must hash fixed PDFs when lawful, record retrieval timestamp and locator, store only short anchors and paraphrases inside the cube, and record no-capture rationale for live pages or changing dashboards.

This keeps `GAP-031` open. The new source receipts are still locator-level. A closure-ready source receipt would need lawful capture, archival URI, content fingerprint, fixed-document hash, or a documented no-capture alternative.

### Metadata-surface refactor

The refactor is intentionally small. `tools/metadata_surface.py` centralizes Markdown cell escaping, sorted counter serialization, and JSON/Markdown surface writing. The evidence receipt, source-claim receipt, outcome-tail plan, and tail-sampling gate builders now use this shared helper.

This removes repeated generated-surface glue without changing the underlying data model. The purpose is not elegance. It is to reduce the number of places where small surface differences can create silent drift or false comparison.

## What this still does not do

It does not collect claimant or household evidence.

It does not create a license, research protocol, consent language, data-sharing agreement, IRB or ethics review, legal basis, or partner agreement.

It does not choose a jurisdiction, time window, agency partner, legal-aid partner, community recruitment route, or sample size.

It does not claim representativeness, field validation, durable outcome proof, source preservation, or closure.

The advance is narrower but important: a future maintainer now has concrete gates that can fail before the archive accepts field evidence.

## Closure disqualifiers

A future UI or housing field result should be non-closing if any of these are true:

- only successful official-route cases were sampled;
- abandoned applications, non-users, unrepresented tenants, defaults, informal exits, or lockouts are missing;
- response rates and missingness are unknown or unreported;
- nonresponse-bias risk is not assessed;
- there is no follow-up after cure, payment, possession, re-housing, waiver, appeal, or correction;
- private identifiers or screenshots enter the cube;
- source passages remain only as live URLs or locator phrases;
- small cells or retaliation risks are not suppressed or redacted;
- the fieldwork has no owner, partner protocol, legal/privacy basis, or publication boundary.

## Anti-theater tests

1. Pick `TSG-UI-001`. Does it include paid, held, debt/remedy, abandoned, and non-user claimant routes?
2. Pick `TSG-HC-001`. Does it include represented, unrepresented/default, informal-exit/lockout, and screening-aftereffect household routes?
3. Pick any gate. Does it forbid private records in the cube and name a kill switch if private identifiers enter the package?
4. Pick any cohort. Does it include a denominator audit rather than only outcome fields?
5. Pick a source-claim receipt. Does it remain locator-level unless a hash, archival URI, or lawful capture exists?
6. Pick `generated/TAIL_SAMPLING_GATES.md`. Does it show the gates as blockers and prerequisites, not as results?
7. Pick `GAP-029`, `GAP-031`, or `GAP-033`. Does the gap remain live or in progress despite the new gates?
8. Pick a receipt builder. Does generated-surface glue now come from `tools/metadata_surface.py` rather than several local copies?

## Source posture

Use OMB statistical survey standards and FCSM nonresponse-bias guidance as sampling and bias floors, not as proof that the archive has a representative sample. Use OMB Evidence Act and GSA OES materials as evaluation-planning anchors, not as evidence that fieldwork has run. Use the NIST Privacy Framework as a privacy-risk management anchor, not as permission to store private records in the cube. The old UI and housing sources remain field-signal and aggregate-signal examples; the new gates say what would be required before those signals can become closure-relevant tails.
