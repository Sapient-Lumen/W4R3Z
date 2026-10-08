# Internal Controls & Continuous Assurance (Make Execution Defensible)

**Purpose:** make internal controls continuous and evidence-backed so failures are detected before they become tragedies.

Public power fails less from “bad laws” than from **weak execution**: fraud, quiet policy drift, unmanaged discretion, and missing follow‑through.
Internal control is the *boring* backbone that makes money, decisions, and compliance **defensible**.

This memo defines a minimal internal control + assurance discipline that plugs into existing joinable artifacts (`REL/DRR/OFR/AL/RULE/STD/CMP`) **without** introducing a new ID family.

**Anchor set:** internal control standards and components in the INTOSAI public-sector guidelines ([BIB-INTOSAI-GOV-9100]); the “three lines” assurance model ([BIB-IIA-THREELINES-2020]); and the US public-sector control framework (“Green Book”) ([BIB-GAO-GREENBOOK-2025]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Assurance case discipline for high-stakes claims: `73-...`.
- Evidence/metrics discipline: `03-...`.
- Records custody and audit trails: `31-...`.
- Publication integrity for control assertions and findings: `53-...`, `55-...`.

## Named tensions (design must surface these)
- Controls and assurance vs throughput/service delivery.
- Real risk reduction vs box-ticking (compliance theater).
- Central audit power vs local autonomy and learning.
- Transparency of controls vs attacker advantage and insider threat.

---
## A. Minimum viable internal control system (MVICS)

A unit SHOULD treat internal control as a small system with five components (language aligns across anchor frameworks):

1) **Control environment**
- MUST: role clarity (who can authorize, approve, execute, review).
- MUST: delegation/acting authority discipline (`78-...`) so “who signed” is auditable.

2) **Risk assessment**
- MUST: a short list of *material risks* (fraud/leakage, coercion abuse, data misuse, outage/continuity, capture) and the controls that claim to address them.
- SHOULD: explicitly tag which risks are *most likely* vs *most catastrophic* (so testing plans aren’t gamed).

3) **Control activities**
- MUST: separation of duties where feasible; otherwise compensating controls (two-person checks, post‑hoc review with sampling).
- MUST: procurement and payment controls for material spend (`38-...`, `07-...`).
- MUST: revenue assessment/collection controls (separation of duties; write-off/abatement logs; audit trail for adjustments) where revenue power is exercised (`93-...`).
- MUST: stage-gate controls for major capital projects (approval/change/cancel receipts; post-implementation review) where infrastructure spend is material (`97-...`).
- MUST: access control + audit logging for systems that decide/allocate/enforce (`06-...`, `42-...`, `59-...`).

4) **Information & communication**
- MUST: staff know the rules; rule changes have distribution + effective dates (`39-...`, `31-...`).
- MUST: “stop the line” escalation path for safety/rights issues; protected disclosures exist (`83-...`).

5) **Monitoring**
- MUST: periodic control testing and a public exception discipline (below).
- MUST: material failures route into **follow‑through** (`OFR-*`) with closure evidence.

---

## B. Continuous assurance via publishable “control map” releases (no new IDs)

To prevent internal control from becoming invisible “compliance theater,” publish three small releases as `REL-*` (diffable, with method notes):

### 1) `REL-TYPE: CONTROL-MAP` (what controls exist and why)
**Cadence:** at least annual; also when major systems/processes change.

**Minimum fields**
- `UNIT` (Unit ID)
- `PERIOD` (dates)
- `MATERIAL-RISKS` (short list; cite relevant `TM-*` where useful)
- `CONTROL-SET` (table with: control name, owner role, control type: preventive/detective/corrective)
- `BASIS` (0+ pointers to `RULE-*` / `STD-*` / `CMP-*` / `IOP-*` that require the control)
- `SYSTEMS` (0+ `ADS-*` / major platforms affected)
- `LAST-UPDATED` + revision log (no silent edits)

### 2) `REL-TYPE: CONTROL-TEST-PLAN` (how controls will be checked)
**Minimum fields**
- `UNIT`, `PERIOD`
- `COVERAGE` (what % of controls will be tested; what is sampled vs 100%)
- `METHOD` (sampling logic; independence note)
- `TRIGGERS` (what opens an `OFR-*`: severity/recurrence thresholds)

### 3) `REL-TYPE: CONTROL-TEST-RESULTS` (what failed, what changed)
**Minimum fields**
- `UNIT`, `PERIOD`
- `EXCEPTIONS` (counts by control/risk class; severity scale)
- `ACTIONS` (corrective actions + deadlines; pointer to evidence releases)
- `OFR-LINKS` (any material/non‑routine exceptions open an `OFR-*`)

**Rule (material exceptions):** if an exception can change rights/resources at scale, it MUST open an `OFR-*` within a stated time window (default: 14 days), and closure requires evidence.

---

## C. Assurance roles: “Three Lines” without bluffing

Use the three lines model as a *role clarity* tool (not a reporting chart):

- **1st line (operations):** owns delivery and controls in daily work.
- **2nd line (risk/compliance):** sets frameworks, monitors, supports; not fully independent.
- **3rd line (internal audit / inspection):** independent assurance; reports to oversight body.

**Join rules (minimal)**
- Internal audit/inspection findings publish as `REL-*` and/or open `OFR-*` where follow‑through is required (see `55-...`).
- If a finding changes authority (recusal, delegation removal, procurement stop), emit a typed `DRR` (`DRR-TYPE: INTEGRITY` / `DELEGATION`) so the change is contestable (`36-...`).

---

## D. Failure modes (and how to force reality)

- **Paper controls:** control maps exist but tests never happen → require published test plans + results; missed cadence is an incident (`71-...`).
- **Independence theatre:** “audit” reports to the unit it audits → publish reporting line + recusal rules; route blocked findings into external oversight (`32-...`, `55-...`).
- **Exception laundering:** exceptions handled informally → material exceptions MUST open `OFR-*` with deadlines and closure evidence. (See `85-waivers-variances-and-exceptions-discipline.md` for the general waiver/variance protocol.)
- **Secrecy as a shield:** “can’t publish” becomes blanket → apply `77` (publish receipts even when payload withheld; oversight has protective access).

---

## E. Where this plugs in (do not duplicate)

- **Money systems:** `07-fiscal-and-budgetary-governance.md`, `38-contracting-and-procurement-register.md`, `49-...` (transfers/subsidies)
- **Compliance regimes:** `81-verification-inspection-and-compliance-ladders.md` (external verification) + `55-...` (findings follow‑through)
- **High-stakes systems:** `06-digital-and-algorithmic-governance.md`, `42-...` (ADS register), `59-...` (cyber/CI)
- **Integrity speakability:** `83-whistleblowing-and-protected-disclosures.md`
- **Secrecy exceptions:** `77-sensitive-information-and-secrecy-governance.md`
