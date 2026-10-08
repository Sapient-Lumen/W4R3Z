# Service Standards & Administrative Time Budgets (Turn Delay into an Enforceable Interface)

**Purpose:** treat *administrative time* as a governed resource: delay is a form of power that silently denies rights and shifts burdens onto the person.

**From-below thesis:** if a person can’t predict **how long** a decision will take, **why** it’s delayed, and **what happens** when the deadline is missed, they are not being governed—they are being *queued*.

(See: control loops `104-governance-control-loops.md`; legitimacy receipts `106-legitimacy-protocols.md`; remedy lanes `08-remedy-and-grievance.md`; approvals systems `29-permissioning-and-approvals.md`; public service capacity `09-public-service-and-state-capacity.md`; records/FOI `31-records-foi-and-government-memory.md`; budget levers `07-fiscal-and-budgetary-governance.md`.)

---

## The minimum “service promise” (per service, per channel)

For each public-facing service (permit, benefit, inspection, complaint, registration), publish a **Service Promise** with:

1) **Scope + eligibility** (who it is for; what is excluded; where discretion exists).
2) **Steps + required inputs** (and *what the government will fetch itself*).
3) **Time budget** (P50/P90 completion targets + maximum legal deadline).
4) **Reasons receipt** for delay (standard codes + free-text explanation).
5) **Escalation + contest lane** (how to force a response; standing rules).
6) **Non-response consequence** (what happens at the deadline: auto-approve, interim protection, or mandatory supervisor review—never “nothing”).

These are **interface obligations**, not aspirations. They bind staff planning and budget, and they give the person leverage.

Related patterns: Citizen Charters / service standards (see [BIB-UK-SERVICE-STANDARD], [BIB-OECD-SERVICE-DESIGN-DELIVERY], [BIB-WB-CITIZEN-CHARTERS]).

---

## Deadline mechanics (make time enforceable)

### A. “Silence is a state”
Every case must be in one of these states, visible to the person:

- **Received** (clock starts; missing items listed; no hidden review).
- **In review** (who owns it; what is being checked; expected date).
- **Paused (needs input)** (clock stops *only* when the person is asked for something specific).
- **Decision issued** (with decision receipt + appeal lane).

### B. Missed deadline triggers (choose per risk class)
When the clock hits the **maximum deadline**, an automatic trigger must fire:

- **Auto-approve** (low externality, high backlog risk; e.g., simple registrations).
- **Interim protection** (benefits/services continue pending review; prevents “starve-out”).
- **Mandatory escalation** (supervisor + independent reviewer within N days).
- **Automatic disclosure** (publish backlog + reasons + mitigation plan).

This is the “time circuit breaker” version of `105-institutional-circuit-breakers.md`.

### C. Compensation / fee shifting
For high-impact services (benefits, licenses, housing, safety), missed deadlines should have *non-symbolic* consequences:

- fee waivers / refunds
- compensatory payments for proven harms
- fee shifting (agency pays costs for late processing)

Treat this as an *anti-backlog incentive* and a fairness repair tool (tie to `08` and `07`).

---

## What to publish (minimum viability)

Publish a public dashboard (monthly at minimum) per service:

- volumes: received / resolved / pending
- **age distribution** (P50/P90/P99)
- reasons for pause/delay (standard codes)
- outcomes (approve/deny/partial) + appeal outcomes
- staffing capacity vs demand (at least headcount bands)
- equity slices where safe and lawful (without exposing small cells)

Tie publication to the archives’ **records discipline** (`31`) and **metrics** (`03`).

---

## Design moves that reduce delay without hiding it

1) **Default data minimization:** require the *fewest* inputs; pre-fill what the state already knows (`33-data-protection...`).
2) **One problem, one journey:** remove “ping-pong” by assigning a primary case owner (`98-persons-path...`).
3) **Risk-tier review:** separate low-risk fast lanes from high-risk scrutiny; publish the tiers.
4) **Stop-the-line:** if backlog crosses a threshold, pause discretionary new programs / intake until capacity is restored (`105`).
5) **Budget for obligations:** time budgets must be funded; unfunded mandates are illegitimate (`07`, `18-intergovernmental-finance.md`).

---

## Tests (plug into `107-governance-test-suite.md`)

- **Contestability:** can a person force a response before harm occurs?
- **Non-response consequence:** what happens at the deadline (not “file a complaint”)?
- **Backlog integrity:** do metrics show age distribution, not just averages?
- **Anti-discretion drift:** do pause codes prevent “infinite requests for more info”?
- **Cross-scope join:** when a case is transferred, does the clock follow the person (`35-transfer-register-and-conditionality.md`)?

---

## Where this belongs by scope (shortcut)

- **Micro-local / municipal:** counter service, inspections, local permits, complaints.
- **Regional / national:** benefits, licensing, immigration/status, major infrastructure approvals.
- **Global / transnational:** *service standards for institutions that bind people* (e.g., humanitarian aid, refugee processing): publish clocks, contest lanes, and missed-deadline triggers.

(Use `103-scope-cards.md` to assign ownership and escalation paths.)

