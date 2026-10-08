# Permissioning & Approvals (Permits, Licenses, Authorisations)

**Purpose:** make licenses/approvals/permits contestable and time-bounded so delay and discretion can’t silently govern.
**Person served:** a person seeking an approval (or harmed by one) who needs predictable timelines, reasons, and an appeal path—so permissioning isn’t arbitrary power.

**From-below:** This makes permits predictable and appealable so projects aren’t stalled or approved in the dark by invisible discretion.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-06` (Complexity), and `EXP-03` (Proof burden) by forcing permits/approvals into a short, receipted path with substitutes and deadlines (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** permit approvals/denials must be issued as `DRR-*` with a binding review/appeal lane (`AL-*`) and deadline enforcement (escalation + duty-to-decide) (`36`, `66`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** safe complaint/reporting channels for corruption, intimidation, and retaliatory inspections; protect applicants/complainants and monitor chilling (`83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**As-of & corrections:** decisions and receipts MUST state the as‑of basis (rules, data, releases) and MUST propagate corrections (reopen/undo downstream holds/penalties when upstream records change); do not strand people in stale status. (See `31-records-foi-and-government-memory.md`, `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)

**Proof burdens:** publish required evidence + least-burdensome alternatives; disclose “once-only” retrieval of state-held facts; ensure adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)

“Permissioning” is where governments turn rules into **case-by-case approvals**: building permits, business licences, zoning variances, environmental approvals, visas, grants/charters, inspections leading to stop-work orders, etc.

It is a high-risk governance surface because it combines:
- **discretion** (room for arbitrary decisions),
- **delay power** (queue control becomes leverage),
- **rent extraction** (fees, bribes, “facilitation”),
- **unequal treatment** (bias, favoritism, selective enforcement),
- **technical complexity** (standards and evidence can become paywalled/opaque).

This memo defines a **Minimum Viable Permissioning System (MVPS)** that keeps permissioning *legible, bounded, and appealable* without turning the archive into a sector-specific handbook.

**Uses:** municipal land-use + construction, national business licensing, environmental permits, safety inspections, regulator approvals, cross-border authorisations (where applicable).

**Anchor set (design evidence):**
- OECD Recommendation on Regulatory Policy and Governance (2012): see [BIB-OECD-RPG-0390].
- OECD Regulatory Enforcement and Inspections (2014) + Toolkit (2018): see [BIB-OECD-REI-2014]; [BIB-OECD-REI-TOOLKIT-2018].
- World Bank Global Indicators of Regulatory Governance (publication/consultation/RIA practices): [BIB-WB-GIRG]
- World Bank “Good practices for construction regulation and enforcement reform” (2013): see [BIB-WB-CONSTR-REG-2013].
- European Commission Better Regulation Guidelines (2021) + Toolbox (2023): see [BIB-EC-BETTERREG-GUIDE-2021]; [BIB-EC-BETTERREG-TOOLBOX-2023].

---

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Service journey design:** `47-service-catalog-and-access-journeys-register.md` (channels + assistance).

## Named tensions (design must surface these)
- **Risk control vs exclusion:** safety rules vs shutting people out.
- **Discretion vs arbitrariness:** case-by-case judgment vs unequal treatment.
- **Speed vs due process:** rapid approvals vs contestable decisions.
- **Uniform rule vs legitimate exception:** consistent standards vs contextual variance.

## A. The permissioning decision: should this be a permit at all?
Before creating (or keeping) a permit/licence/approval, apply a simple ladder:

1) **Publish a rule, then enforce ex post** (preferred when harms are low or easily remediated)  
- examples: routine registrations, low-risk business activity, low-risk construction changes

2) **Notification + random audit** (better than universal pre-approval for moderate risk)  
- requires a credible audit capability; links to inspections governance (OECD 2014/2018 anchors above)

3) **Tiered permits** (pre-approval only for high-risk classes; fast path for low-risk)  
- requires risk classification + time bounds

4) **Full permit with public record** (only when harms are high and irreversible, or standards are complex)  
- require stronger transparency + remedy + anti-corruption controls

**Anti-pattern:** universal pre-approval + opaque discretion + slow queues (“permissioning as rent”).

---

## B. MVPS — Minimum Viable Permissioning System (spec)
A permissioning system MUST provide, at minimum:

### 1) Public criteria and legal basis
- Each permit type MUST have:
  - a **Rule ID** (legal basis) and a short plain-language summary (see `25-legal-legibility-and-rule-inventory.md`),
  - a **`STD-*` ID** where technical standards apply (see `27-standards-and-technical-governance.md`),
  - explicit eligibility/decision criteria and required evidence.

### 2) Risk-tiering and “fast paths”
- MUST: classify permit types into a small number of risk tiers (e.g., low/medium/high).
- SHOULD: “fast path” for low-risk applications (standard forms; predictable timelines; minimal discretion).
- MUST: prohibit “discretion creep” (fast path cannot silently become slow path without a logged rule/standard change).

### 3) Time bounds and queue discipline
- MUST: publish statutory or charter time limits by permit type (including completeness checks).
- MUST: define what happens when deadlines are missed (typed outcomes):
  - **deemed approval** (only where safety allows),
  - **deemed denial with reasons** (forces appealable decision),
  - **automatic escalation** (supervisor review + public exception log).
- SHOULD: publish queue stats and variance (to detect “slow-walk” corruption).

### 4) Separation-of-duties (anti-bribery and anti-favoritism)
- MUST: log interactions; prohibit informal “off-record” decision channels.
- SHOULD: separate **plan review** from **inspection/enforcement** teams (reduce quid-pro-quo).
- SHOULD: randomized assignment / rotation for high-risk permit classes (where feasible).
- MUST: conflict disclosures for decision-makers on variances/exemptions (`22-public-integrity-and-procurement.md`).

### 5) Permit/Approval Register (PAR) — the legibility core
Permissioning MUST be auditable. Maintain a **Public Permit/Approval Register (PAR)** that conforms to the register pattern (`IOP-9`; see `70-interoperability.md`).

**Privacy rule:** publish what is needed for legitimacy and anti-corruption; redact personal data where appropriate; publish aggregates when individual records are sensitive.

**Minimum PAR fields (joinable)**
- Permit ID (stable; never reused)  
- Permit Type ID + risk tier  
- Owning unit (Unit ID)  
- Rule ID(s) (legal basis) + `STD-*` ID(s) (if applicable)  
- Coverage object (e.g., parcel/asset/service area ID where relevant)  
- Status + version (submitted / complete / approved / denied / appealed / withdrawn)  
- Key dates (submitted; completeness; decision; effective; expiry)  
- `AUTH-DRR` (decision receipt for approve/deny/variance; join rule in `70-...`)  
- For variances/waivers/exemptions: `AUTH-DRR` MUST be `DRR-TYPE: EXCEPTION` with bounds + expiry (see `85-waivers-variances-and-exceptions-discipline.md`).  
- Decision reason code (typed; not free-text only)  
- Reviewer/inspector unit (not necessarily person)  
- Links: appeal case ID (if any), relevant program ID (if this is a program gate), related contracts (if project-funded)

### 6) Reasons + remedy must be real (not performative)
- MUST: approvals/denials must provide **reasons** tied to criteria (and cite Rule/`STD-*` IDs).
- MUST: the person-facing explanation in the `DRR` MUST pass the comprehension test (what decided / why / what-next / by when) under `98-persons-path-and-accessibility-invariants.md` (in-language; usable offline).
- For denials based on missing documentation, the `DRR` MUST state what was missing, where to obtain it, the resubmission deadline, and whether the state could have obtained it (once-only default); offer assisted retrieval or explain why not.
- MUST: publish a “no wrong door” help + complaint intake for permits (including safe/confidential options where retaliation risk is plausible) (`08-...`, `36-...`, `83-...`).
- SHOULD: approvals/denials SHOULD issue a `DRR-*` receipt and the PAR entry SHOULD store it as `AUTH-DRR` (keeps reason-giving + deadlines + remedy joinable; see `31-...` and `70-...`).
- MUST: provide an appeal path with deadlines (see `08-remedy-and-grievance.md`).
- SHOULD: publish anonymized precedent library for high-impact permit types (improves consistency).

---

## C. “Silence is consent” (use carefully)
This tool can reduce rent-seeking and delay power, but it can also create safety risks.

**Rule:** use **deemed approval** only when:
- harm is low or reversible, AND
- standards are objective, AND
- audit/inspection exists to catch false filings.

Otherwise, prefer:
- deemed denial with reasons + fast appeal, or
- automatic escalation + public exception log.

---

## D. Failure modes (permissioning is where capture hides)
- **Queue as extortion:** long waits + informal “helpers” → bribes  
  - Mitigate: published SLAs, PAR visibility, variance dashboards, randomized assignment.
- **Selective enforcement:** inspections used against enemies  
  - Mitigate: risk-based inspection plans, published inspection criteria, appealable orders.
- **Variance laundering:** exemptions become the real rule  
  - Mitigate: publish variance register and reasons; require periodic review; tighten criteria.
- **Paywalled standards:** compliance requires buying documents  
  - Mitigate: incorporate-by-reference rules require public access (see `27-...`).
- **Shadow intermediaries:** unofficial fixers become the interface  
  - Mitigate: prohibit off-record routing; publish official assistance; log contacts.

---

## E. Minimal metrics (choose ≤10 total)
Prefer metric IDs from `03-metrics-and-evidence.md` packs.
- time-to-decision (median + 90p) by permit type / risk tier; plus variance ([LRR-4] / [REG-3])
- share of decisions with published reasons + Rule/Standard citations ([LRR-8])
- appeal rate and overturn rate by permit type (with reasons) ([LRR-4] / [REG-3])
- integrity signals: complaint concentration, anomalous fast-tracks, conflict disclosures completeness ([IPM-2] / [IPM-4])
- inspection targeting quality (risk-based coverage; false positive/negative proxies) ([REG-2] / [REG-3])

---

## F. Where to wire this
- **Municipal:** land-use, variances, building permits, business licensing (`20-municipal.md`)
- **Regulatory bodies:** enforcement + inspections + licensing (`13-regulation-utilities-and-soes.md`)
- **National:** whole-of-government licensing/authorisation discipline (`40-national.md`)
