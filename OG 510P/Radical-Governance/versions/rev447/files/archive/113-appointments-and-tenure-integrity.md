# Appointments and Tenure Integrity (AIP)

**Purpose:** Treat *personnel* as a primary capture surface: appointments, acting authority, removals, and board stacking.

**Person served:** People affected by the institution’s decisions (who need predictable, contestable authority) and staff (who need anti‑retaliation removal discipline).

**Core claim:** If you can silently swap decision‑makers, you can change outcomes without changing law. Appointments require the same legibility‑with‑bite as rules.

---

## AIP: minimal protocol

### 1) Role inventory (public)
- Maintain a **Role Register** of all authority‑bearing roles (policy, adjudication, enforcement, procurement, inspection, data access).
- Each role entry MUST include: scope, powers, non‑delegables, conflict rules, term/tenure type, removal standard, and oversight hooks.

### 2) Appointment Receipt (`ADR-*`) for every authority‑bearing appointment
Each appointment MUST produce an **Appointment Decision Receipt** that is public by default (with redactions only for narrow safety reasons).

**Minimum fields:**
- **Role:** `ROLE-*` identifier; authority scope; non‑delegables.
- **Selector:** who appointed; legal basis.
- **Process:** method (e.g., election / merit list / nomination+confirmation / lottery / rotation); dates.
- **Qualifications:** stated criteria; how assessed.
- **Conflicts:** disclosures + recusal plan.
- **Term:** start/end; renewal rules.
- **Removal:** standard + procedure + appeal channel.
- **Standing & contest window:** who can contest and by when (see `106-legitimacy-protocols.md`).

### 3) Acting authority is time‑bounded (no “acting forever”)
- **Acting** appointments MUST be explicitly labeled and **hard time‑bounded**.
- If an acting appointment exceeds the bound, a **circuit breaker** MUST trigger: automatic escalation to independent review + publication of reasons + interim constraints on the acting role’s non‑delegables. (See `105-institutional-circuit-breakers.md`.)

### 4) Removal discipline (anti‑retaliation)
- For roles that protect rights or control coercion/spend, removal MUST be:
  - **Reasoned** (removal receipt),
  - **Contestable** (standing + timeline + interim protection),
  - **Protected** against retaliation for lawful dissent, whistleblowing, or adverse findings (see `83-whistleblowing-and-protected-disclosures.md`).

### 5) Anti‑stacking constraints
- Prevent rapid mass replacement (“stacking”) by requiring **staggered terms** for boards/commissions where feasible.
- Where rapid turnover is legally permitted, require an explicit **Stacking Notice**: impact analysis + continuity plan + oversight trigger.

---

## Failure modes (and fixes)

- **Capture by acting roles:** enforce hard acting bounds + publish ADRs.
- **Quiet purge:** require removal receipts + contest windows + interim protections.
- **Board stacking:** stagger terms; stacking notice + oversight trigger.
- **Shadow authority:** role inventory + non‑delegables + delegation receipts.

---

## Cross-links

- Legitimacy receipts + standing/contest windows: `106-legitimacy-protocols.md`
- Circuit breakers: `105-institutional-circuit-breakers.md`
- Emergency powers (acting expansions): `112-exception-control-and-emergency-powers.md`
- Information/records (publish ADRs + change logs): `115-information-integrity-and-record-interfaces.md`

**See also:** `163-integrity-stack-anti-corruption-rails.md` (conflict-of-interest + revolving-door rails).
