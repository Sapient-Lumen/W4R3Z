# Public Assets, Maintenance, and Capital Planning Rails

**Stack relation:** use `304-public-capital-assets-and-infrastructure-resilience-routing-guide.md` for the canonical route across the public-capital / assets / infrastructure-resilience family. This memo is the maintenance / lifecycle-planning / deferred-maintenance-liability specialization; `97` is the broad capital-allocation / stage-gate front door; `138` handles large-project integrity and change orders; `48` is the asset-register substrate; `154` handles resilience compacts; and `59` handles cyber / outage continuity. `302` remains the fiscal-state neighbor when the primary question is money-power design.

**Purpose:** prevent “infrastructure collapse by neglect” by making assets legible end‑to‑end: inventory → condition → maintenance plan → capital decisions → delivery → operations.

**Person served:** a resident who depends on roads, bridges, water, housing, schools, hospitals, parks, and digital infrastructure—who usually only learns something is broken *after* failure.

This memo defines the minimum rails for **capital governance** so that:
- capital projects don’t crowd out maintenance,
- lifecycle costs are accounted for,
- deferred maintenance becomes a *tracked liability*, not a political trick,
- procurement + delivery choices remain contestable,
- safety‑critical assets get stronger scrutiny.

**Anchor set (start here):**
- OECD Recommendation on the Governance of Infrastructure (2020): see [BIB-OECD-INFRA-2020].
- IMF Public Investment Management Assessment (PIMA) framework + handbook: see [BIB-IMF-PIMA-2022] and [BIB-IMF-PIMA-2025].
- World Bank Public Investment Management Reference Guide (2016/2020): see [BIB-WB-PIM-RG-2016].
- GASB Statement No. 34 (modified approach for infrastructure): see [BIB-GASB-34].

## Kernel anchors (do not repeat)
- Asset identity and inventory are already in the archive: `48-asset-and-infrastructure-register.md`.
- Procurement integrity + open contracting: `110-budget-procurement-integrity.md`, `179-open-contracting-and-procurement-rails.md`.
- Service SLOs + redress ops: `108-service-standards-and-time-budgets.md`, `189-service-level-governance-and-redress-ops.md`.
- Observability and audit rails: `197-polycentric-federalism-and-overlapping-sovereignty.md`, `84-internal-controls-and-continuous-assurance.md`.

---

## A. Minimum Viable Asset Governance (MV-AG)

1) **Asset register is complete enough to govern**
- MUST: every material public asset/network has a stable **Asset ID (AST-*)** and owner/operator Unit IDs.
- MUST: criticality tags (safety critical / continuity critical / climate critical).
- MUST: link to contracts (`CON-*`), maintenance work orders (`WO-*`), incidents (`INC-*`), and service catalog items (`SRV-*`) where the asset is a dependency.

2) **Condition + risk are measured on a schedule**
- MUST: publish a condition method and cadence by asset class.
- MUST: store last-inspected date + condition score + inspector identity (or audited org).
- SHOULD: include “unknown condition” as an explicit risk category (unknown is not neutral).

3) **Maintenance is budgeted as a first-class obligation**
- MUST: each asset class has a maintenance standard and a minimum condition target.
- MUST: maintenance plans include a **funding plan** (base + contingency).
- MUST: maintenance underfunding is disclosed as **deferred maintenance debt** with a dated trajectory.

4) **Lifecycle cost discipline for capital decisions**
- MUST: every capital proposal includes lifecycle cost (capex + opex + renewal) and risk externalities.
- MUST: disclose “future operating cost commitments” created by new assets.
- SHOULD: require explicit trade-off statements: “this project implies X maintenance deferral elsewhere” unless additional funding is dedicated.

5) **Capital pipeline is legible and contestable**
- MUST: publish a pipeline with stage gates (idea → appraisal → selection → delivery → operations review).
- MUST: publish why projects were selected or not (reason codes: `52-reason-codes-registry.md`).
- SHOULD: reserve a portion of capacity for *repair-first* projects.

6) **Delivery choices remain auditable**
- MUST: contract variation/change-orders are published and explainable (link `CON-*` ↔ `AST-*`).
- MUST: a “project outcomes” page exists post‑delivery (time, cost, scope, defects, warranty claims).

7) **Operations review closes the loop**
- MUST: post‑implementation review at 6–18 months: performance vs expected; lessons learned; corrective actions.
- MUST: incident reporting that links failures back to maintenance decisions and procurement.

---

## B. Stage gates (capital governance without bureaucracy theater)

**Gate 0 — Eligibility**
- Does the proposal reference an `AST-*` (or declare a new AST) and a service dependency (`SRV-*`) where relevant?

**Gate 1 — Appraisal**
- Options analysis includes “maintain/repair existing” and “non‑asset alternatives” (policy/process changes).
- Lifecycle cost + risk model attached.

**Gate 2 — Selection**
- Portfolio view: new capex cannot silently cannibalize essential maintenance.
- Equity + access impacts are assessed (`209-equal-protection-accessibility-and-language-access-rails.md`).

**Gate 3 — Delivery**
- Procurement uses open contracting rails (`179-...`).
- Variation discipline enforced.

**Gate 4 — Operations & renewal**
- Maintenance plan updates and budget line changes are recorded.
- Asset condition trend is published.

---

## C. Schema notes (linkages, not new bureaucracy)

### 1) Asset-to-service dependency edges
Create explicit links:
- `SRV-*` → depends_on → `AST-*`

This enables **service SLO auditing** to identify whether failures come from:
- staffing/capacity,
- vendor performance,
- asset condition,
- or policy constraints.

### 2) Deferred maintenance as a public liability
Track a simple series per asset class:
- current condition distribution
- target condition distribution
- backlog estimate range (with method)
- annual maintenance spend vs required spend

GASB’s “modified approach” conceptually supports publishing condition goals and required preservation costs when used. See [BIB-GASB-34].

---

## D. Failure modes + countermeasures

- **Capex glamour / maintenance starvation** → require portfolio trade-off statements + publish deferred maintenance debt.
- **“Unknown condition” hiding** → condition cadence + “unknown” risk tagging and escalation.
- **Procurement-driven design capture** → open contracting + variation transparency + independent estimates.
- **Asset owner/operator ambiguity** → enforce owner/operator Unit IDs and responsibility lines.
- **Emergency-by-neglect** → integrate with emergency powers discipline (`112-...`, `186-...`) so “deferred maintenance” cannot be laundered into permanent emergency.

---

## E. Minimal tests (add to `107-governance-test-suite.md`)

- **T3.8 Asset legibility:** every critical service has declared `AST-*` dependencies.
- **T3.9 Maintenance funding honesty:** deferred maintenance debt is disclosed with method + trend.
- **T3.10 Capital lifecycle discipline:** every project has lifecycle cost and explicit operating cost commitments.

