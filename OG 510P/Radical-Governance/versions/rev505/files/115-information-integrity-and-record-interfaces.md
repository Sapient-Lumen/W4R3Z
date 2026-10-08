# Information Integrity & Public Records Interfaces

**Purpose:** make *information power* legible and contestable: records exist, disclosures happen on time, and algorithmic decision systems are registrable and reviewable (without turning transparency into theater or a weapon).

**Person served:** anyone who needs records to contest a decision, prove eligibility, prevent retaliation, or understand how an automated/assisted decision was made.

**From-below:** if the state (or platform-like public service) can act without leaving a trail, people lose by default. This memo defines a **small portable interface** that makes “paper trail” a rights-bearing object.

---

## The minimum interface (portable across scopes)

### 1) Record Capture Floor (RCF)
A governed person MUST be able to obtain a **stable record pointer** for any materially adverse or eligibility-determining action.

- **RCF-1 Stable IDs:** each decision/action creates a stable ID (human-readable + machine).
- **RCF-2 Decision Receipt join:** RCF MUST join to the Decision Receipt pattern (see `106-legitimacy-protocols.md` and `111-deliberation-to-decision-binding.md`).
- **RCF-3 Evidence bundle:** the record MUST include (or point to) inputs considered, policy basis, and a minimal audit trail (who/what system touched it).
- **RCF-4 Retention discipline:** retention schedules MUST be public; destruction MUST be logged; *missing record* is a reportable incident.
- **RCF-5 Adverse inference:** if a required record is missing, default presumption shifts toward the governed person unless the authority proves good‑faith loss and offers a remedy.

**Compatibility note:** this extends `31-records-foi-and-government-memory.md` with an explicit “stable pointer” floor.

### 2) Disclosure Clock (DC)
“Transparency” fails when it is late. Disclosures MUST have clocks and triggers.

- **DC-1 Publish-by defaults:** classes of records (budgets, contracts, audits, policies, performance metrics) have a *publish-by* deadline. See `108-service-standards-and-time-budgets.md`.
- **DC-2 Deadline miss triggers:** when publish-by is missed, trigger a circuit breaker: auto-escalation, interim publication, or mandatory external audit (`105-institutional-circuit-breakers.md`).
- **DC-3 Redaction receipts:** redactions MUST produce a reason receipt that cites the exemption, scope, and a review path.

### 3) RTI / FOI Request Receipts (RR)
A request for records is itself an enforceable transaction.

- **RR-1 Request ID + due date:** every request yields a stable ID and statutory clock.
- **RR-2 Narrowing offers:** authorities MUST offer narrowing options that do not waive rights.
- **RR-3 Denial reason receipt:** denials MUST cite exemption + harm rationale + appeal channel.
- **RR-4 Anti-retaliation guard:** requesters MUST be protected from adverse targeting; requests are *not* intelligence leads (see `98-persons-path-and-accessibility-invariants.md`).

Rights anchor: Tromsø Convention baseline (see [BIB-COE-TROMSO]) and general open government norms (see [BIB-OECD-OG]).

### 4) Algorithmic Decision Register (ADR)
If a system influences outcomes, it must be registrable.

- **ADR-1 Register scope:** any automated/assisted system used for eligibility, risk scoring, enforcement prioritization, or service triage MUST be listed.
- **ADR-2 Public card:** each entry publishes: purpose, decision points touched, data categories, evaluation summary (error/impact), human override/recourse, and contest path.
- **ADR-3 Change logs:** material model/rule changes are logged with effective dates and a backtesting note.
- **ADR-4 Independent access:** qualified external auditors (and ombuds) must be able to review under controlled access when full publication is unsafe.
- **ADR-5 “No secret law” rule:** if a system changes the practical meaning of a rule for the governed, the operative logic MUST be explainable in plain terms.

Compatibility notes:
- This does **not** require publishing exploitable details (safety constraint); it requires **registrability, accountability hooks, and contest paths** (see `112-exception-control-and-emergency-powers.md` for exceptions discipline).

---

## Minimal metrics (so this stays real)

- **Record availability:** % of adverse actions with a stable RCF pointer issued at time of action.
- **FOI performance:** median/95p response time, denial rate, appeal win rate.
- **Redaction rate:** proportion of pages/items redacted; reversal rate after appeal.
- **Missing-record incidents:** count + remedy time.
- **ADR coverage:** % of outcome-influencing systems registered; audit completion rate.

---

## Failure modes & fixes (tight)

- **“Transparency theater”:** publishing dashboards with no contest lane → link OPEN to DEC receipts + RR appeals (`106`, `107`).
- **Weaponized disclosure:** FOI used to target requesters → anti-retaliation guard + access separation (`98`).
- **Administrative disappearance:** “we can’t find the file” → missing-record incident + adverse inference + remedy.
- **Model drift capture:** silent rule/model changes → ADR change log + backtesting note + contest window.

---

## References (archive keys)

- [BIB-COE-TROMSO] access to official documents (FOI rights baseline).
- [BIB-OECD-OG] open government principles (participation, transparency, accountability).
- [BIB-OECD-AI] OECD AI principles (accountability/transparency baseline).
- `31-records-foi-and-government-memory.md` (records foundation).
