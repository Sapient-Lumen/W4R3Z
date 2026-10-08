# Civil Service Merit & Capacity Rails (Recruitment, performance, depoliticisation)

**Stack relation:** use `297-state-capacity-appointments-and-agency-independence-routing-guide.md` for the canonical route across the state-capacity / appointments / agency-independence cluster. This memo is the merit recruitment / workforce capability / depoliticisation rails layer; `09` is the broader state-capacity front door; `113` handles appointment / acting / removal integrity; `228` handles board-governance and other high-discretion appointment packets; `229` handles agency / regulator independence surfaces.

**Purpose:** treat the *administrative state* as a safety‑critical system: hire, promote, and operate in ways that preserve **capability**, **impartiality**, and **learning**, while resisting patronage and capture.

**Person served:** anyone who needs public services to work *today* (benefits, permits, policing constraints, courts, infrastructure), and needs the machinery of government not to swing wildly with factional turnover.

**From‑below:** citizens and frontline staff need **challengeable hiring/promotion decisions**, **safe reporting channels**, and **observable service capacity**—so the civil service can be trusted without being worshipped.

## A. Threat model (what breaks capacity)

1. **Patronage & politicisation:** jobs traded for loyalty; purges; “acting” appointments to bypass merit.
2. **Capture via revolving doors:** policy and procurement shaped by anticipated private rewards.
3. **Capability rot:** pay compression, unmanaged skills gaps, no training, no incident learning.
4. **Fear culture:** retaliation for reporting; corruption becomes invisible.
5. **Opacity:** nobody can see staffing levels, vacancy duration, or service backlogs—so failure has no owner.

## B. Design invariants

- **Merit is legible:** criteria are published, job‑relevant, scored, and auditable.
- **Impartiality is protected:** clear boundary between political direction and professional execution.
- **Capacity is measured:** time‑to‑hire, vacancy rate, backlog age, error rate, attrition—public by default.
- **Integrity is enforced:** conflicts‑of‑interest and revolving‑door controls with real consequences.
- **Learning loop exists:** after‑action reviews and training pipelines are mandatory for high‑risk functions.

These align with public‑integrity guidance emphasizing merit‑based HR as a core integrity control.

## C. Core rails

### C1. Recruitment rails (open, scored, contestable)
- **Open posting** for all roles above a low threshold; exceptions require written justification.
- **Published rubric** (skills, experience, values, job simulation) and **structured interviews**.
- **Independent observers** for senior roles; randomised audit sampling of hiring files.
- **Time‑bound hiring SLOs** (e.g., shortlist within N days; decision within M days), with backlog reporting.
- **Candidate challenge window**: brief appeal lane for process violations (not “I disagree with judgement”).

Evidence and guidance on merit-based recruitment and the tradeoffs between career‑ and position‑based systems can be drawn from recruitment reform literature and governance notes.

### C2. Promotion & performance rails (avoid both stagnation and purge)
- **Promotion criteria** must include demonstrated competence, ethics, and service outcomes—not patronage.
- **Rotation limits** for sensitive roles (procurement, inspectors, licensing, enforcement) to prevent local capture.
- **Protected professional standards bodies** (job‑family councils) publish competency frameworks and training paths.

### C3. Depoliticisation boundary (two‑track governance)
- **Political track:** elected officials + political appointees set goals and priorities.
- **Professional track:** career officials execute within law; protected from arbitrary dismissal.
- **Written “direction receipts”**: when political leadership directs a major change, it is logged (who, what, why, legal basis), enabling later accountability.

### C4. Integrity & revolving‑door controls
- **Entry/exit disclosure** for senior officials: assets, affiliations, outside income.
- **Cooling‑off periods** (role‑dependent) + “no‑switch” rules for vendors recently overseen.
- **Lobbying and influence integrity** rules should be explicit and enforceable.

### C5. Safety and reporting culture
- **Protected disclosure** channel with external routing options and retaliation penalties.
- “Do you feel safe reporting?” becomes a tracked metric (survey + case outcomes), consistent with survey evidence on reporting fear.

## D. Minimal registers (keep this tight)

- **`HR-*` Workforce ledger:** headcount by function, vacancies, time‑to‑hire, attrition, pay bands (aggregated).
- **`HIR-*` Hiring decision record:** rubric, panel, scores, exception flags (redacted where needed).
- **`COI-*` Conflict & revolving‑door register:** disclosures, recusals, cooling‑off enforcement events.
- **`TRN-*` Training & certification ledger:** mandatory quals for high‑risk functions; expiration dates.
- **`CAP-*` Capacity incidents:** when service SLOs break, record cause, corrective action, follow‑through.

Use the same publication integrity + tamper‑evident logs discipline already in the archive.

## E. Evaluation questions (fast checks)

1. Can a citizen see **how long it takes** to hire for critical roles and whether vacancies are rising?
2. Are hiring exceptions rare, justified, and audited?
3. Are promotion outcomes correlated with performance and competence (not faction)?
4. Do COI/revolving‑door violations show real enforcement events?
5. Do capacity incidents trigger **root‑cause analysis** and operational fixes?

## F. Hooks into the archive

- State capacity framing: `09-public-service-and-state-capacity.md`.
- Integrity system blueprint: `187-public-integrity-system-blueprint.md`.
- Whistleblowing rails: `121-whistleblowing-and-protected-disclosure.md`.
- Procurement rails: `179-open-contracting-and-procurement-rails.md`.
- Influence integrity rails: `181-influence-lobbying-transparency-and-integrity-rails.md` + `187-public-integrity-system-blueprint.md`.

## G. Governance tests to add

- **T3.8 Merit recruitment legibility:** rubrics published; structured scoring; appeal lane exists.
- **T3.9 Depoliticisation boundary:** clear political/professional delineation; direction receipts logged.
- **T3.10 Revolving‑door enforcement:** cooling‑off rules exist and violations are recorded with consequences.
