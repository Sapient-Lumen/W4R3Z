# Audit & Inspection Integrity (Oversight as an interface)

**Purpose:** make oversight **operational** (not symbolic) by treating audits/inspections as **interfaces** with receipts, clocks, and follow‑through—so power stays contestable and capture-resistant.

**Scope:** Supreme Audit Institutions (SAIs), inspectors general, regulator inspections, accreditation audits, internal audit, and third‑party assurance used by government.

---

## Design stance

- Oversight fails in predictable ways: **scope capture**, **selective sampling**, **non-public findings**, **endless drafts**, **non-response**, and **no follow‑through**.
- Fix by requiring **verifiable artifacts** (receipts), **bounded timelines**, and **joinable follow‑through** into procurement/budget/rulemaking/control loops (`104`, `105`, `110`, `118`).

---

## Core objects (receipts + ledgers)

### Audit Plan Receipt (`APR-*`)
MUST include:
- mandate + authority; audited entity; period; audit type (financial / performance / compliance); scope exclusions (with reasons)
- risk rationale + selection method (join to `DR-*` if randomized/stratified selection is used — see `119`)
- data access basis + limits (join to `PDR-*`/`ALR-*` where sensitive data is accessed — see `127`)
- publication plan (what will be public; what will be withheld and why; redaction rules)
- timeline gates (draft → management response → publication deadline)

### Finding Receipt (`AFR-*`)
MUST include:
- finding statement; criteria/standard referenced; evidence pointers; severity; uncertainty/confidence
- responsible lane(s) (who can fix); harm surface (rights/safety/money/time)
- recommended actions as **testable** items, not slogans
- contest lane: how the audited entity (and affected public) can challenge facts/criteria without suppressing publication

### Management Response Receipt (`MRR-*`)
MUST include:
- accept / partially accept / reject (with reasons)
- remediation plan (owner, budget line, deadline); if rejecting, alternative safeguard
- if delayed: interim protections + a bounded reschedule (no indefinite deferral)

### Follow‑Through Ledger (`FTL-*`)
MUST include:
- each `AFR-*` mapped to implementation status; evidence of completion; residual risk
- escalation triggers (auto‑hearing, budget hold, procurement pause) when deadlines are missed (pair with `105` circuit breakers)
- repeat-finding detection (flag recurrences across years/agencies)

### Inspection Event Receipt (`IER-*`) (regulators / field inspection)
MUST include:
- site/system inspected; checklist version; sampling method; noncompliance items
- immediate protective orders (if any) + proportionality rationale
- contest/appeal path and interim safety defaults

---

## Independence & anti‑capture baseline

MUST:
- protected appointment + removal discipline for heads of oversight bodies (pair with `113`)
- budget protection floor + transparent staffing levels (pair with `110`)
- guaranteed access to records (including contractors), and protection from retaliation for sources (pair with `121`)
- publication default: **publish findings + management responses**, with narrow, receipted safety exceptions (pair with `115`)

Norm anchors: INTOSAI independence principles ([BIB-INTOSAI-P10], [BIB-INTOSAI-P1]); public‑sector auditing fundamentals ([BIB-ISSAI-100]).

---

## Timelines (anti-stall clocks)

MUST adopt hard deadlines (examples; tune by scope):
- draft findings to audited entity: ≤ 90 days after fieldwork close
- management response window: 30–60 days
- publication deadline: ≤ 30 days after response window closes
- follow‑through reporting: quarterly until closure

Missed clocks MUST trigger a public **Delay Receipt** (who delayed, why, new date, interim protections).

(See time budgets pattern: `108-service-standards-and-time-budgets.md`.)

---

## Minimal metrics (publishable)

Track:
- % audits published by deadline; median days to publish
- % findings with `MRR-*` in window
- implementation rate at 6/12/24 months; repeat‑finding rate
- “scope exclusions” count and distribution (capture sensor)
- escalation trigger frequency (should fall over time if follow‑through works)

---

## Joins (how this stays small)

- Join `AFR-*` ↔ budget/procurement: tag affected programs and contracts (`110`).
- Join `AFR-*` ↔ rulemaking: when findings imply rule failure, file a `RCR-*` proposal (`118`).
- Join `AFR-*` ↔ control loop: treat each material finding as an incident in `104` postmortem logic.
- Join whistleblowing lanes to oversight intake (`121`).

---

## Failure modes checklist (quick)

If oversight is “present” but ineffective, look for:
- no publication default (or endless drafts)
- findings without owners/budgets/deadlines
- selection opacity (no `APR-*` or sampling receipts)
- retaliation risk (no protected disclosure lanes)
- repeat findings with no escalations

---

## References (citation keys)

- [BIB-INTOSAI-P10], [BIB-INTOSAI-P1], [BIB-ISSAI-100].
