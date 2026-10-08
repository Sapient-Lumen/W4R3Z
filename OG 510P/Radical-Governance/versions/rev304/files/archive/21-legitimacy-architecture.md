# Legitimacy Architecture (How Decisions Gain “Rightful Authority”)

**Purpose:** define legitimacy as lived contestability (receipts + remedy + follow‑through), not mere procedural aesthetics.
**Person served:** anyone subject to a consequential decision who needs “legitimacy” to cash out as lived contestability (receipt, reasons, and an effective remedy).

**From-below:** This turns “legitimacy” into enforceable rights—receipt, reasons, remedy, and follow‑through—so you’re not fobbed off with procedural theater.
**EXP pointer:** counters `EXP-01` (Opacity), `EXP-06` (Complexity), and `EXP-07` (Indifference) via receipts + reasons + remedy (`98-persons-path-and-accessibility-invariants.md`).

This memo describes how to **compose** the decision/legitimacy modules in `02-design-toolkit.md` into a *small, reliable pipeline* across scopes.

**Goal:** a system where (1) power is contestable, (2) reasons are public, (3) minorities have enforceable protections, and (4) high-stakes decisions must pass through *more than one legitimacy generator*.

## Kernel anchors (do not repeat)
- `01-principles.md` (tensions + adoption dynamics)
- Decision receipts (person-facing) default to `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- `98-persons-path-and-accessibility-invariants.md` (person’s path)
- `83-whistleblowing-and-protected-disclosures.md` (retaliation discipline)
- `99-protective-legibility-and-adoption-dynamics.md` (protective legibility)
- `32-oversight-institutions-and-follow-through.md` (follow‑through)
- `73-assurance-case-and-governance-safety-case.md` (assurance cases)

## Named tensions (design must surface these)
- Legibility vs safety.
- Transparency vs retaliation.
- Speed vs due process.
- Joinability vs justice.
- Ideal legitimacy stacks vs **material floor** (revenue, literacy/translation, physical safety, time/subsistence).
- **Design rule:** treat tension‑management (redaction, safe channels, representation, deadlines, countervailing power) as part of legitimacy, not as an optional “implementation detail.”

**Power map invariant (legitimacy is about power, not paperwork):** any legitimacy pipeline MUST name (a) the discretionary **chokepoints** and enforcement edges, (b) who can override whom (formal and informal), and (c) the countervailing actors who can force closure when the pipeline fails (appeal lane, ombuds/audit, court, or equivalent).
Note: whenever a decision requires a `DRR` artifact, include ≥1 portable **Reason Code** (`RC-*`) and an **Appeal Lane** (`AL-*`, see ALR `36-...` and `52-reason-codes-registry.md`) alongside the cited Rule IDs so appeals and audits can aggregate patterns. For review outcomes, include `AO-*` outcome code(s) and link to the challenged `DRR`.

**Person’s Path check (legitimacy as lived experience):** a legitimacy pipeline is non‑credible if the affected person can’t understand the decision or safely use the remedy. Any rights-/resource‑affecting decision route MUST satisfy the `98` accessibility invariants (receipt comprehension; “no wrong door” routing; representation duty where self‑advocacy is unrealistic). Treat fear/retaliation and delay as defects, not user error. See `98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`, and [TM-29].

**Deliberation anchor:** for comparative design/case evidence on representative deliberative processes, see [BIB-OECD-DELIBWAVE-2020] and [BIB-OECD-DEL] (operational design invariants: `88-deliberative-institutions-and-sortition.md`; for long-horizon duties: `89-intergenerational-governance-and-future-obligations.md`).

---

## 1) Legitimacy generators (the small set)
Legitimacy is produced by **processes**. The core generators are:
- **Election/representation** (`DEC-1`, `DEC-5`) — allocates authority at scale.
- **Deliberation/sortition** (`DEC-2`) — improves quality and trust for complex, long-horizon, or polarized issues.
- **Bounded allocation participation** (`DEC-3`) — local preference revelation with limited downside.
- **Direct democracy (guard-railed)** (`DEC-4`) — agenda power, but high manipulation risk.
- **Rights + rule of law constraints** (`LAW-1..5`) — legitimacy through *limits* (what majorities cannot do).
- **Expertise with transparency** (`CAP-7`, `OPEN-4/5`) — legitimacy through competence + reasons.
- **Remedy** (`08-remedy-and-grievance.md`) — legitimacy through correction (errors are expected; fixes are mandatory).

**Rule of thumb:** high-impact decisions MUST route through **at least two** generators (e.g., elected + deliberative; elected + rights review; elected + independent costings).

Anchors (practice principles / standards):
- OECD *Good Practice Principles for Deliberative Processes* — see [BIB-OECD-DEL].
- Venice Commission *Code of Good Practice in Electoral Matters* — see [BIB-VENICE-ELECT].
- International IDEA *Electoral System Design*: see [BIB-IDEA-ESD].

---

## 2) Decision typing (route the decision to the right channel)
Classify proposals before choosing a decision path:

1) **Routine operations** (service levels, hiring rules, maintenance):
- Default: elected executive + professional administration (`CAP-1/6`) with transparency (`OPEN-1`).
- Override: tribunal/ombuds if rights or fairness complaints arise (`LAW-3`, `ACC-3`).

2) **Distributional budgets** (who gets money/benefits):
- Default: elected budgeting + readable accounts (`CAP-2`).
- Add: bounded participatory budgeting for local capital envelopes (`DEC-3`).
- Add: independent fiscal scrutiny for major commitments (`CAP-4`).

3) **Rights-limiting / coercive** (policing, detention, surveillance, bans):
- MUST: strict legality + published doctrine + independent oversight (`SAFE-*`, `LAW-1/5`).
- MUST: accessible remedy and after-action reporting.
- SHOULD: deliberative review for policy-level shifts (not incident review) (`DEC-2`).

4) **Long-horizon / irreversible** (zoning frameworks, mega-projects, constitutional change, ecological budgets):
- SHOULD: deliberative process with duty-to-respond (`DEC-2`).
- SHOULD: “future impact statement” and review trigger (`DEC-6`).
- MUST: publish assumptions and alternatives (`OPEN-5`).
- If the proposal changes a top-tier instrument (constitution/charter/treaty), use integrity-grade change discipline (`DEC-9`; `58-constitutional-change-and-amendment-discipline.md`).

5) **Boundary / responsibility changes** (merger, split, annexation, mandate transfers):
- MUST: MV-BRP process (`17-jurisdiction-formation-and-boundaries.md`) + deliberative phase for affected publics (`DEC-2`).

6) **Inter-jurisdiction commitments** (shared services, corridors, standards):
- MUST: compact discipline + auditability (`19-compacts-and-cooperative-governance.md`).

7) **Emergency / exception governance** (states of emergency, rapid restrictions, escape clauses):
- MUST: typed and time-bounded emergency declaration; renewal votes; independent review stays on; publish an Emergency Measures Register (`23-emergency-governance-and-exceptions.md`).
- MUST: extra safeguards for election timing and incumbent entrenchment.

---

### Decision routing matrix (quick reference)

Use this to route proposals to the smallest *credible* legitimacy pipeline and to force a minimum set of public artifacts (so people can contest, audit, and appeal).

| Decision type | Minimum route (generators) | Mandatory artifacts (for legibility) |
|---|---|---|
| Routine operations | Admin execution under elected authority + transparency; tribunal/ombuds on demand | `DRR` decision record/receipt (where rights/resources affected) + reasons; service standards; complaint log IDs (`OPEN-9`) |
| Distributional budgets | Elected budgeting + readable accounts; bounded PB for local envelopes | budget + execution reports; `PROG-*` IDs for major lines; `DRR` for high-impact awards/eligibility; evaluation commitments for reforms (`OPEN-8`) |
| Rights-limiting / coercive | Legality + published doctrine; independent oversight; enforceable remedy | `DRR` + Rule IDs; incident logs; serious-incident pipeline IDs; `DPR-*`/`ADS-*` IDs if data/automation (`LAW-8`, `IOP-5`) |
| Long-horizon / irreversible | Elected decision + deliberative quality gate + future impact statement | public evidence pack; assumptions; `DRR`; `PROG-*`/`EVAL-*` IDs; `STD-*` IDs where technical (`DEC-6`, `IOP-8`) |
| Boundary / mandate changes | MV-BRP process + deliberation + fiscal note | competence-ledger version event + authorizing `DRR`; boundary crosswalk; transition plan (`17-...`, `70-...`) |
| Inter-jurisdiction commitments | Compact discipline + auditability; elevate to dual legitimacy when powers are high-salience | Compact ID + compact register entry + authorizing `DRR`; ledger updates; consolidation logic (`19-...`, `70-...`) |
| Emergency / exception governance | Typed declaration + sunsets/renewals + independent review stays on | EMR ID + linked exception ledger + `DRR` for exceptional measures; after-action review (`23-...`, `70-...`) |

---

## 3) Minimum Viable Legitimacy Stack (MVLS)
A scope has MVLS when it has all of the following (adapted by scale):

### A) Contestability
- **Regular, competitive elections** for general-purpose authority (`DEC-1`).
- **Districting & representation rules** published and stable; changes require heightened process (see §5).
- **Political finance / influence transparency** baseline (`ACC-5`).

### A1) Legibility needs bite (counter-power floor)
Legibility is necessary but not sufficient: when information exists and enforcement doesn’t, contestation becomes theater (see `04-threat-models.md` [TM-33]).
Minimum floor:
- at least one **independent body that can compel records and impose/trigger consequences** (`32-...`, `55-...`, `82-...`)
- **contestation capacity** treated as public infrastructure (legal aid, advocates, safe filing, non‑digital paths) (`08-...`, `98-...`, `82-...`)
- **automatic consequence triggers** (“dead‑man’s switches”) for missed deadlines / ignored findings (`82-...`, `35-...`, `07-...`)
- **redundant oversight** / overlapping mandates to reduce single‑point capture (`32-...`)
(See `101-claude-rev142-normative-requirements.md` (NR-02, NR-13); `04-threat-models.md` [TM-33].)

### B) Reason-giving and public learning
- **Public record** for major decisions (proposal, evidence, alternatives, reasons, votes, implementation plan).
- **Publication of uncertainty**: what is known, unknown, and assumed (`OPEN-5`).

### C) Deliberative “quality gate”
- A standing ability to convene **deliberative mini-publics** with stratified random selection and compensation (`DEC-2`).
- A **duty-to-respond**: elected/authorized bodies MUST respond publicly, within a deadline, to recommendations.
- SHOULD: log the process as an `ENG-*` entry (Participation & Deliberation Register) and link recommendations → response `DRR` (see `41-...`, `IOP-17`).

### D) Rights and remedy
- A path to **independent review** and enforceable remedy (`LAW-3`, `LAW-5`; see `08-...`).
- Protection for complainants and whistleblowers (`ACC-2/3`).

### E) Integrity and audit
- Independent audit and procurement legibility (`ACC-1`, `OPEN-2`).

**If MVLS fails at any layer, “more participation” will not fix legitimacy.** Fix contestability, reason-giving, or remedy first.

---

## 4) Design patterns (small, reusable)

### Pattern 1: “Elected allocates, deliberation reviews”
- Elected body retains final authority.
- Standing Citizens’ Assembly reviews: major plans, high-salience conflicts, long-horizon risks.
- Assembly output is non-binding but triggers: (a) published response, (b) amended draft, or (c) recorded disagreement.

### Pattern 2: “PB for bounded budgets”
- PB is most legitimate when:
  - envelope is fixed and public,
  - eligibility rules are clear,
  - projects are audited,
  - results are implemented on a timetable.

### Pattern 3: “Direct democracy with a deliberative phase”
- Any initiative/referendum route MUST include:
  - constitutional/rights review,
  - fiscal note + implementation plan,
  - a deliberative mini-public phase with a public evidence pack,
  - signature integrity and anti-dark-money disclosure.

### Pattern 4: “Independent election administration”
- Electoral administration SHOULD be insulated from partisan control and audited.
- Anchor: International IDEA *Electoral Management Design*: see [BIB-IDEA-EMD].
- Observation/standards anchor: OSCE/ODIHR *Election Observation Handbook*: see [BIB-OSCE-EOH].
- Verification anchor: election outcomes should be independently checkable (prefer risk‑limiting audits where feasible); see [BIB-NASEM-SECURINGTHEVOTE-2018] and [BIB-NIST-RLA-GENTLE].
- See: `56-elections-and-electoral-administration.md`.

### Pattern 5: “Future-proofing as an interface”
- For long-horizon domains (climate, infrastructure, AI, pensions), add:
  - future impact statements,
  - review triggers,
  - independent evaluation.
- Anchor: see [BIB-UN-DFG].

---

## 5) Representation choices (compact menu)
Representation is a design variable; the choice changes coalition incentives.

### A) Districting and apportionment
- SHOULD follow stable criteria; minimize bias; independent boundary review.
- Anchor: Venice Commission Code: see [BIB-VENICE-ELECT].

### B) Majoritarian vs proportional
- **Majoritarian**: clearer accountability; higher risk of permanent minorities and polarization.
- **Proportional / multi-member**: inclusion; coalition governance; risk of fragmentation.

### C) Preferential methods (RCV/approval)
- These can reduce “spoiler” dynamics and encourage broader coalitions; design details matter.
- Use only with clear voter education and transparent tabulation.

### D) Mixed systems
- Common compromise: constituency + proportional top-up (MMP-like). Use when you need both place-linkage and proportional fairness.

Anchor: see [BIB-IDEA-ESD].

---

## 6) By scope (default compositions)
This is a **starting point**, not a universal template.

- **Micro-local (`10-...`)**: mixed councils (elected + sortition) + PB; strong anti-exclusion safeguards.
- **Municipal (`20-...`)**: elected council with proportional incentives where feasible + standing Citizens’ Assembly for major plans; strong remedy for permits/services.
- **Metro/regional overlays (`16-...`, `30-...`)**: legitimacy often collapses when bodies are indirect/opaque; use direct representation for high-salience powers, otherwise compact/authority transparency + duty-to-respond forums.
- **National (`40-...`)**: “people + places” compromise (often bicameral) + independent election admin + strong constitutional remedy; deliberation for constitutional/long-horizon issues.
- **Supranational (`50-...`)**: subsidiarity review + parliamentary channel + dispute settlement; deliberation to build cross-border legitimacy.
- **Global (`60-...`)**: no unitary demos; rely on layered legitimacy: treaty consent + transparency + verification + remedy; add recurring global deliberative panels for agenda and norm testing.

---

## 7) Failure modes (and the first fix)
- **Participation theatre:** lots of meetings, no power. Fix: duty-to-respond + decision logging + an Engagement Register (`ENG`) that links inputs to response `DRR` (see `41-...`, `IOP-17`).
- **Capture by professional advocates:** fix: sortition mini-publics + influence transparency.
- **Manipulated referenda:** fix: deliberative phase + fiscal/rights review + disclosure.
- **Legibility collapse (“who governs?”):** fix: competence ledger + compact register (`34-...`, `70-...`, `19-...`).
- **Legitimacy collapse from coercion:** fix: legality + oversight + remedy before expanding mandates.