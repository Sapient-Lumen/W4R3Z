# Procurement as a Governance Lever (with Guardrails)

**Purpose:** treat public procurement as a *constitutional* surface (not a back-office detail): spending decisions set market structure, labor conditions, service reliability, and corruption risk.

**Person served:** people who depend on public services and bear the harms of captured contracting (overpricing, safety failures, vendor lock‑in) and of poorly designed “policy procurement” (exclusion, retaliation, discriminatory burden).

**From-below:** so a resident can trace what was bought *for them*, challenge unfair exclusion or waste, and prevent procurement from quietly becoming a coercion or surveillance channel.

**Scope fit:** works at **every scope** that buys things; becomes **inter-scope** when procurement is pooled, subsidized, or used to implement compacts.

**Anchor set (start here):** Open Contracting Data Standard for joinable procurement disclosure [BIB-OCDS]; MAPS for system assessment and reform targeting [BIB-MAPS-MAIN-2018]; UNCAC for anti‑corruption obligations [BIB-UNCAC].

---

## A. Why procurement is “government”
Public procurement is where abstract values become **award decisions** (who gets paid), **delivery risk** (what fails), and **market shape** (who can compete). It is a *high‑leverage* surface for:

- **Integrity:** bribery, bid rigging/collusion, conflicts, shell companies (see `155-illicit-finance-and-kleptocracy-defense.md`).
- **Service reliability:** maintenance, spare parts, uptime obligations (`82-service-standards-and-minimum-service-guarantees.md`).
- **Industrial policy & resilience:** diversifying suppliers, strengthening critical inputs (`153-industrial-policy-and-supply-chain-resilience.md`).
- **Rights & inclusion:** accessibility, non-discrimination, living-wage compliance.
- **Digital governance:** software procurement shapes data rights, auditability, and vendor lock‑in (`70-interoperability.md`, `73-assurance-case-and-governance-safety-case.md`).

The design question is not “how to buy cheaply,” but **how to buy in a way that is contestable, resilient, and rights‑protecting**.

---

## B. The procurement constitution (minimal guarantees)
These are the smallest rules that keep procurement from becoming a capture machine.

### 1) Publish a joinable contracting register (`OPEN-2`)
- MUST: a contracting register with stable IDs for planning → tender → award → contract → implementation.
- SHOULD: publish OCDS releases or an OCDS‑compatible subset where feasible [BIB-OCDS].
- MUST: link contracts to **budget/execution** lines (`07-fiscal-and-budgetary-governance.md`) and to **delivery evidence** (milestones, acceptance, change orders) to prevent “award transparency” without “delivery truth.”

### 2) Competition defaults + justified exceptions
- MUST: competitive tender as default.
- MUST: a documented exception process for single-source/urgent awards (receipt + time-bounded + post‑hoc review).
- SHOULD: keep exception categories narrow and auditable (ties into `85-waivers-variances-and-exceptions-discipline.md`).

### 3) Conflict-of-interest + revolving-door discipline
- MUST: COI disclosures and recusal rules for procurement officials and evaluation committees (`79-conflict-of-interest-and-revolving-door-discipline.md`).
- SHOULD: vendor debarment rules with due process and sunset/review lanes.

### 4) Beneficial ownership & shell-company defenses
- SHOULD: beneficial ownership disclosure and verification for contract recipients where lawful/feasible, with a correction lane and audit hooks [BIB-BODS], [BIB-FATF-BO-2023].

### 5) Remedy that actually works
- MUST: an accessible bid-challenge lane and a resident/user complaint lane for delivery failures (`08-remedy-and-grievance.md`).
- SHOULD: publish aggregate stats for protest outcomes, delays, and repeat issues (protective legibility: `99-protective-legibility-and-adoption-dynamics.md`).

---

## C. “Policy procurement” without capture (how to use leverage safely)
Governments often want procurement to advance goals (labor, climate, security, inclusion). This can work, but it can also become a **pretext** for favoritism. Use these guardrails:

### 1) Separate *eligibility floors* from *award scoring*
- **Floors**: hard constraints that apply to all (e.g., accessibility compliance; wage floors; safety certifications).
- **Scoring**: transparent tradeoffs (e.g., lifecycle cost; emissions; local capacity) with published weights.

### 2) Prefer measurable performance clauses over vague promises
- Use verifiable deliverables and acceptance tests; require change orders to be publishable and justified.
- For digital procurement: require auditability, exportability, and “no-silent-change” controls (`73`, `74`).

### 3) Modularize to reduce lock‑in
- Break mega-contracts into interfaces and modules where feasible.
- Require portability and data export requirements (`70-interoperability.md`).

### 4) Anti-retaliation publication discipline
Publishing must not become a retaliation channel for whistleblowers or small vendors. Use `99-protective-legibility-and-adoption-dynamics.md` patterns.

---

## D. Early-warning detection (red flags, not vibes)
Use **risk indicators** as triggers for audits and remedy (not as automatic guilt).

- SHOULD: compute and publish (at least internally) procurement “red flag” indicators to detect risks of collusion, favoritism, and abuse, mapped to OCDS fields where applicable [BIB-OCP-REDFLAGS-2024].
- SHOULD: define escalation thresholds: when red flags trigger a targeted review, a pause, or an inspection lane (`81-verification-inspection-and-compliance-ladders.md`).

Key design point: red flags must connect to a **decision loop** (investigate → correct → publish closure), otherwise they become dashboards that normalize failure.

---

## E. Assess and reform the system (MAPS)
Procurement failures are often systemic: unclear rules, weak professionalization, missing e‑procurement, or toothless oversight.

- SHOULD: periodically assess the procurement system using MAPS (main methodology + modules such as e‑procurement and professionalization) and publish the reform plan [BIB-MAPS-MAIN-2018].
- SHOULD: align donor/IFIs and inter-scope procurement requirements to avoid duplicative rule stacks that increase burden without improving integrity.

---

## F. Inter-scope procurement (pooled buying + compacts)
When multiple scopes buy together (health, infrastructure, emergency supplies), governance must prevent two common failure modes:

1) **Buck‑passing:** unclear authority for dispute, acceptance, and payment.
2) **Centralized capture:** one procurement unit becomes a gatekeeper.

Minimum:
- MUST: a compact that defines decision rights, exception rules, audit authority, and dispute lane.
- SHOULD: publish a cross-scope “money map” (who pays; who signs; who accepts) (`18-intergovernmental-finance.md`).

---

## G. Minimal metric set (portable)
Tie each metric to a governance action.

- **OPEN coverage:** % of awards/contracts published with joinable IDs (OCDS fields where applicable) [IPM-PROC-1].
- **Exception rate:** % spend via non-competitive awards + time-to-review [IPM-PROC-2].
- **Change-order load:** change orders as % of contract value + clustering by vendor/agency [IPM-PROC-3].
- **Delivery truth:** % contracts with acceptance evidence and completion/termination status [IPM-PROC-4].
- **Challenge effectiveness:** protests resolved within X days + remedy rate + retaliation indicators [IPM-PROC-5].

(If you don’t have a loop for these, don’t collect them yet—build the loop first.)
