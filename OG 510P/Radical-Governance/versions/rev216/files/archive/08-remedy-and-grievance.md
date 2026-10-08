# Remedy & Grievance (Legitimacy Requires Fixing Harm)

**Purpose:** ensure people can safely contest decisions and obtain relief—without needing lawyers, literacy, or institutional trust.

A system is not “rule-of-law” in practice if people cannot **challenge decisions** and get **timely, enforceable remedies**—especially where coercion or automation is involved.

**Anchor set:** see [BIB-UN-REMEDY-60147].

**Canonical interface:** `36-appeal-lanes-and-redress-registry.md` (ALR) defines how `AL-*` lanes are registered, versioned, and cross-walked.

**See also:** `66-justice-and-administrative-justice-governance.md` (courts/tribunals as auditable infrastructure).

**Accessibility invariant (persona test):** remedy systems MUST work for a person who is (a) low‑literacy/illiterate, (b) offline/no smartphone, (c) not fluent in the dominant language, (d) at retaliation risk, and (e) facing a time‑critical harm (eviction/detention/benefits cutoff/custody). If the remedy stack fails this test, it MUST be treated as a governance defect (see `98-persons-path-and-accessibility-invariants.md`).

## Kernel anchors (do not repeat)
- Person-facing invariants (no AI-only gate; non-reading options): `98-persons-path-and-accessibility-invariants.md` and service journeys `47-...`.
- Appeal lanes + fields (including collective filing): `36-...`.
- Systemic redress when harm is patterned: `76-...`.
- Records + publication integrity for decisions and rules: `31-...`, `53-...`, and `39-...`.
- Protective legibility / adoption dynamics (who loses discretion): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Speed of relief vs due process/accuracy (especially in crisis lanes).
- Confidentiality/safety for complainants vs public precedent/learning.
- Individual remedy vs pattern remediation (small harms can be huge in aggregate).
- Individual harms as pattern sensors: the point of legible harms is also to surface systemic patterns that require systemic redress and, where needed, rule/policy change (`76-...`, `41-...`, `88-...`, `28-...`).
- Accessibility/assistance vs fraud narratives and gatekeeping incentives.

---
## 0) Person-facing invariants (non-negotiable)
These are the minimum conditions for remedy to function in practice (see `98-persons-path-and-accessibility-invariants.md`).

- **Accessibility invariant:** remedy MUST work offline and under translation needs; it must be usable by a low‑literacy person with no internet and a time‑critical harm.
- **No wrong door:** any intake channel MUST either accept the filing or route it without losing deadlines, preserving a single tracking number.
- **Navigation duty (explain the receipt):** the institution that made the decision MUST provide a plain-language next-step explanation (in the person’s language/channel) and a guided route to the correct `AL-*` lane; “see the website” is not sufficient where rights or essentials are at stake.
- **Recourse can take different forms:** the contestation path may be a court/tribunal, an ombuds, a council, or a consensus process; but it MUST be discoverable, safe, and time-bounded enough that rights-affecting harms are not trapped in endless process.

- **Representation duty:** where the affected party cannot effectively contest (children, people under custody/control, severe disability), the system MUST support representative filings and SHOULD provide an automatic advocate/ombuds intake path for high‑stakes decisions (with conflict‑of‑interest controls).
- **Remedy people fear is not remedy:** if retaliation risk makes people afraid to file, the remedy system is failing; publish safe reporting options, representation options, and anti‑retaliation pathways (`83-...`, `98-persons-path-and-accessibility-invariants.md`).
- **Anonymous / confidential filing by default:** where feasible, offer an option to file without public identity disclosure (or via a representative). If identity is required for investigation, the lane MUST disclose what will be shared, with whom, and the safeguards; provide protected contact channels.
- **Delay is denial:** missed response deadlines MUST trigger defined outcomes (auto‑escalation / interim protection / deemed denial) rather than silence.

**Boundary (don’t oversell remedy):** remedy systems can correct **errors**, unlawful acts, and misapplication of rules. They cannot by themselves make an unjust rule generous or humane when it is being applied correctly. When correct application produces systematic harm, the appropriate path is **political change** informed by joinable evidence: participation/duty‑to‑respond (`ENG-*`), program evaluation (`PROG/EVAL/CLM`), and systemic redress (`76-...`).

**When institutional channels fail:** this memo assumes remedy lanes remain open enough to be used. When lanes are closed/captured and coercion is unconstrained, the archive can only specify a *floor* (preserve evidence/publication integrity and protect community continuity) and does not prescribe forms of non‑institutional resistance. A system that forces people there is failing by this archive’s own standards (see `04` [TM-31], `53-...`, `24-...`).


## A. Layered remedy stack (design goal: “easy first, enforceable last”)
1) **Front-door grievance**
- MUST: a clear intake channel (online + offline) with tracking number and response deadlines.
- MUST: for rights-affecting decisions, the notice/reasons MUST cite the legal basis (Rule IDs where available) and link to the public rules register (see `25-legal-legibility-and-rule-inventory.md`).
- SHOULD: provide a short **decision receipt** (one page / one screen) with a stable Decision ID (`DRR`), cited Rule IDs, any evidence/release IDs (e.g., `REL-*`), and the appeal lane (`AL-*`) / time limit.
- SHOULD: include a **receipt verification code** (QR/short code) so the holder can confirm the receipt exists (and retrieve the redacted `DRR` + `AL-*` lane) even when details must be protected. (See `31-records-foi-and-government-memory.md`.)

**Decision receipts:** canonical minimum fields live in `31-records-foi-and-government-memory.md` (Decision Receipt table). Any receipt should include `DRR-*`, cited `RULE-*` (as-of), ≥1 `RC-*`, relevant `REL-*` joins (when evidence matters), and at least one `AL-*` lane + deadline.

Anchor (reason-giving + effective remedy baseline): see [BIB-COE-GOODADMIN-2007], [BIB-EU-CHARTER-A41], [BIB-EU-CHARTER-A47] (plus [BIB-ICCPR] and [BIB-UN-REMEDY-60147]).
**Rule:** if a decision is enforced against someone, the receipt MUST exist (or a narrow, logged exception).


### Illegibility is itself harm (AL-LEG)
When required artifacts are missing (no receipt, no log, no cited rule), treat the absence as a **contestable incident**, not “nothing happened.”
- People MUST be able to file an `AL-LEG` complaint (legibility failure) that triggers a time‑bound response and an escalation path if the artifact is not produced.
- Default burden shift: if the state cannot produce the required receipt/log by deadline, oversight may presume noncompliance for interim protection (typed and logged) pending a merits review.
(See `36-appeal-lanes-and-redress-registry.md` and `32-oversight-institutions-and-follow-through.md`.)

- SHOULD: triage by risk (coercion, custody, benefits cutoff, housing, child welfare, immigration, high-stakes ADS).

2) **Ombuds / inspector general (independent review)**
- SHOULD: independent intake + investigation + public reporting.
- MUST: protection against retaliation for complainants and staff.
- See: `32-oversight-institutions-and-follow-through.md` (independence protections + follow-through loop).

3) **Administrative tribunal (fast specialized review) (`LAW-3`)**
- SHOULD: accessible to non-lawyers; published decisions; appealable.

4) **Courts (rights enforcement) (`LAW-2`)**
- MUST: enforceable remedies (injunctions, restitution/compensation, orders to disclose, contempt for noncompliance where appropriate).

---

## B. Remedies menu (keep small but explicit)
- **Stop / prevent:** injunction, stay, immediate protection order.
- **Fix decision:** reconsideration with reasons; reversal; new hearing; human review (for ADS).
- **Repair harm:** restitution, compensation, rehabilitation.
- **Change system:** policy update; training; removal of unlawful guidance; sanctions for misconduct.
- **Truth + learning:** public incident reports and after-action reviews (especially for coercion or algorithmic failures).

---

## C. “High-risk defaults”

**Automation default:** if an automated system materially influenced a decision, the person MUST receive a receipt that cites `ADS-*` (and `MOD-*` when material) plus `RC-*` reason codes and the relevant appeal lane `AL-*` (see `42-...`, `36-...`, `70-...`).

### 1) Coercion + custody
- MUST: independent serious-incident pathway (use of force, death/serious injury, torture/ill-treatment allegations).
- MUST: preservation of evidence + rapid external notification.
- MUST: coercive contacts issue a receipt and create joinable event logs: `DRR`/receipt cites `ENF-*` + `RULE-*` (as-of) + complaint lane `AL-*` (canonical `43-...`).
- Link to `05-public-safety-and-coercion.md` (`SAFE-1/2/4/5`).

### 2) Automated decision systems (ADS)
- MUST: meaningful explanation, right to human review, and appeal that can *actually* change outcomes.
- MUST: logging and auditability for contested decisions.
- Link to `06-digital-and-algorithmic-governance.md` (`IOP-5`).

### 3) Cross-border listings, sanctions, and watchlists
These systems are often **rights-affecting without local votes**. Minimum due process:
- MUST: notice that listing exists (unless a narrow, time-bound secrecy exception is justified).
- MUST: a **summary of reasons** and evidence-handling rules (what can be disclosed; how to contest).
- MUST: a time-bound **independent review** path with authority to recommend/require delisting.
- SHOULD: legal assistance for people who cannot navigate the process.
- MUST: publish aggregate stats (list size, delistings, average review time) to prevent “secret permanent punishment”.

Anchor: UN Security Council **Ombudsperson** model for delisting requests (ISIL/Al-Qaida list): see [BIB-UNSC-OMB]; procedure: see [BIB-UNSC-OMB-PROC].


---

## D. Anti-bottleneck design rules
- **Time-bound everything:** each layer needs deadlines and escalation triggers.
- **No-response is a defect:** missed deadlines should be treated as `AO-NORESP` events, triggering the lane’s published `NO-RESPONSE-RULE` (auto-escalation and/or interim protection); see ALR (`36-...`).
- **Secrecy exceptions are reviewable:** if a decision or record is withheld/classified, the refusal MUST be a joinable `DRR-KIND: REFUSAL` with typed legal basis, a non-sensitive reasons summary, **existence metadata**, and `AL-*` lanes; independent review must be able to inspect withheld material (in camera) and publish outcome summaries (see `31-...`; anchors: [BIB-COE-TROMSO], [BIB-TSHWANE-2013], [BIB-JOHANNESBURG-1995]).
- **No receipt / no effect (where feasible):** if an action is enforced against someone and the required receipt/log cannot be produced, treat that absence as a **procedural rights violation** that triggers an urgent lane (`AL-*`) and presumptive interim protection until the record is produced (or a narrow, logged exception is justified).
- **Publish patterns:** complaints should produce public “bug reports” on institutions (without doxxing).
- **Don’t overload courts:** tribunals and ombuds should absorb volume, courts should set rights standards.
- **Hostile UX is denial:** “dark patterns” and sludge that prevent filing, opting out, or understanding rights are a remedy failure surface; require measurement (burden budgets) and a fix path (see [BIB-OECD-DARKPATTERNS-2022]; `47-...`).


### D2. Missing required artifacts (legibility remedy)
A transparency system only works if **missing required artifacts are themselves contestable**.

**Rule:** every scope SHOULD provide a clear path to file “no receipt / no log / missing required record” complaints.
- The front-door channel (`AL-FRONT`) MUST accept these complaints and issue a review-result `DRR` that either:
  1) supplies the missing receipt/log (backfilled), or
  2) records a violation and triggers protective remedy, or
  3) documents a narrow, time-bound exception with legal basis and a follow-up deadline.
- For high-stakes harms, the default `NO-RESPONSE-RULE` SHOULD provide **interim protection** when the state cannot produce the required artifact in time.
- Oversight bodies SHOULD run **gap audits** (complaints vs logged events; spend vs contracts; denials vs receipts) and open `OFR-*` cases when the absence pattern suggests dark enforcement or administrative domination (see `32-...`).

---


### D6) Systemic harms (pattern-of-practice) are handled as oversight cases
- **Collective filing SHOULD be supported** where appropriate: allow a community, organization, or affected class to initiate a single complaint that represents shared harm. If collective filing is not available, publish the substitute mechanism (watchdog standing, representative complaints, class action, or pattern‑based redress intake). The ALR schema (`36-...`) MUST disclose whether collective filing is supported.

Individual appeals can’t fix recurring harm. When grievance spikes, `AO-NORESP` rises, or disparities/patterns appear, the unit SHOULD open a scoped `OFR-*` systemic case with deadlines, interim protections (where needed), and an evidence-based closure rule. See `76-systemic-redress-and-pattern-remediation.md` and `55-oversight-findings-and-response-register.md`.


## E. Minimal metrics
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- time-to-remedy (median + 90p) by case type (incl. fast lane) [LRR-4]
- accessibility of remedy channels (languages, disability access, offline access) [LRR-9]
- overturn/reversal rate and outcome mix (`AO-*`) by lane (`AL-*`) and reason (`RC-*`); for ADS-involved decisions also track appeals [LRR-10] / [DAG-3]
- compliance with tribunal/court orders (on-time share + reason codes) [LRR-6]
- retaliation incidents affecting complainants/whistleblowers [IPM-4]
