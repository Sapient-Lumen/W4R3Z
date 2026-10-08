# Jurisdiction Formation & Boundary Change (Create / Merge / Split Units)

**Purpose:** discipline boundary changes so reorganizations don’t erase obligations, records, or remedy routes.
**Person served:** a community affected by boundary, annexation, or district changes who needs those changes to be receipted, justified, and contestable (not used to erase voice).

**From-below:** This prevents boundary changes from quietly stripping your vote, services, or rights by forcing reasons, impact checks, and contestation paths.

This memo is a **cross-scope primitive**: how to *change the map* (territorial units and their responsibilities) without turning boundary decisions into gerrymandering, patronage, or service collapse.

**Quick use:** for a one-page operational checklist (gates: finance, records, remedy, elections), see `92-boundary-change-checklist.md`.

**Use cases**
- create a new jurisdiction (new municipality/region)
- merge jurisdictions (amalgamation)
- split jurisdictions (secession / subdivision)
- adjust boundaries (annexation / transfer of territory)
- transfer responsibilities between units (without boundary change)

**Why this matters:** boundary and structure decisions are among the highest-leverage moves in governance. They are also “low-salience” to most citizens until things break.

## Kernel anchors (do not repeat)

- **EXP pointer:** boundary/formation processes must reduce EXP-06 Complexity and EXP-01 Opacity (see `98-persons-path-and-accessibility-invariants.md`).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Constitutional discipline:** `58-constitutional-change-and-amendment-discipline.md`.

## Named tensions (design must surface these)
- **Self-determination vs minority protection:** boundary choices create winners/losers.
- **Stability vs adaptability:** durable borders vs demographic/ecological change.
- **Simplicity vs fairness:** legible maps vs gerrymander/capture risk.
- **Identity vs service delivery:** recognition claims vs administrative capacity.

## Anchor set (start here)
- European Charter of Local Self‑Government — **Article 5** (boundary changes require prior consultation): see [BIB-COE-LOCALSELF-ART5]
- Local Government Boundary Commission for England — technical guidance (statutory criteria and process discipline): see [BIB-LGBCE-GUIDE-2023]
- New Zealand Local Government Commission — reorganisation guidelines (end-to-end process template): see [BIB-NZ-LGC-REORG-GUIDE]
- World Bank — *Municipal Mergers and Associations* (comparative lessons + evidence framing): see [BIB-WB-MUNICIPAL-MERGERS]
- Oates (1999) — fiscal federalism / decentralization logic (spillovers vs. heterogeneity): see [BIB-OATES-1999-FISCALFED]
- Gómez‑Reino et al. (2021) — meta-analysis on scale economies in local services (scale is real but not universal): see [BIB-GOMEZ-REINO-2021-SCALEMETA]
- Blesse & Baskaran (2016) — merger cost evidence (example quasi-experimental design): see [BIB-BLESSE-BASKARAN-2016-MERGERS]

---

## 1) The decision rule: use the smallest change that solves the problem

Order of operations (least structural violence → most):
1) **Compact / contract** (`IOP-1`) — coordinate without changing who exists.
2) **Functional authority** (`15-functional-authorities.md`) — add a narrow-body for a network good with strong auditability.
3) **Boundary adjustment** — fix mismatched service areas or broken community-of-interest edges.
4) **Responsibility transfer** — move a function up/down while keeping boundaries stable (requires clear funding responsibility).
5) **Merger / split / new unit** — structural change with high transition cost.

**Bias:** prefer *reversible* and *auditable* moves first (see `03-metrics-and-evidence.md`, `04-threat-models.md`).

---

## 2) Tests (when a new unit, merger, split, or boundary change is justified)

Use these as a **gate** before politics turns it into a tribal referendum.

### T1 — Spillover / externality test (the “why isn’t this already working?” test)
Boundary change is justified if a major policy domain has spillovers that are systematically unmanaged:
- air/water basins, transit corridors, housing/land-use spillovers, emergency response mutuality
- cross-border enforcement or regulation gaps producing arbitrage

If spillovers dominate but local preference heterogeneity is high, prefer **metro overlays** and **functional authorities** (`16-...`, `15-...`) before mergers.

### T2 — Scale & capital test (economies of scale + capex governance)
Some network goods have:
- large fixed costs, complex maintenance, and long-horizon capital planning
- debt capacity needs that small units cannot credibly manage

Use evidence carefully: scale economies vary by service and context (see the meta-analysis anchor above).

### T3 — Preference heterogeneity test (subsidiarity’s core)
If residents’ preferences or conditions are materially heterogeneous, a merger may **degrade welfare** even if administrative costs fall. Use:
- service preference mapping (surveys + revealed demand where possible)
- “local option” design: keep preference-sensitive services local, while merging only back-office and network goods.

### T4 — Administrative capability test (capacity floor)
If a unit cannot sustain:
- basic budgeting, procurement, staffing, remedy, and auditability (`07`, `08`, `09`)
then you either:
- merge, or
- create a shared-service authority / joint administration compact with strict transparency.

### T5 — Fiscal base alignment test (avoid free-riding and predation)
Boundary changes must specify:
- who pays, who benefits, and who bears residual risk (guarantees, pensions, debt)
- transfer formulas and equalization rules (avoid “tax base secession” dynamics)

### T6 — Rights, remedy, and representation test (anti-gerrymander)
A boundary change fails if it predictably:
- entrenches a group’s disenfranchisement
- breaks remedy pathways or creates “forum shopping” to evade accountability
- produces large and persistent electoral inequality

---

## 3) Minimum Viable Boundary & Reorganisation Process (MV-BRP)

A process is legitimate if it is **bounded, reviewable, and transition-safe**.

### MV-BRP institutions
- **Independent boundary / reorganisation commission** (statutory mandate; protected budget line)  
  - proposes or evaluates changes against published criteria
  - runs consultation + publishes impact assessments
  - maintains a public change-log and implementation plan

- **Consultation requirement** (communities must be consulted; referendum optional but not always sufficient)
  - consultation must include affected residents + affected service users (not always identical)

- **Judicial / quasi-judicial review path** (`LAW-5`)
  - fast review for process violations, rights violations, or bad-faith gerrymandering

### MV-BRP artifacts (must be published)

- **If the change requires charter/constitution amendment:** treat it as integrity-grade constitutional change (proposal bundle as `REL-*` + gating docket as `DRR-TYPE: INTEGRITY`), per `58-constitutional-change-and-amendment-discipline.md`.

- **Impact assessment** (1–3 pages “decision brief” + appendices):
  - service continuity risks (what could break on day 1)
  - fiscal map: assets, liabilities, debt, pensions, guarantees
  - representation map: districts/wards implications; electoral equality impacts
  - capacity plan: staffing, systems migration, procurement continuity
  - “why this can’t be solved by a compact/authority instead”

- **Person-facing notice packet:** publish a comprehension-tested “what changes for you” notice (services affected, where to go, what stays the same, deadlines, how in‑flight cases are handled) and provide no‑wrong‑door routing + navigator support for low-capacity users (`98-persons-path-and-accessibility-invariants.md`, `47-...`).

- **Scope assignment record** (`DRR-TYPE: SCOPE`; see `IOP-10` in `02-design-toolkit.md`)
  - records the scope tests (spillovers/scale/local knowledge/rights risk/enforceability) and the evidence used
  - links the competence-ledger change (old → new) and the money-map change (revenue/transfers/liabilities)
  - names the remedy continuity plan (where appeals go during and after transition)
  - **Minimum fields:** affected Unit IDs; mandate tags; competence-ledger crosswalk (old→new); backstop Unit ID per transferred mandate; funding/transfer IDs; transition deadlines; remedy lane mapping; evaluation checkpoint

- **Transition plan** (hard requirement)
  - asset + liability allocation rule (including pensions)
  - staff transfer and continuity rules (anti-purge)
  - data/system migration plan + accountability logs (`IOP-4/5/6`)
  - dispute resolution escalation ladder (`IOP-2`, `LAW-5`)
  - sunset / evaluation checkpoint (see next section)

### MV-BRP timing rules (anti-manipulation)
- No boundary change becomes effective **inside** a narrow pre-election window (jurisdiction-specific), unless emergency and court-validated.
- Publish draft maps early enough to allow counter-proposals.

(For examples of statutory criteria discipline and process mechanics, see the England and NZ anchors.)

---

## 4) Reversibility: pilots, sunsets, and “merge-with-exit”

When politics is uncertain, use **trial structures**:
- “merge back-office only” (shared admin authority) with a 3–5 year evaluation window
- “metro overlay first” (authority) before full two-tier metro government
- “merge-with-exit”: allow a split pathway if specific conditions fail (service quality, fiscal sustainability, representation)

**Rule:** any structural reform MUST have a falsification plan (what would make us undo or redesign it) (`03-metrics-and-evidence.md`).

---

## 5) Interfaces (how boundary changes stay legible)

Boundary changes are also *interoperability events*:
- Update the **competence ledger** and publish a new **version** (`34-competence-ledger-and-mandate-registry.md`; see also `70-interoperability.md`)
- Re-check **backstop routing** for transferred mandates (avoid “no one is obligated” gaps)
- Preserve stable **unit IDs** and maintain crosswalks (old → new)
- Move all affected bodies into **consolidated public accounts** (`07-fiscal-and-budgetary-governance.md`)
- Carry over grievance channels and ensure **no orphaned remedies** (`08-remedy-and-grievance.md`)

---

## 5a) Example: responsibility transfer without orphaning remedy
A boundary change is not required to trigger interoperability problems. Example pattern:
- A regional body takes over wastewater permitting from municipalities (responsibility transfer), but municipalities still control land-use approvals that affect runoff.
- Publish the transfer as a **competence-ledger version event** with a crosswalk: which `RULE-*` and `PAR-*` decisions move; which stay local; who funds enforcement.
- For any in-flight cases, preserve the same join-keys: decision receipts (`DRR-*`) and appeals continue without restart; the receiving unit inherits deadlines and evidence obligations.
- If mandates overlap, use the competence-dispute lane (`34-competence-ledger-and-mandate-registry.md`; see also `70-interoperability.md`) and publish the ruling + ledger update.

## 6) Success metrics (minimal)

Choose 5–10 measures tied to the decision rationale. Prefer metric IDs from `03-metrics-and-evidence.md` packs; add at most 1–2 local-only measures.
- admin cost per capita (local add-on; control for service mix)
- service continuity: outage/queue spikes at transition [CAD-1] / [CAD-2]
- capex delivery slippage + maintenance backlog trend [CAD-6] / [CAD-7]
- fiscal risk: debt + contingent liabilities (incl. pensions/guarantees) [IPM-9] + consolidation coverage [IPM-7]
- legitimacy: participation breadth / contestation [LRR-1]
- remedy effectiveness: time-to-resolution for top grievance classes [LRR-4]
- distribution: service access for historically underserved areas [CAD-3]

---

## 7) Failure modes + countermeasures (map to `04-threat-models.md`)

- **Gerrymander / boundary manipulation** → independent commission + timing rules + court review.
- **Tax-base secession / fiscal predation** → equalization + liability assignment rules; require consolidated risk reporting.
- **Service collapse during transition** → transition plan as a gating requirement; continuity staffing rules.
- **Hidden government via workaround bodies** → require ledger inclusion + consolidated accounts for all successor entities (`70`, `15`).
- **Over-merger (loss of local responsiveness)** → keep preference-sensitive services local; use overlays for network goods.
- **Reform theater** (structural change without capability) → capacity floor test; build auditability first (`80-implementation-roadmap.md`).
