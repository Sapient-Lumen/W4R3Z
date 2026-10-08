# Public Health & Biosecurity Governance (Outbreaks as a Cross-Scope Interface)

**Stack relation:** use `291-public-health-preparedness-and-biosecurity-routing-guide.md` for the canonical route across the public-health / preparedness / biosecurity cluster. This memo is the canonical public-health governance front door; `234` is the preparedness/response operating specialization; `192` is the research/lab biosecurity extension; `165` handles the general emergency-powers rails neighbor when the issue is not health-specific; `61` handles communication, correction, and public-guidance integrity.

**Purpose:** enable protective health action while keeping emergency power bounded, logged, and socially trusted.

**Person served:** A person seeking care or protection during an outbreak, especially those with low trust or limited access, who needs timely, non‑discriminatory services and contestable restrictions.

**From-below:** This makes outbreak decisions explainable and reviewable so emergency measures protect people without becoming unaccountable control.

**EXP pointer:** counters `EXP-02` (Waiting) and `EXP-05` (Fear) by forcing emergency health measures into bounded, contestable interfaces with safe reporting (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).

**Authority:** restrictions and emergency measures must be grounded in explicit legal basis and receipted (`DRR-*`/`EMR-*`), with an independent binding review lane and duty-to-respond (`23`, `45`, `66`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** safe reporting for frontline staff and communities (incl. discrimination/abuse); protect complainants and publish chilling indicators (`83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**As-of & corrections:** decisions and receipts MUST state the as‑of basis (rules, data, releases) and MUST propagate corrections (reopen/undo downstream holds/penalties when upstream records change); do not strand people in stale status. (See `31-records-foi-and-government-memory.md`, `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)

**Proof burdens:** publish required evidence + least-burdensome alternatives; disclose “once-only” retrieval of state-held facts; ensure adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)

Public health crises are where polycentric governance is most visibly tested: **spillovers ignore boundaries**, evidence shifts fast, and legitimacy can collapse if measures feel arbitrary or unreviewable.
This memo defines a compact **Minimum Viable Public Health Governance Spine (MVPHGS)** using the archive’s existing interfaces (`REL-*`, `DRR-*`, `RULE-*`, `AL-*`, `EMR-*`, `CON-*`, `AST-*`, `OFR-*`, `PROG-*`).

**Anchor set (start here):**
- International Health Regulations (IHR) (2005) text (as amended; current since 19 Sep 2025): [BIB-WHO-IHR-TEXT-2025].
- IHR amendments context + entry into force (incl. “pandemic emergency” alert level): [BIB-WHO-IHR-AMEND-EIF-2025]; [BIB-WHO-IHR-AMEND-QA].
- WHO Pandemic Agreement (WHA78.1, adopted 20 May 2025; PABS annex pending): [BIB-WHO-PA-2025]; [BIB-WHO-PA-QA-2025].
- Surveillance system design exemplars (EU/EEA): [BIB-ECDC-SURV-FRAMEWORK-2025]; [BIB-ECDC-WBS-FRAMEWORK-2025].

**Primary threats:** [TM-4] epistemic failure, [TM-18] exception entrenchment, [TM-15] targeting/surveillance abuse, [TM-6] administrative overload, [TM-5] legitimacy collapse.

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Person-facing access + remedy under crisis: `98-persons-path-and-accessibility-invariants.md`, `08-remedy-and-grievance.md`, `36-...`.
- Service standards (waiting is harm; triage tiers; no digital-only gate): `82-service-standards-and-minimum-service-guarantees.md`, `47-...`.
- Emergency measures still require receipts + sunsets: `23-...`, `45-emergency-measures-register.md`.
- Records + publication integrity (no silent edits; “as‑of” access): `31-...`, `53-...`.
- Community continuity + serious-incident independence: `24-mutual-aid-and-serious-incident-protocol.md`, `10-micro-local.md`.

## Named tensions (design must surface these)
- **Speed + uncertainty vs due process + contestation** (fast action, reviewable reasons)
- **Legibility vs privacy/safety** (publish methods + aggregates; avoid targeting surfaces)
- **Cross‑border coordination vs local legitimacy** (IHR/PA obligations without arbitrary domestic power)
- **Population benefit vs concentrated harm** (the tail; protect vulnerable groups)

---

## 1) The MVPHGS pipeline (what “ideal” looks like operationally)
Treat response as a pipeline that emits **joinable public artifacts**:

1) **Situational awareness is publishable**
 - publish surveillance and capacity signals as `REL-*` releases (methods + revision logs) (`51-...`, `26-...`).
 - publish uncertainty (intervals, caveats) and version changes; no silent overwrites.

2) **Triggers are rules (not vibes)**
 - publish the *trigger rubric* as `RULE-*` (what metrics move the system between response modes).
 - major trigger flips emit `DRR-*` receipts citing the rubric and the `REL-*` baselines used.

3) **Measures are bounded and contestable**
 - measures live as `RULE-*` instruments (orders, guidance with legal effect, mandates), and each rights-/resource-affecting measure emits a `DRR-*` with:
 - reason codes (`RC-*`, including `RC-PH-*` where relevant),
 - cited `REL-*` evidence,
 - and the applicable remedy lanes (`AL-*`).
 - exceptional powers are logged in `EMR-*` episodes (`45-...`).

4) **Money and logistics stay auditable under stress**
 - emergency procurement still lands in `CON-*` (and links to `EMR-*` where applicable) (`38-...`, `22-...`).
 - stockpiles and critical assets are `AST-*` and have an auditable replenishment plan (`48-...`).

5) **Oversight closes the loop**
 - open an `OFR-*` entry early for high-salience response episodes (state `OPEN`, `OFR-KIND: CASE`) and close via verified action plans (`55-...`, `32-...`).
 - run an `EVAL-*` after-action evaluation (what worked, what didn’t, what changed).

---

## 2) Surveillance & releases (make reality legible)
### 2.1 Minimum `REL-*` releases to publish (context-specific)
- **Transmission & severity signals:** cases/positivity (if used), syndromic indicators, hospitalization/ICU occupancy, deaths (with revision notes).
- **Health system capacity:** staffed beds, critical staffing shortage metrics, queue/deferral signals (link to `[CAD-2]` loops for queue time discipline).
- **Intervention coverage:** vaccine/therapeutic uptake, test turnaround times, outreach distribution metrics (equity slices).

**Release discipline (non-negotiable):**
- methods + definitions are pinned to the release (`REL-METHOD`); revisions emit a new `REL-*` with a diff note (`51-...`).
- publish suppression rules (privacy, small-n) and what gets redacted/aggregated (`33-...`).
- if using newer signal types (wastewater, genomic), publish the standard/baseline used (`STD-*`) and sampling caveats (see exemplars: [BIB-ECDC-WBS-FRAMEWORK-2025]).

### 2.2 Cross-border alert mapping
When a response is linked to a global or regional alert (e.g., IHR PHEIC / “pandemic emergency”), record:
- the alert classification and date in the `EMR-*` **Cross-border notifications** field (or a linked `DRR`),
- any notification obligations and domestic implementing unit(s),
- and any deviations/opt-outs where allowed by the governing instrument.

(Anchors: [BIB-WHO-IHR-AMEND-QA], [BIB-WHO-IHR-AMEND-EIF-2025].)

### 2.3 International support & financing (make solidarity auditable)
Outbreaks fail when **money, commodities, and logistics** become opaque patronage. Treat cross-border support as a joinable interface:

- **Declare the support channel** (grant/loan/in-kind) and the eligibility logic as a `RULE-*` or program note linked from `REL-*` releases.
- Record disbursements and allocations as `PROG-*` entries that join to procurement (`CON-*`) and stockpiles (`AST-*`).
- Publish minimum transparency: recipient, purpose, unit costs where safe, delivery milestones, and a correction lane (no silent backfills).

Use global financing as *capacity-building*, not only crisis response; the Pandemic Fund is a canonical reference point for how hosted multi-donor financing is structured (trustee + governance + technical review). (Anchors: [BIB-PANDEMICFUND-HUB], [BIB-WB-PANDEMICFUND-FIF].)

### 2.4 Opt-outs, reservations, and “club” coordination (design for partial participation)
International health law is **polycentric**: instruments can enter into force with reservations/rejections, and major actors may refuse specific amendments or agreements. This memo assumes **variable geometry** and designs for it:

- Treat international obligations as *inputs* to domestic `RULE-*` and `EMR-*` entries, not as a substitute for domestic legality.
- Publish a **Participation Ledger** for major instruments: status (party / not party / reservation / rejection), date, and domestic implementing authority.
- When global consensus fails, define **minimum interoperable commitments** (a “club floor”): data sharing formats, verification, and mutual assistance protocols that can operate among willing parties without coercing non-parties.

Recent examples: the United States publicly rejected the 2024 IHR amendments and the 2025 Pandemic Agreement, illustrating why governance must remain functional under partial buy-in. (Anchors: [BIB-REUTERS-US-IHR-REJECT-2025], [BIB-REUTERS-US-PA-REJECT-2025].)

---

## 3) Measures & orders (rights-safe, reviewable)
### 3.1 Response modes (recommendation)
Define a small set of **response modes** (e.g., *Green / Amber / Red / Emergency*) and publish:
- what triggers each mode (`RULE-*`),
- what measures are allowed in each mode (and which require additional authorization),
- and the default review cadence + sunset rules (tie to `EMR` renewal discipline when exceptional).

### 3.2 A minimal receipt for a public-health measure (`DRR-*`)
For any material restriction/mandate/allocation decision, the `DRR` SHOULD include:
- **Person-facing usability:** where the measure binds a specific person (isolation/quarantine, denial of access, denial of scarce treatment), the notice/receipt MUST satisfy the comprehension + accessibility invariants (plain language, translation, disability access) and include a safe, low-friction path to contest or request accommodation. For minors or people who cannot self-advocate, trigger representation duty. (`98-persons-path-and-accessibility-invariants.md`, `31-...`, `36-...`)
- legal basis (`RULE-*` as-of),
- evidence (`REL-*`),
- reason code(s) (use `RC-PH-*` for common cases),
- the balancing test used (if any),
- impacted services (`SRV-*`) and continuity-floor checks for `ESS-1`,
- and a clear contestation path (`AL-*`).

---

## 4) Scarce resource allocation (vaccines, beds, therapeutics)
Scarcity is where legitimacy breaks fastest. The governance move is **pre-commitment + auditable exceptions**:

- publish the allocation policy as a `RULE-*` instrument *before* peak scarcity where possible.
- publish the operational implementation as a `DRR-*` (who runs it, what discretion exists, what logs exist).
- when using scoring/priority systems, record them as:
 - an **algorithmic decision system** (`42-...`) if automated, and/or
 - a published rubric with appeal lanes if manual.

Use `RC-PH-002` for scarcity allocation and require independent review for denials with high harm risk.

---

## 5) Public health data governance (don’t turn health into surveillance)
Public health relies on sensitive data. “Because emergency” is not a lawful basis by itself.

- Use `33-data-protection-and-personal-data-governance.md` as the baseline.
- Publish the **data purpose/retention table** for outbreak surveillance (purpose, fields, retention, sharing, safeguards).
- For high-risk data uses (location tracing, cross-agency linkage), require:
 - a `DRR-*` citing the lawful basis + safeguards,
 - an `AL-*` lane for correction/objection where feasible,
 - and an oversight plan (`OFR-*` spot checks).

Use `RC-PH-003` for public-health lawful-basis invocations and require sunset/retention discipline.

---

## 6) Communications & correction discipline (fight misinformation by being auditable)

- If chatbots or AI-mediated hotlines are used as the front door to public-health guidance or eligibility/allocation, register them (`ADS-*`) and treat rights-affecting outputs as determinations that must emit/point to a `DRR-*` with `RULE/RC/AL` (see `42-...`, `06-...`).
A response’s credibility depends on visible correction, not perfection.

- Treat official guidance bulletins and major advisories as `REL-*` releases (versioned) with:
 - “what changed and why” notes,
 - links to the `REL-*` evidence releases used,
 - and a correction lane if factual errors are alleged (a lightweight `AL-*` or ombuds intake).
- When retracting or materially changing guidance, issue a `DRR-*` (or a correction `DRR-TYPE: INTEGRITY`) with `RC-PH-004` and link the old/new `REL-*`.

(See correction discipline in `37-claims-evidence-and-update-discipline.md`, integrity tooling in `53-...`, and the communication spine in `61-public-communication-and-information-integrity.md`.)

---

## 7) Failure modes (design against)
- **Policy-by-dashboard with no method notes** → require `REL-METHOD` and revision logs (`51-...`).
- **Ruleless discretion (“we had to”)** → require `RULE-*` trigger rubric + `DRR-*` for flips and major measures.
- **Emergency powers normalize** → fixed sunsets + rising renewal thresholds + `EMR` closure artifacts (`45-...`, [TM-18]).
- **Health becomes surveillance** → purpose/retention publication + independent audits + time-bounded exceptional linkage permissions (`33-...`, [TM-15]).
- **Procurement chaos** → all awards still in `CON-*` with conflict controls; stockpile audits (`22-...`, `38-...`).
