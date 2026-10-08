# Asset & Infrastructure Register (AIR)

Public infrastructure fails when it becomes **invisible**: projects are announced, assets decay, maintenance is deferred, and “emergency repair” becomes a standing corruption channel.
This memo defines a compact **Asset & Infrastructure Register (AIR)** keyed by `AST-*` so capital, maintenance, outages, and safety risks can be joined across scopes.

**Anchor set (start here):** OECD Recommendation on the Governance of Infrastructure ([BIB-OECD-INFRA-2020]); IMF Public Investment Management Assessment (PIMA) handbook ([BIB-IMF-PIMA-2022]); ISO asset management overview ([BIB-ISO-55000]).

---

## 1) What counts as an `AST` object
An `AST-*` entry is a **public asset** or **publicly‑regulated critical asset** whose condition affects rights, safety, or essential services.
Examples: bridges, water mains, treatment plants, schools, hospitals, fleets, ports, public housing, major IT systems *when they are safety/service‑critical*.

**Rule:** do not create a new ID type for “projects.” Capital projects attach to assets via `AST-*` plus `CON-*` (procurement) and/or `PROG-*` (program object).

---

## 2) Minimal public fields (v0)
Publish a public AIR dataset keyed by `AST-*` (with a revision log via `REL-*`). The goal is **joinability**, not perfect detail.

| Field | Meaning | Links |
|---|---|---|
| `AST-*` | stable asset ID | join key |
| `asset_class` | type/category (road/bridge/school/water/etc.) | align to local taxonomy (and COFOG where useful) |
| `name_or_label` | human label | avoid sensitive details |
| `location` | coarse location (grid/segment) | protect sensitive facilities |
| `owner_unit` / `operator_unit` | who owns and who operates | Unit IDs (competence ledger) |
| `service_dependencies` | what services rely on it | `SRV-*` where defined |
| `criticality_tier` | low/med/high (typed rubric) | drives inspection cadence |
| `condition_grade` | A–F (or similar) + method | link to `REL-*` inspection method |
| `last_inspected` | date |  |
| `maintenance_backlog_est` | backlog $ or backlog/RC ratio | ties to [CAD-7] |
| `planned_work` | planned works and funding | `CON-*` / `PROG-*` / `TRF-*` / `EMR-*` where relevant |
| `incidents` (optional) | material outages/failures | link to `OFR-*` where independent review is triggered |

**Two-layer publication model:** keep a protected operational register (exact coordinates, security details) and publish a **coarsened public release** unless a narrow, typed exemption applies (see `31-records-foi-and-government-memory.md`).

---

## 3) Join rules (make “capex vs maintenance” auditable)
1) **Capital decisions must attach to assets.** Any capital appropriation / approval / award MUST cite `AST-*` (created or affected), plus `CON-*` and/or `PROG-*`.
2) **Maintenance deferral is a decision.** Material deferrals MUST produce a `DRR` citing the affected `AST-*`, the rule basis (as-of), and the next review date.
3) **Emergency repairs can’t be off-book.** If emergency powers/exception procurement are used, the work MUST cite `EMR-*` and be traceable to a `DRR`.
4) **Service outages are not “just operations.”** For critical assets, material outages SHOULD be logged and joinable to `AST-*` and affected `SRV-*` (ties to [CAD-1] / [CAD-2]).

---

## 4) Governance (minimum)
- **Stewardship assignment:** every `AST-*` has an accountable steward (Unit ID) and an operator (may differ).
- **Inspection cadence:** set by `criticality_tier` with published method notes (`REL-*`).
- **Lifecycle discipline:** require a published lifecycle cost view for major asset classes (build → maintain → replace). PIMA-style planning/allocation/implementation checks should be used to prevent “capex theatre.”
- **Oversight hook:** supreme audit/inspectorate SHOULD sample `AST-*` entries to verify existence, condition claims, and backlog estimates.

---

## 5) Minimal metrics (portable)
Do not invent new indicator families: reuse existing packs.
- **[CAD-6] Capex delivery slippage:** cost/schedule variance for major works linked to `AST-*`.
- **[CAD-7] Maintenance backlog:** backlog ratio + condition trend keyed to `AST-*`.
- **[IPM-8] Fiscal risk completeness:** include infrastructure liabilities and disaster exposure when material.

