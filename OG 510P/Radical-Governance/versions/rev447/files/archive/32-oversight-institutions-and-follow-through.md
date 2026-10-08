# Oversight Institutions & Follow‑Through (Audit, Ombuds, Integrity)

**Purpose:** specify oversight bodies and **follow‑through duties** so findings turn into correction (not theatre) and stay usable from below (`98`).
**Person served:** a person harmed by abuse, corruption, or neglect who needs oversight to compel fixes and protect against retaliation—not just publish reports.

**From-below:** This makes oversight land as action—findings, deadlines, responses—so reports don’t die on shelves while harm continues.
**EXP pointer:** counters `EXP-07` (Indifference) by making findings bindable and follow-through measurable (`98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** oversight is defined by binding hooks (duty-to-respond deadlines, corrective orders, budget/authorization triggers, and/or court-review backstops). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** independent intake + protected disclosures + retaliation remedies; monitor and publish chilling/retaliation signals (`83`, `03`, `77`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** oversight findings MUST state evidentiary basis + standard; where key evidence is state-held, overseen bodies must produce it (and receipts disclose gaps); contested findings route to `RC-*` + an `AL-*` lane (`44`, `52`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


“Checks and balances” fail in practice when oversight is **starved**, **captured**, or **non-binding** (findings disappear into political fog). This memo defines a compact *oversight stack* and a *follow‑through loop* that works across scopes.

**Anchor set (start here):**
- See: [BIB-INTOSAI-P10]; [BIB-INTOSAI-P1]; [BIB-ISSAI-300-2019]; [BIB-ISSAI-3000-2019]; [BIB-VENICE-OMB-2019]; [BIB-UN-PARIS-PRINC-48134].

## Kernel anchors (do not repeat)
- `01-principles.md` (tensions)
- `98-persons-path-and-accessibility-invariants.md` (person’s path)
- `83-whistleblowing-and-protected-disclosures.md` (protected disclosures)
- `08-remedy-and-grievance.md` (remedy)
- `99-protective-legibility-and-adoption-dynamics.md` (protective legibility)
- `73-assurance-case-and-governance-safety-case.md` (assurance cases)

## Named tensions (design must surface these)
- Publish enough to create contestable power without exposing witnesses/complainants to retaliation.
- Default to **joinable summaries + redaction discipline + review clocks** (`77`, `83`) rather than silence.
- Structural independence vs institutional culture: even when oversight is structurally independent, constraints on authorized violence depend on institutional willingness to use safeguards rather than evade them; the archive can design safeguards, not culture. (See `101-claude-rev142-normative-requirements.md` (NR-17).)

---

## A. Treat oversight as a closed loop (not a “watchdog” slogan)
### Countervailing power is part of the design (not an externality)
Transparency and oversight reports do not “work” unless someone can *use* them.

**Minimum conditions (operational):**
- **Binding hooks:** oversight MUST have at least one hard lever (duty‑to‑respond with deadlines, enforceable corrective orders, budget/authorization triggers, or court‑review backstop). Otherwise “oversight” is advisory speech, not countervailing power.
- **Resourcing:** oversight bodies MUST have protected budgets/staff and control over their own publication pipeline.
- **Standing:** defined actors (ombuds, unions, civil society orgs, accredited journalists) SHOULD have standing to initiate reviews/complaints where individual filing is unsafe or infeasible.
- **Usable outputs:** “publication” must include an accessible summary + joinable IDs (`OFR-*`, `DRR-*`, `REL-*`), not just a large PDF.
- **Safety:** retaliation protections and secure channels for witnesses/complainants are part of follow‑through, not an optional add‑on.

**Goal:** convert findings into verified fixes.

**Minimum loop**
1) **Discover** (audit/investigation/complaints)
2) **Publish** (redacted where necessary)
3) **Respond** (duty‑to‑respond with an action plan)
4) **Remediate** (implementation with deadlines)
5) **Verify & close** (independent verification; closure criteria)

**Rule:** if a body can publish findings, the governed entity MUST have a **time‑bound duty to respond** and the public MUST be able to see whether issues were closed.

---

### OFRR (joinable follow‑through)
Define follow‑through as a public register, not a narrative.

- **Canonical spec:** `55-oversight-findings-and-response-register.md` (minimum schema, lifecycle states, and escalation hooks).
- **Rule:** oversight outputs SHOULD be referenced by `OFR-*` in decision receipts (`DRR-*`) and linked to evidence releases (`REL-*`) and remedy lanes (`AL-*`) where applicable.

## B. Minimum Viable Oversight Stack (MVOS)
Rather than proliferating agencies, define a small stack by *function*.

### Core (should exist at municipal+; national MUST)
1) **External audit (SAI / audit office)**
- mandate: financial + compliance + (optionally) performance/value-for-money
- outputs: audited accounts; thematic audits; recommendation tracking

2) **Ombuds / complaints reviewer (low-cost remedy)**
- mandate: maladministration, service failures, procedural justice
- outputs: case resolutions + systemic “pattern reports”

3) **Integrity investigation / inspector general function**
- mandate: corruption, serious misconduct, conflicts, procurement fraud
- outputs: investigations + referrals + systemic risk findings

### Optional add-ons (scope-dependent)
- **NHRI (rights monitoring)** — typically national; may be regional in federations.
- **Independent election administration** — where elections occur.
- **Independent fiscal institution** — for forecasting/costing discipline.
- **Data protection / competition / sector regulators** — where market power or sensitive data are central.

**Design rule:** new oversight bodies SHOULD only be created if they cover a distinct failure mode *and* can be made independent *and* the follow‑through loop is in place.

---

## C. Independence protections (portable)
Independence is not a vibe; it is *appointment + tenure + budget + access*.

**MUST (all core oversight bodies)**
- **Appointment transparency:** published criteria; public shortlist; conflict disclosures.
- **Removal for cause only:** narrow grounds; recorded reasons; reviewable.
- **Budget protection:** formula or multi-year floor; cannot be retaliatorily cut mid‑investigation.
- **Access to records:** statutory right of timely access (including contractors, where public funds or delegated authority is involved).
- **Publication default:** publish findings with narrow, typed redactions.

**SHOULD**
- **Plural appointment pathway:** e.g., mixed supermajority + independent panel to reduce single‑party capture.
- **Cooling-off and revolving door limits** for oversight leadership.

Anchors for these protections appear in INTOSAI‑P 1/10 (audit independence) and the Venice Principles (ombuds independence and mandate).

## C2. Oversight ecosystem (press, civil society, and complainant support)
Institutional oversight works better when the *public oversight ecosystem* is not starved or chilled.

**MUST**
- keep FOI/RTI **fees low/capped**, publish deadlines, and make denials typed + appealable (see `31-...` and [BIB-COE-TROMSO]).
- protect whistleblowers and provide safe reporting channels (see `83-...` and anchors [BIB-EU-WHISTLE-2019], [BIB-COE-WHISTLE-2014], [BIB-UNODC-REPORTINGPERSONS-2015]).
- protect complainants against retaliation (including in service/benefit systems) and make retaliation itself contestable (log as a case where feasible).

**SHOULD**
- provide basic **navigation help** (ombuds/legal aid) for complex remedy lanes so rights exist in practice.
- enable accredited researchers/auditors to access protected data in secure settings for replication and disparity testing (privacy‑preserving; purpose‑limited).
- publish “evidence packs” for major public decisions so third parties can contest reasons and detect omissions.

---

## D. Follow‑through protocol (stop “audit theatre”)
### 1) Duty to respond
**Dead-man’s switch (anti-theater):** missed response deadlines MUST trigger a deterministic escalation (not discretionary shame). When a response due date passes, the OFRR entry is flagged as non‑response and the next escalation rung (hearing → bounded holdback → referral) is automatically initiated or scheduled under a published rule.

- MUST: every published finding requires a **written response** within a fixed window (e.g., 60–120 days) stating:

  - accept / partial / reject (with reasons)
  - actions, deadlines, owners
  - required resources (if any)

### 2) Public tracking
- MUST: publish status and closure criteria; “implemented” claims require evidence.
- SHOULD: legislative hearing or council session for high-severity findings.

### 3) Escalation ladder
- SHOULD: repeated noncompliance triggers:
  1) mandatory public hearing
  2) budget holdback on the affected program (bounded)
  3) referral to prosecutor / tribunal / court (as appropriate)

**Rule:** escalation MUST be typed and linked to the legal basis (`RULE-*` IDs where available).

---

## D2. Legibility-gap audits (treat absence as a signal)
Artifact discipline is only enforceable if *missing artifacts* create an auditable trail.

**Pattern:** open a typed oversight case when statistical or administrative signals suggest “dark government”:
- complaints/surveys show high coercive contact, but `ENF-*`/`DRR-*` logs are low;
- significant spending occurs without matching `CON-*` records;
- denial volumes rise without corresponding receipts or reason codes.

**OFRR practice:** create `OFR-KIND: CASE` with `CASE-TYPE: LEGIBILITY-GAP`, publish the detection method (at a high level), require a remediation plan with deadlines, and verify closure via sampling.

This makes “nothing happened” contestable: absence becomes a joinable object in the same follow-through loop as other findings.

**Detection tactics (keep cheap):**
- **Randomized sampling** (“mystery shopper” service requests; spot-check receipts vs. outcomes).
- **Reconciliation checks** (payments↔contracts↔deliverables; denials↔appeals; enforcement contacts↔complaints).
- **Whistleblower intake + safe disclosure** (with optional *bounded* integrity bounties for verified high-impact omissions, where lawful).
- **Synthetic test cases** for ADS-driven processes (submit controlled inputs to validate reason codes, deadlines, and recourse behavior).
- **Self-report + safe harbor:** maintain a channel where units/vendors can file correction receipts for artifact failures (missing logs, wrong bases, data errors) and earn reduced sanctions for fast correction—while repeat self-reports trigger deeper audits (`ACC-8`).

**Empirical note (why randomization matters):** randomized audits/monitoring have shown deterrence and leakage-reduction effects in field settings, and public disclosure of audit findings can change political incentives by informing voters (see [BIB-OLKEN-2007]; [BIB-FERRAZFINAN-2008]).

**Assurance practice (make control failures predictable):**
- publish a lightweight **registry conformance report** (quarterly/annual): % decisions with `DRR`, % denials with `RC-*` + `AL-*`, % deadlines met (and `AO-NORESP` logs where not), % services with published burden budgets, % core registers with “as-of” access.
- run periodic **adversarial drills** (“governance red‑teaming”): attempt to execute a rights-affecting action *without* producing the required artifacts, or to sabotage remedy by delay, and measure detection + escalation time.
- treat “artifact integrity” as part of assurance: checksum manifests + mirrors for core registers (see `31-...`).

## D3. Participation‑integrity cases (stop consultation capture)

Where public consultation is online (or high‑volume), it is vulnerable to **bot floods, identity theft, and organized astroturf** that manufacture the appearance of consent. Treat this as a governance integrity issue, not a PR dispute.

**Pattern:** open an `OFR-*` with `OFR-KIND: CASE` and `CASE-TYPE: PARTICIPATION-INTEGRITY` when there is credible evidence of manipulation *or* when an `ENG-*` process fails to publish a required provenance summary.

**Minimum case outputs**
- a public **provenance summary** (join to the `ENG-*` entry; usually a `REL-*` release) describing dedupe/clustering and any verification sampling;
- a typed remediation plan (platform controls, sponsor disclosure enforcement, re‑run or re‑weighting policy);
- a corrective `DRR` for any material decision that relied on manipulated inputs (or a recorded justification for why not).

Anchors: [BIB-PEW-FCC-COMMENTS-2017]; [BIB-STANFORD-FILTERINGBOTS-2017]; [BIB-NYAG-FAKECOMMENTS-2021]. Canonical participation register: `41-...`.

## E. Oversight Files & Responses Register (OFRR)
To prevent oversight from disappearing into PDFs, maintain a small public register conforming to `IOP-9`.

**Minimum:** a machine-readable feed + human view.

### OFRR — minimum fields
- **OFR ID** (stable)
- **OFR kind** (`CASE` / `FINDING`)
- **Issuing body** (Unit ID; appears in competence ledger)
- **Case/finding type** (audit / ombuds pattern / investigation / evaluation / inspection / serious incident / other)
- **Subject unit(s)** (Unit IDs)
- **Trigger joins** (for `CASE`: linked `ENF-*` / `DRR-*` / `EMR-*` / `CMP-*` as applicable)
- **Linked objects** (`RULE-*` IDs, `PROG-*` IDs, `CON-*` IDs, `PAR-*` IDs, `EMR-*` IDs, etc.)
- **Severity** (small ordinal scale)
- **Publication date** + redaction basis (if any)
- **Response due date** + link to response
- **Action plan** (owners + deadlines)
- **Status** (see lifecycle states)
- **Closure verification** (who verified + date)

**Recordkeeping:** preserve underlying decision records and evidence links (see `31-records-foi-and-government-memory.md`).

---

## F. Minimal metrics (portable)
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- audit/oversight **closure rate** within 12/24 months [IPM-5]
- median time from finding → published response (new; can be added as a local derivative of [IPM-5])
- repeat findings rate (same issue reappears within 24 months)
- ombuds case resolution time and systemic pattern rate [LRR-4]
- substantiated misconduct/corruption cases with outcomes (bounded, privacy-preserving) [IPM-4]
