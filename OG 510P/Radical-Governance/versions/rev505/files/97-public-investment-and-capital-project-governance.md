# Public Investment & Capital Project Governance (Infrastructure Spend as Legitimacy Infrastructure)

**Stack relation:** use `304-public-capital-assets-and-infrastructure-resilience-routing-guide.md` for the canonical route across the public-capital / assets / infrastructure-resilience family. This memo is the broad capital-allocation / stage-gate / lifecycle-governance front door; `138` is the large-project integrity / change-order specialization; `225` handles maintenance and deferred-maintenance liability; `48` is the asset-register substrate; `154` handles resilience compacts; and `59` handles cyber / outage continuity. `302` remains the fiscal-state neighbor when the real issue is broader money-power design.

**Purpose:** make capital projects contestable over their lifecycle so debt, land, and contracts don’t become hidden coercion.

**Person served:** Residents paying for and living with public projects who need stage gates that prevent corruption, cost overruns, and unsafe assets.

**From-below:** This makes capital projects traceable so spending delivers, overruns are contestable, and communities can demand follow‑through.

**EXP pointer:** counters `EXP-02` (Waiting) and `EXP-07` (Indifference) by making capital projects receipted, time-bounded, and contestable when delay or harm concentrates on communities (see `98-persons-path-and-accessibility-invariants.md`).

Public infrastructure spending is a **high-risk legitimacy surface**: it is where optimism bias, corruption, and “announce-and-abandon” politics meet long-lived assets and future obligations.
This memo defines a compact **stage-gated discipline** for major capital projects **without adding new ID families**.

**Interfaces to reuse (no new ID families):** `PROG-*` (portfolio/program), `AST-*` (assets), `CON-*` (procurement/contract), `RULE-*` (legal basis), `REL-*` (published methods/baselines), `DRR-*` (gate approvals, scope changes, sanctions, cancellations), `AL-*` (appeals/urgent lanes), `OFR-*` (oversight cases), `SRV-*` (services affected).

Anchors (start here): [BIB-IMF-PIMA-2022]; [BIB-OECD-INFRA-2020]; [BIB-WB-INFRAGOV-2023]; appraisal baseline: [BIB-UK-GREENBOOK-2026].
See also: `07-fiscal-and-budgetary-governance.md` (budget legitimacy), `48-asset-and-infrastructure-register.md` (join keys), `22-public-integrity-and-procurement.md` + `38-contracting-and-procurement-register.md` (open contracting), `63-climate-adaptation-and-disaster-risk-governance.md` (resilience), `89-intergenerational-governance-and-future-obligations.md` (irreversibility/future lane).

## Kernel anchors (do not repeat)
- Contracting/procurement register and COI constraints: `38-...`, `79-...`.
- Asset/infrastructure register (what is built/owned): `48-...`.
- Records + publication integrity for decisions, change orders, and audits: `31-...`, `53-...`.
- Service standards / public value obligations: `82-...`.
- Protective legibility (who benefits; who pays): `99-protective-legibility-and-adoption-dynamics.md`.
- Person-facing access (capital projects impose time/transport/safety burdens; keep remedy usable): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- Speed of delivery vs due diligence and corruption resistance.
- Transparency and public scrutiny vs sabotage/security risks.
- Lowest upfront cost vs lifecycle quality/resilience.
- Local economic goals vs fair competition and capture.

---
## A. Minimum viable capital project governance (MVCPG)

### 1) Portfolio discipline (before picking projects)
- MUST: treat major capital projects as a **portfolio** (`PROG-*`) with an explicit purpose (service reliability, capacity, safety, decarbonization, resilience).
- MUST: publish portfolio criteria as a versioned `REL-*` (what qualifies; how prioritization happens; update log).
- SHOULD: enforce a “**maintenance first**” screen: new capacity is disfavored when a material maintenance backlog exists unless explicitly justified (join to [CAD-7] via `AST-*`).

### 2) Appraisal discipline (no “single-option theatre”)
For major projects (local definition), the proposal MUST have a public appraisal packet (coarsened if needed).
- MUST: a clear **problem statement** + scope boundaries + non-goals.
- MUST: options analysis (≥2 credible options, including “do minimum/maintain/retrofit”).
- MUST: published assumptions (demand, costs, discounting, delivery approach), with a revision log (`REL-*`).
- SHOULD: include distributional impacts (who pays/who benefits), land/tenure issues, and rights impacts (link to `62-...`, `12-...` where relevant).
- SHOULD: include a person-facing access plan for affected residents and landholders: notices that pass the comprehension test, a no-wrong-door intake for questions/objections, and representation duty triggers where displacement/low-capacity communities are involved. (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`)
- SHOULD: resilience and climate screens for material assets (hazard exposure, lock-in risk) and lifecycle O&M implications (link to `63-...`, `65-...`).

### 3) Gate approvals emit Decision Receipts (`DRR-*`)
Major capital projects SHOULD not proceed on “press release authority.”
- MUST: each stage gate emits a `DRR-*` that cites:
 - the legal basis (`RULE-*` as-of),
 - the latest appraisal/baseline release(s) (`REL-*`),
 - the affected asset(s) (`AST-*`, created or changed),
 - the program/portfolio (`PROG-*`),
 - the contestation lane(s) (`AL-*`) where applicable.

Where the project requires takings, relocation, or compensation determinations, those individual decisions MUST emit their own `DRR-*` receipts (with usable remedy lanes and interim protection norms for housing continuity) rather than being buried inside a project dossier. (`62-...`, `98-persons-path-and-accessibility-invariants.md`, `36-...`)

**Portable gate set (minimal):**
- **G0 — Portfolio admission** (eligible and prioritized; alternatives considered).
- **G1 — Preferred option approval** (appraisal meets threshold; baseline published).
- **G2 — Procurement authorization** (procurement plan, market sounding, conflict controls).
- **G3 — Award and notice-to-proceed** (award published; beneficial ownership complete; bid‑rigging checks).
- **G4 — Commissioning/acceptance** (as-built + safety/quality sign-off; operating responsibility assigned).
- **G5 — Post-implementation review** (benefits vs baseline; lessons captured; deprecation/retrofit decisions).

### 4) Procurement and change control are first-class legitimacy surfaces
- MUST: publish awards and core contract fields with joinable IDs (`CON-*`, and OCID where using OCDS) (`38-...`, [BIB-OCDS]).
- MUST: treat **material change orders** and scope changes as decisions: emit `DRR-*` citing baseline deltas, reasons (`RC-*`), and independent review triggers where thresholds are crossed (tie to `55-...` / `OFR-*` sampling).
- SHOULD: adopt explicit anti-bid‑rigging and collusion protocols for capital spend (`22-...`, [BIB-OECD-BIDRIGGING-2025]).

### 5) Handover, maintenance funding, and asset joinability
- MUST: “build → operate” handoff produces/updates `AST-*` entries (condition baseline, responsible steward, inspection cadence).
- MUST: major capex approvals include a credible **operations & maintenance** funding plan (avoid hidden future liabilities) (join to `07` and [IPM-8]).
- SHOULD: publish lifecycle cost assumptions and update them after commissioning (`REL-*` with diffs).

### 6) Benefits realization and evaluation commitments
- SHOULD: major projects register a benefits hypothesis and evaluation commitment (`28-...` / `EVAL-*` where used) and publish results as `REL-*` (methods + revisions). Anchors: [BIB-UK-MAGENTA-2025].

---

## B. Join rules (so “capex vs maintenance vs performance” is auditable)

1) **Every major project attaches to `AST-*`.** If the asset does not exist yet, create the `AST-*` at G1 (preferred option) so downstream spend can join early.
2) **Every gate emits a `DRR-*`.** Approvals, cancellations, and major scope changes are not “management notes.”
3) **Every award attaches to `CON-*` and cites the gate `DRR-*`.** Awards without an authorizing `DRR-*` are governance incidents.
4) **Baselines are versioned `REL-*`.** Cost/schedule/benefit baselines and appraisal methods must be diffable (no silent edits).
5) **Change orders are joinable.** Material changes cite the original baseline `REL-*` and record delta impacts (cost/schedule/benefits/risk).
6) **Commissioning updates the AIR.** G4 must update `AST-*` condition and steward/operator fields, and establish inspection cadence.

---

## C. Failure modes (and minimal countermeasures)

- **Optimism bias / strategic misrepresentation:** require options analysis + published baselines + post‑implementation review (G5) tied to accountability (`OFR-*` sampling).
- **Corruption via change orders:** publish change orders, enforce thresholds for independent review, separate duties, and use open contracting joins.
- **Off-book liabilities (PPPs/guarantees/maintenance starvation):** publish fiscal risk statement + lifecycle O&M commitments; join to `IPM-8` and AIR backlog [CAD-7].
- **Lock‑in / irreversible harm:** apply the irreversibility test (`89-...`) and require explicit “stop rules” / off-ramps with sunset/review dates (`74-...`).

---

## D. Minimal metrics (portable)
Use existing packs; do not invent a new metric family.
- **[CAD-6] Delivery slippage:** cost/schedule variance for major works (join to `AST-*` / `CON-*`).
- **[CAD-7] Maintenance backlog:** backlog ratio + condition trend for critical assets (join to `AST-*`).
- **[IPM-8] Fiscal risk completeness:** include PPP/guarantee + O&M exposure when material.
- **[IPM-5] Audit closure:** % recommendations closed within 12/24 months (for sampled major projects).
