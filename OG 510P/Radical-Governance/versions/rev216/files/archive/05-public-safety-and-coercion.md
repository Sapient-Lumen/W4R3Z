# Public Safety & Coercion (Minimum-Violence Governance)

**Purpose:** constrain coercive power so safety actions remain receipted, reviewable, and less lethal—especially for those most targeted.

This memo specifies *minimum viable* governance for institutions that can **use force**, **detain**, or otherwise coerce. It is intentionally short and plugs into `02-design-toolkit.md` (`SAFE-*`, `LAW-*`, `ACC-*`, `OPEN-*`).

**See also:** `24-mutual-aid-and-serious-incident-protocol.md` (mutual aid + independent serious-incident pipeline), and `43-enforcement-and-custody-event-register.md` (joinable coercion logs + custody episodes).

**Design objective:** maximize safety and compliance while minimizing violence, abuse, politicization, and error.


## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- `01-principles.md` (legibility vs safety; transparency vs retaliation)
- `98-persons-path-and-accessibility-invariants.md` (person’s path)
- `83-whistleblowing-and-protected-disclosures.md` (protected disclosures)
- `77-sensitive-information-and-secrecy-governance.md` (secrecy/redaction discipline)
- `32-oversight-institutions-and-follow-through.md` (follow‑through)

## Named tensions (design must surface these)
- Speed vs due process.
- Transparency vs operational/security risk.
- Legibility of coercion vs retaliation risk for witnesses/complainants (see [TM-29]).
- Receipts/logs vs toothless enforcement (“legibility theater” inside coercive institutions) (see [TM-33]).
- Default to **joinable public summaries + redaction discipline + independent review**, not to silence.
- Structural independence vs institutional culture: the issuer of receipts sits inside the force‑wielding institution; independence is necessary but not sufficient. The archive can design safeguards; it cannot design culture.

## 1) Non-negotiable constraints (always-on)
- **Legality:** coercion must have a clear legal basis and an auditable decision trail (`LAW-1/2`, `OPEN-1`).
- **Necessity + proportionality:** force is last resort; the least harmful effective means (`SAFE-1`).
- **Accountability:** every serious incident is reviewable and produces learning (not just punishment) (`SAFE-2`, `03-metrics-and-evidence.md`).
- **Humane custody:** detention is safe, monitored, and time-bounded (`SAFE-4`).
- **Non-partisanship:** coercive institutions cannot become tools of factional control (`SAFE-5`, `ACC-4`).

**Culture boundary:** structural safeguards (independent oversight, logs, lanes) are necessary but not sufficient. Whether they are used or evaded depends on institutional norms and internal narratives. Treat **dignity discipline** and **retaliation control** as part of coercion governance capacity (`09-...`, `83-...`).


Anchors: see [BIB-UN-UOF]; [BIB-UN-LEO-CODE]; [BIB-MANDELA-RULES]; [BIB-ISTANBUL-PROTOCOL].


## 1a) Coercion receipts + event logs (no dark enforcement)

- **Person-facing usability is non-optional:** coercion receipts MUST satisfy the comprehension + accessibility invariants (plain language in the person’s language; what happened/why/what next; disability access). If a representative user cannot identify the deadline and next step, the format MUST be revised, not merely appended. See `98-persons-path-and-accessibility-invariants.md` and `31-records-foi-and-government-memory.md`.
- **Fear is a defect:** complaint paths MUST be safe to use (anti-retaliation posture + protected channels). A remedy people are afraid to use is not a remedy. See `08-...`, `98-persons-path-and-accessibility-invariants.md`, and [TM-29].
- **Representation duty:** where the affected person cannot realistically contest (children, severe incapacity, custody without counsel), the system MUST provide/trigger an independent advocate or equivalent representation channel. (`98-persons-path-and-accessibility-invariants.md`, `36-...`)
- Any action affecting liberty/property/bodily integrity MUST generate (1) a person-facing receipt (linked `DRR`) and (2) an `ENF-*` event record.
- Receipts/logs cite `RULE-*` basis (**as-of**) and publish the complaint/review lane `AL-*` (see `36-...`).
- Custody episodes are logged start→end with welfare/medical checkpoints (see `43-...`).

## 2) Minimum institutional architecture (portable across scopes)

### A) Mandates and separation
- Police: public order + investigation, *not* political intelligence.
- Intelligence: bounded by law, higher authorization thresholds, and stronger oversight.
- Military: external defense; domestic use is exceptional and tightly constrained (`SAFE-3`).
- Prosecution: independent from police command; transparent charging standards (UN Guidelines on Prosecutors) [BIB-UN-PROSECUTORS]
- Defense bar independence + access (UN Basic Principles on Lawyers) [BIB-UN-LAWYERS]

### B) Use-of-force governance (“serious incident” pipeline)
- Codify the force standard (necessity/proportionality + de-escalation) and publish the policy (`SAFE-1`).
- Define a **serious incident** class (death, serious injury, firearm discharge, custody death).
- Require: scene preservation + independent investigation + public summary + policy update loop.
- Implementation reference: see [BIB-UNODC-UOF-RB].

### C) Complaints and independent oversight
- One door for the public (accessible, multilingual, protected from retaliation).
- Each complaint/discipline path MUST be discoverable as an `AL-*` lane in the Redress Registry (ALR) (so deadlines, interim protection, and escalation are legible).
- Independent investigators with access to records (including video) and referral power (`SAFE-2`, `ACC-3`).
- Publish aggregate findings: patterns, discipline rates, policy changes (not personal data dumps).

### D) Custody & detention safeguards
- Counsel access and time limits + judicial review.
- Medical intake + continuity of care; disability accommodations.
- Recording of interviews; shift away from confession-driven interrogation toward rapport-based interviewing.
- Independent inspections of all detention sites, including short-term holding.
- Anchors: see [BIB-MANDELA].
  OPCAT (treaty): see [BIB-OPCAT]; NPM overview (OHCHR): [BIB-UN-SPT-NPM]  
  Méndez Principles (2021): see [BIB-MENDEZ-2021].

### E) Emergency operations (riots, disasters, terrorism)
- Use `SAFE-3` emergency powers protocol (see `23-emergency-governance-and-exceptions.md`); keep a public Emergency Measures Register / exceptions ledger.

- If events drift toward violence without accountability, prioritize **preserving the record** (coercion/custody logs, receipts, as‑of access, and mirrored bundles; see `53-publication-integrity-and-tamper-evident-logs.md`).
- Post-event: after-action report + independent review + compensation/remedy path (`LAW-2`, `SAFE-3`).

## 3) Interfaces across scopes (who owns what)

- **Assurance case:** coercive powers SHOULD be covered by an `AC-*` governance safety case with monitoring + stop-conditions (see `73-assurance-case-and-governance-safety-case.md`).
- **Micro-local:** no coercive authority; focus on prevention, mediation, and liaison to municipal safety services.
- **Municipal:** daily policing policy + oversight + transparent data; local detention only with `SAFE-4` guarantees.
- **Regional:** mutual aid compacts with MASIP activation logs + independence rules (`19-...`, `24-...`); standards harmonization; specialized investigation capacity.
- **National:** constitutional constraints, nationwide standards, inspectorates, prosecution independence.
- **Supranational/global:** rights baselines, monitoring, and cross-border cooperation guardrails.

## 4) Common failure modes (and the simplest countermeasures)
- **Impunity loop:** weak investigations → repeat abuse → distrust → non-cooperation.  
  Counter: independent serious-incident pipeline + public learning loop.
- **Politicization:** selective enforcement/intimidation.  
  Counter: separation + protected oversight + transparent deployment rules.
- **Data suppression:** “no numbers, no problem.”  
  Counter: mandated publication + independent audit + external measurement anchors.
- **Custody harm:** torture/ill-treatment, deaths in custody, coercive interviewing.  
  Counter: inspection + recording + medical safeguards + due process.
