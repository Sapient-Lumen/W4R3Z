# 989 — Cloudtainer field-intake controls, consent/linkage firewalls, source-preservation safeguards, and no fieldwork by gate

## One-line thesis

Rev0790 made sampling gates concrete, but a sampling gate can still become dangerous theater if it is treated as permission to contact people, link administrative records, or store private lives; rev0791 adds field-intake controls so claimant and household evidence cannot move forward without lawful-basis, consent/waiver, PII-separation, linkage-key, adverse-action, and publication firewalls.

## Why this matters

The riskiest unfinished work is no longer discovering that affected-person evidence is missing. The archive now knows that. The risk is procedural overconfidence: a field sample is named, cohorts are listed, and suddenly a maintainer behaves as if the archive has authority to recruit claimants, query case records, link debts or dockets, or collect hardship stories.

That would recreate the very administrative failure the cube criticizes. People seeking unemployment benefits or housing stability are not test fixtures. Their participation can intersect with benefits, debt collection, court posture, representation, shelter access, immigration risk, domestic safety, landlord retaliation, and future screening. A protocol that cannot protect them should not collect them.

The new `metadata/field_intake_controls.json` therefore sits after `metadata/tail_sampling_gates.json` and before any future field-tail result. It is a pre-collection firewall. It does not collect evidence. It says what must be true before collection can begin.

The governing rule is **no fieldwork by gate**.

## Pattern pack

1. **A sampling gate is not contact authority.** A target population and cohort list do not authorize calls, interviews, observation, records access, or partner data linkage.
2. **Consent is not a paragraph pasted into a survey.** It requires understandable purpose, voluntary participation, no penalty, confidentiality limits, contacts, future-use posture, and an approved route for waiver or lawful basis where consent is not used.
3. **Linkage keys are operational hazards.** The archive may record that a key exists and who holds it, but the key, contact roster, identifiers, and partner case records must stay outside the cube.
4. **Administrative dependence makes refusal safety a proof condition.** Evidence from claimants or households is suspect if refusal can affect benefits, services, representation, shelter, debt, appeal, or enforcement posture.
5. **Small cells can be disclosures.** Aggregate-safe publication requires suppression, redaction, or non-public retention when cohort tails can identify people, staff, providers, shelters, or places.
6. **Legal/privacy sources are triggers, not approvals.** A regulation or guidance page can force a review question; it cannot replace owner, legal, ethics, privacy, or partner decisions.
7. **Stop rules must be operational.** If PII enters the cube, if retaliation risk appears, if key custody fails, or if consent/lawful basis is disputed, the field path stops before evidence is accepted.
8. **Refactor only to prevent drift.** The new builder and lint surface exist to catch broken links, missing controls, and false closing language; they are not a new registry for its own sake.

## What changed

### Field-intake controls

Rev0791 adds two non-closing controls.

`FIC-UI-001` covers unemployment-insurance claimant outcome-tail fieldwork. It blocks claimant contact and record linkage until there is an owner-approved evaluation question, human-subjects/legal/ethics determination, consent/waiver/lawful-basis path, data-sharing or partner agreement, separate research invitation, language and disability access route, adverse-action firewall, partner-held linkage key, no-PII-in-cube rule, and publication suppression plan.

`FIC-HC-001` covers housing household outcome-tail fieldwork. It blocks household contact and record linkage until there is an owner-approved evaluation question, consent or lawful-basis path, provider/court/community partner agreement, safety posture, no-landlord recruitment route, language/disability/trauma check, partner-held linkage key, separation from representation/service eligibility decisions, and publication controls that avoid exposing households, shelters, providers, or locations.

Both controls link back to the relevant sampling gates and outcome-tail plans. Both block `GAP-029`, `GAP-031`, `GAP-032`, and `GAP-033`. Neither can close them.

### Human-subjects and consent floor

Rev0791 adds source-claim receipts for 45 CFR 46 and OHRP materials. These receipts are deliberately locator-level. They do not tell the archive that a future project is research, non-research, exempt, approved, or waived. They only force a review boundary.

The practical rule is simple: if the work involves claimant or household interaction, observation, follow-up contact, identifiable private information, linkable coded data, or administrative records about living people, the maintainer cannot proceed by intuition. A qualified owner has to decide the legal, ethics, privacy, and program-governance route.

### Linkage firewall

The controls add a data-linkage firewall:

- partner-held identifiers only;
- linkage key never enters the cube;
- contact roster separated from outcome extract;
- minimum necessary fields only;
- no reidentification by the cube maintainer;
- retention/destruction schedule outside the cube;
- private screenshots, raw recordings, claim numbers, docket numbers, addresses, account identifiers, contact rosters, and partner case records are prohibited cube artifacts.

This is not merely privacy hygiene. It preserves evidentiary integrity. Once the cube stores private cases, it becomes a vulnerable operational record system rather than a public governance archive.

### Adverse-action firewall

For UI, participation refusal cannot affect benefits, claim timing, fraud review, waiver, appeal, or debt collection. The field researcher cannot be the adjudicator or collector.

For housing, participation refusal cannot affect representation, shelter, rental assistance, court support, or services. Recruitment cannot run through landlords or adverse parties. Safety planning is required where retaliation, lockout, domestic violence, immigration, or shelter exposure risks arise.

This changes the proof posture. Evidence from people under administrative dependence is not credible unless refusal is safe.

### Source and preservation controls

The new source receipts also advance `GAP-031` without closing it. 45 CFR, OHRP, NIST, and OMB/Digital.gov sources are now registered, health-tracked, and linked to the new controls. But they remain locator-level. They need point-in-time locators, lawful capture, content fingerprints, archival URIs, or documented no-capture decisions before any claim is source-preservation complete.

### Refactor/audit

The bounded refactor is the new `FIELD_INTAKE_CONTROLS` generated surface plus lint coverage. The lint now checks that field-intake controls:

- link to real tail-sampling gates and outcome-tail plans;
- include core human-subjects, exemption, consent, coded-data, PII, and privacy-records source receipts;
- block live affected-person, source-preservation, stewardship, and material-outcome gaps;
- remain `not_collected` and non-closing;
- prohibit enough private/linkage artifacts;
- keep linkage and key custody outside the cube;
- avoid allowing private identifiers in permitted cube artifacts;
- include adverse-action firewall language.

This is not a new doctrine family. It is a practical guard that prevents the previous two revisions from being misused.

## What this still does not do

It does not contact anyone.

It does not create consent language, a waiver, an IRB approval, a non-research determination, a data-sharing agreement, a system-of-record notice, or a partner protocol.

It does not link claim records, docket records, hotline records, provider records, shelter records, payment records, or screening records.

It does not store PII, private case records, raw recordings, screenshots, contact rosters, linkage keys, or household narratives.

It does not prove payment, waiver, appeal, possession, re-housing, debt relief, screening correction, or durable stability.

It does not close any live gap.

The advance is narrower: fieldwork now has to pass through a harm-aware intake firewall before future maintainers can even start.

## Anti-theater tests

1. Pick `FIC-UI-001`. Does it say refusal cannot affect benefits, claim handling, fraud review, waiver, appeal, or debt collection?
2. Pick `FIC-HC-001`. Does it forbid landlord/adverse-party recruitment and require safety planning for retaliation or lockout risk?
3. Pick either control. Does the linkage key stay outside the cube?
4. Pick either control. Does it prohibit names, addresses, private screenshots, raw recordings, contact rosters, linkage keys, and partner case records?
5. Pick a consent or human-subjects receipt. Is it only a locator and review trigger, not approval?
6. Pick `generated/FIELD_INTAKE_CONTROLS.md`. Does it show pre-collection blockers, not evidence results?
7. Pick `GAP-029`, `GAP-031`, `GAP-032`, or `GAP-033`. Does the gap remain live or in progress despite the new control surface?
8. Pick the source-health row for a new legal/privacy source. Does it say locator-level reliance only and refuse authorization by source row?

## Source posture

Use 45 CFR 46 and OHRP materials as review-boundary sources, not self-certification. Use the consent provisions as a floor for noncoercive, understandable, voluntary participation and confidentiality disclosure, not as a completed consent form. Use coded-private-information guidance as a key-custody and no-reidentification warning, not as permission to link records in the cube. Use NIST PII guidance and OMB A-130 Appendix I as confidentiality and records-about-individuals guardrails, not as collection authority.

The practical rule is: **the cube may plan and summarize safely; partners and authorized owners must hold private evidence, keys, permissions, and decisions.**
