# 223 — Tabletop drills and governance red-teaming rails

**Purpose:** prevent “paper governance” by making institutions prove—in low-cost exercises—that rights, records, oversight, and remedy actually work under stress.

This is the governance analogue of incident-response practice: you don’t learn the system in the incident.

**Joins:** `04-threat-models.md`, `23-emergency-governance-and-exceptions.md`, `80-implementation-roadmap.md`, `84-internal-controls-and-continuous-assurance.md`, `32-oversight-institutions-and-follow-through.md`, `130-audit-and-inspection-integrity.md`, `154-critical-infrastructure-resilience-compacts.md`.

---

## A. The drill types (keep it small)

1) **Tabletop drill (TTX):** scenario walkthrough; validate roles, logs, deadlines, and escalation.
2) **Artifact drill:** attempt to execute a rights‑affecting action **without** producing required artifacts (decision receipt, rule pointer, queue classification, appeal lane) and measure detection.
3) **Exit drill:** prove you can terminate or replace a vendor/system without stranding people (joins `219`).
4) **Cross-scope drill:** exercise routing across the jurisdiction graph (`221`) and continuity (`109/114`).

---

## B. The “Receipts First” drill rule

Every drill MUST produce:

- an **Exercise Receipt** `EXR-*` (date, scenario, participants, scope)
- an **After-Action Review** `AAR-*` (what failed, why, fixes)
- **Fix Tracking** `OFR-*` entries for material failures (so findings can’t disappear)

No `AAR`, no credit.

---

## C. The minimum scenario set (per year)

- **Queue collapse:** sudden surge; test prioritization integrity (`140`) and interim protection (`82/85`).
- **Record mismatch:** upstream register error breaks downstream eligibility; test corrections propagation.
- **Secrecy claim:** request withheld; test withholding receipts + review lanes (`77/168`).
- **Capture attempt:** conflict-of-interest + vendor swap; test procurement and influence tripwires (`110/163/186`).

---

## D. Metrics (Goodhart-resistant)

Track:
- time to detect missing artifact
- time to produce a valid decision receipt
- time to route to the correct appeal/ombuds lane
- fix closure time (AAR → shipped fix)

**Prohibition:** don’t rank agencies by drill scores without gaming defenses; publish as learning indicators.

---

## E. Failure migration hook

If drills repeatedly fail for a scope (capability collapse), trigger the **Failure Migration Rule** (`176`): temporary upward support/assumption, remediation plan, restore authority after capability proof.
