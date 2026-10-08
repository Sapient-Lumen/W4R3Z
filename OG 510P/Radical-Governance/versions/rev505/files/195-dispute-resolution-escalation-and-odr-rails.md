# Dispute Resolution, Escalation, and Online Dispute Resolution Rails

**Stack relation:** use `283-justice-and-redress-stack-routing-guide.md` for the canonical route across the justice/redress cluster. This memo is the escalation and dispute-routing layer; `08` sets remedy floors; `36` makes lanes discoverable; `76` handles recurring patterned harms.

**Aim:** prevent “ping‑pong”, dead ends, and high-friction appeals by making dispute resolution a **joinable interface** across agencies and scopes.

This memo complements:
- `36-appeal-lanes-and-redress-registry.md` (person-facing lanes)
- `114-interjurisdictional-dispute-and-coordination.md` (cross-scope coordination)
- `172-administrative-justice-complaints-ombuds-mesh.md` (ombuds mesh)

It adds a missing piece: **escalation architecture** and a minimal **ODR (online dispute resolution)** pattern that is fair, auditable, and non-exclusionary.

---

## 1) Non‑negotiables

1) **One front door**: every dispute begins in a single discoverable intake surface (in-person + phone + paper + digital), with translation and accessibility.

2) **No wrong door**: if the wrong agency receives the claim, it must **route** it and issue a **Routing Receipt** with the new owner and deadlines.

3) **Clocks are binding**: every lane has time budgets, escalation triggers, and an explicit “deemed denial / deemed acceptance” rule where appropriate.

4) **Evidence doesn’t reset**: evidence already produced must not be re‑requested without a reason and a reference to what changed.

5) **Every step is receipted**: a person (or counterparty) can always prove what happened.

---

## 2) Three dispute planes

### A. Person ↔ Institution (administrative justice)
**Default stack:** front-door intake → case officer review → supervisor review → independent complaints/ombuds → tribunal/court.

**Must emit artifacts**
- **Intake Receipt (INT‑*)**: claim summary, requested remedy, scope, urgency tag.
- **Routing Receipt (RTE‑*)**: if re-assigned, includes justification + new clock start.
- **Evidence Receipt (EVD‑*)**: submitted items + authenticity basis + access controls.
- **Decision Receipt (DRR‑*)**: reasons, rule-as-of, appeal lane, deadlines.
- **Escalation Receipt (ESC‑*)**: why escalated, who now owns it, and what changes.

### B. Institution ↔ Institution (agency disputes)
Use a **bounded interagency compact**: a standing mechanism with:
- a joint chair (rotating)
- a neutral secretariat
- shared docket + clock discipline
- mandatory “best evidence so far” exchange

**Trigger:** dispute prevents delivery of a statutory service / blocks a rights claim.

### C. Scope ↔ Scope (intergovernmental / interjurisdictional)
**Core idea:** treat cross-scope disputes as an **operations problem** with a formal escalation ladder.

Minimum ladder:
1) **Operational fix window** (short) — technical teams resolve using shared facts.
2) **Policy/mandate window** — designated officials resolve within mandate.
3) **Neutral review** — ombuds/inspectorate/arbitrator with authority to issue a binding directive *or* a binding interim measure.
4) **Judicial/constitutional lane** — for foundational conflicts.

**Anti‑ping‑pong rule:** if more than N transfers occur or deadlines are missed, the case auto-escalates to the neutral review level.

---

## 3) Online Dispute Resolution (ODR) as an interface, not a platform

ODR should be designed as a **seamless transfer layer** across dispute mechanisms (negotiation → mediation → ombuds → tribunal), not as a single privatized “app”. The OECD’s ODR framework emphasizes governance, legal robustness, and ethical standards to ensure fairness and transparency, and highlights the need to support transfers across mechanisms.

### ODR minimum requirements
- **Multi-channel parity:** everything doable online must be doable offline.
- **Identity without exclusion:** allow strong identity when available, but support assisted access and paper attestations.
- **Explainability of process:** the system must show “where your case is” + what happens next.
- **Auditability:** immutable event log for submissions, notices, proposals, decisions.
- **Fairness & power safeguards:**
 - informed consent for mediation
 - safe refusal
 - ability to request a human hearing
 - accessibility and language support

### ODR transfer protocol (ODR‑TX)
Define a minimal schema that every mechanism can accept:
- parties + representatives
- claim + requested remedy
- timeline + notices
- evidence bundle pointers
- offers / proposals history
- confidentiality boundary flags

---

## 4) Design pattern: escalation clocks + “deemed” rules

**Why:** many systems fail not because the law is bad, but because stalling is rational.

Minimum set:
- **Response clock** (initial acknowledgement)
- **Investigation clock**
- **Decision clock**
- **Escalation clock** (missed → auto escalation)

**Deemed rules (use selectively):**
- *Deemed denial* enables appeal when an agency does not act.
- *Deemed approval* can be appropriate for low-risk permits when agency delay is the primary harm.

---

## 5) “Emergency mode” guardrails for dispute resolution

During emergencies, dispute resolution must not be silently suspended.

- Publish an **Emergency Dispute Protocol**: what changes, what does not.
- Maintain an **urgent lane** for life, liberty, housing, benefits, and essential services.
- Require time limits, oversight, and proportionality for emergency measures; the Venice Commission compiles standards emphasizing compatibility with democracy, human rights, and rule of law in emergency contexts.

---

## 6) Implementation checklist (tight)

1) Publish lanes in `36-appeal-lanes-and-redress-registry.md` + link from every decision surface.
2) Add Routing Receipts + anti-ping-pong rule to `114-interjurisdictional-dispute-and-coordination.md`.
3) Stand up ODR‑TX schema + event log (can start as a spreadsheet + email receipts).
4) Add a public dashboard: clock compliance, transfer counts, escalation frequency.

---

## 7) Minimal tests to add (see `107-governance-test-suite.md`)

- **Dispute joinability:** can evidence and timelines transfer across mechanisms without reset?
- **No wrong door:** does the system route and receipt instead of rejecting?
- **Anti‑stall:** do clocks and escalation triggers actually bind?

