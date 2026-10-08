# Accessibility, usability, and language access as integrity controls

**Track:** Shared

Accessibility and language access are often treated as “compliance.” For **The Election Stack**, treat them as
*integrity controls*: if voters cannot reliably understand, mark, verify, and cast a ballot (or are systematically
prevented from doing so), the evidence stack is incomplete even if cryptography is perfect.

This document stays **tight**: it does not restate statutes or standards. It gives a **minimal control set** and a
**minimal publishable-proof set** that can plug into `246-assurance-case-skeleton-and-evidence-minimization.md`.

## Scope

Covers:
- In-person voting: polling place accessibility + accessible voting equipment.
- Voter-facing web properties: registration portals, ballot tracking, voter info, accessibility statements.
- Language access: bilingual materials, translated interfaces, interpreter flows.

Not covered (but related): broader disability civil-rights law surveys; procurement law; full human factors manuals.

## Anchors (external, not requirements)

Use these as canonical references when you need to justify a control, *without copying large text into the archive*:
- **EAC** “Voting Accessibility” resource hub (HAVA context, links).
- **EAC** “Accessible Elections — Information for Election Officials” training series (end-to-end accessibility).
- **EAC** “Making Voting Accessible” quick start guide (practical checklist framing).
- **DOJ ADA** “Voting and Polling Places” overview (ADA applies to registration, polling places, and voting methods).
- **DOJ ADA** polling-place checklist (fieldable measurement checklist).
- **EAC** language access resources (VRA Section 203 context and jurisdiction coverage pointers).
- **DOJ** Section 203 language-minority protections explainer (plain-language summary).
- **WCAG 2.2** (web accessibility benchmark for voter-facing web experiences).

## Minimal control set (A-grade, deployable)

Think in three “failure modes”:
1) **Access failure** (can’t physically access, can’t perceive/operate),
2) **Comprehension failure** (can’t understand language/instructions),
3) **Verification failure** (can’t confirm selections match intent).

### A1. Polling place accessibility (in-person)
Controls:
- Pre-election accessibility survey using a standardized checklist; record issues + temporary remedies.
- “Accessible route” is treated as a dependency chain: arrival → entry → voting area (breaks anywhere are failures).
- Documented contingency: alternate accessible location or alternate means where legally allowed.

Minimal publishable proofs:
- **Signed checklist attestation** per site (no photos unless needed; prefer “defect codes” + measurements).
- **Issue log**: barrier found → remedy → timestamp → responsible party (hashable).

### A2. Accessible voting equipment and ballot marking/verification
Controls:
- At least one accessible station per polling place configured and tested (audio/tactile, assistive tech compatibility).
- Setup checklist includes privacy and independence (e.g., headset availability, privacy sleeve, station placement).
- “Verification step” usability: voters can review selections in an accessible modality before casting.

Minimal publishable proofs:
- Pre-election **setup/functional test checklist** (signed + hashed).
- **Accessibility incident log** (equipment failure, missing supplies, assistive request patterns).

### A3. Voter-facing web accessibility (registration/info/tracking)
Controls:
- WCAG-targeted accessibility review (at least A/AA posture per jurisdiction policy) for critical voter flows.
- Change control: accessibility regressions treated like security regressions (block release or require mitigation).
- Publish an accessibility contact channel + response SLO (so barriers become observable).

Minimal publishable proofs:
- **Accessibility conformance snapshot** (tool report + human spot-check notes) with hashes and test date.
- **Regression gate policy**: which checks run before deploy, who can override, and how overrides are logged.

### A4. Language access and interpreter flows
Controls:
- Maintain a language coverage map for the jurisdiction (what is required/provided, where, and in what form).
- For translated materials: establish a review workflow (translation → review → approval) and versioning.
- Poll-worker runbook for interpreter assistance and for voters who bring an assistant (log only minimal metadata).

Minimal publishable proofs:
- **Language inventory**: which artifacts exist per language (ballot, instructions, signage, web pages).
- **Translation provenance**: who produced/reviewed, version ids, and dates (no PII).

## Evidence minimization patterns (don’t bloat the archive)

Prefer:
- Hashes of artifacts + reproducible build paths (e.g., “generate signage pack vX from repo commit Y”).
- Short, structured logs (CSV/JSON) over long narratives.
- “One photo only when needed” principle: photos are high-risk for incidental PII.

Avoid:
- Uploading full vendor manuals or long training decks (cite them; store only deltas/checklists).
- Storing any voter-identifying data (including in screenshots of web forms or helpdesk tickets).

## Integration points in this archive

- Use the **assurance-case skeleton** to express these as claims with small evidence objects:
  `docs/246-assurance-case-skeleton-and-evidence-minimization.md`.
- Pair with **ops communications + chain-of-custody** for public status and incident comms:
  `docs/247-ops-security-controls-comms-and-chain-of-custody.md`.
- If a track explores remote return (B/C), treat accessibility upgrades as *necessary but not sufficient*; do not
  let “accessible” become a rhetorical substitute for “secure.”

## Suggested next tight artifacts (optional)

If you need more precision without bloat, create *small* appendices only:
- A polling-place checklist template aligned to DOJ ADA checklist headings (no measurements embedded).
- A translation provenance template (CSV) suitable for hashing and public release.


## Primary anchors

- EAC — Voting Accessibility (xref: eac_voting_accessibility)
- DOJ ADA — Voting and Polling Places (xref: ada_voting_and_polling_places_page)
- W3C — WCAG 2.2 Recommendation (xref: w3c_tr_wcag22)
- vote.gov — Voting with a disability (xref: vote_gov_guide_to_voting_disability)
