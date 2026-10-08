# Critical Infrastructure & Utilities Integrity

**Purpose:** treat **utilities and critical infrastructure** (water, power, heat, sanitation, telecom, transport lifelines) as a *governance interface* where outages, rationing, maintenance backlogs, and emergency measures are **power** over people.

**Person served:** a person whose life depends on continuity of essential services and who needs *clear rights, clocks, and receipts*—especially during failures.

## Core primitives

### 1) Utility / Lifeline Service Card (USC-*)
A public, versioned card per service domain / operator / region.

**USC fields (minimum):**
- **Scope:** who is covered; exclusions; priority classes (with reason + appeal lane).
- **Service promise:** baseline availability; maximum outage windows; restoration targets; accessibility commitments.
- **Dependencies:** upstream/downstream dependencies (power → water, telecom → emergency).
- **Emergency modes:** predefined degradations (rationing tiers) + triggers + exit conditions.
- **Contact + contest:** how to report failure; how to contest classification/denial.

### 2) Outage / Degradation Event Receipt (OER-*)
Every significant outage, rationing episode, or safety shutdown produces an OER that is joinable to repair and remedy.

**OER fields (minimum):**
- What happened (start time, affected scope, severity tier).
- Why (cause category + uncertainty).
- Immediate protections (critical loads, medical needs, shelters, interim relief).
- Restoration plan (next update time, ETA ranges, dependencies).
- Post‑incident hooks: audit/inspection trigger; compensation/credits policy.

### 3) Maintenance & Asset Integrity Register (MAIR-*)
A lightweight public register of **risk‑bearing assets** (not sensitive details), with backlog + risk signals.

**MAIR fields (minimum):**
- Asset class + region; condition bands; deferred maintenance backlog summary.
- Risk tiers and “single points of failure”.
- Planned works schedule + change receipts (joins rulemaking/change control).

### 4) Priority / Rationing Decision Receipt (PRR-*)
When scarcity forces prioritization (rolling blackouts, water restrictions), decisions must be receipted.

**PRR fields (minimum):**
- Rule version used (joins `118-rulemaking-and-change-control.md`).
- Priority criteria + why proportional; what safeguards prevent discrimination.
- Contest path + interim protection for critical needs.

## Circuit breakers (anti‑abuse defaults)

- **CB‑U1 Restoration clock:** if restoration updates miss their promised cadence, auto‑escalate to independent incident command + publish a variance note (joins `108` time budgets).
- **CB‑U2 “No silent rationing”:** any degradation beyond baseline MUST issue an OER within a fixed window.
- **CB‑U3 Vulnerability protection:** if a person is medically/legally dependent on continuity, missed clocks trigger interim protection (alternate supply, relocation, credits) (joins `98`).
- **CB‑U4 Emergency procurement guardrails:** emergency buys must still produce minimal procurement receipts and post‑hoc audit hooks (joins `110/112/130`).

## Minimal metrics (publishable)
- Availability / outage minutes by tier; restoration time distribution; missed‑update rate.
- Deferred maintenance backlog trend; critical asset risk band trend.
- Complaints → resolution time; compensation/credits issued; contest outcomes.

## Joins (where this plugs in)
- Time budgets + service promises: `108-service-standards-and-time-budgets.md`.
- Portability / continuity at seams (moves, jurisdiction shifts): `109-portability-and-cross-jurisdiction-continuity.md`.
- Rule version replay / change control: `118-rulemaking-and-change-control.md`.
- Information integrity & disclosure clocks: `115-information-integrity-and-record-interfaces.md`.
- Audit & inspection follow‑through: `130-audit-and-inspection-integrity.md`.
- Exception control (emergency powers): `112-exception-control-and-emergency-powers.md`.

## Bibliography anchors
- Service standards & delivery: [BIB-UK-GOV-SERVICESTD], [BIB-OECD-PUBLIC-SERVICE].
- Asset management / maintenance discipline: [BIB-ISO-55000].
- Critical infrastructure resilience framing: [BIB-OECD-CRITINFRA].
- Water safety planning (risk‑based continuity): [BIB-WHO-WSP].

## See also
- `154-critical-infrastructure-resilience-compacts.md` — resilience compacts + mutual-aid rail patterns.
