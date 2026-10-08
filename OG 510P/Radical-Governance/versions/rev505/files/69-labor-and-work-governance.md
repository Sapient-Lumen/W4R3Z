# 69 — Labor & work governance (MVLWSG: decent work as auditable infrastructure)

**Stack relation:** use `299-social-protection-skills-work-and-worker-voice-routing-guide.md` for the canonical route across the social-protection / skills / work / worker-voice family. This memo is the labor-standards / enforcement front door; `64` is the income-security / benefits-delivery front door; `68` is the learning / capability / credentialing front door; `175` is the worker-voice / bargaining / codetermination institutional-carrier specialization.

**Purpose:** Treat labor standards, enforcement, and worker protections as a *joinable pipeline* rather than a scattered set of agencies, complaints, and court cases. The goal is not “more paperwork” — it is **predictable rights, measurable compliance, and contestable decisions** in a domain with persistent power asymmetry.

**Person served:** A worker facing wage theft, unsafe work, or retaliation who needs low‑risk complaint channels and recovery that actually happens.

**From-below:** This turns “decent work” into enforceable standards so wage theft, unsafe conditions, and retaliation have clear receipts and remedies.
**EXP pointer:** counters `EXP-05` (Fear) and `EXP-07` (Indifference) by making labor enforcement and retaliation risks contestable (`98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).

**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)
**Authority:** determinations/citations/remedies/sanctions MUST be issued as `DRR-*` with a binding contestation lane (`AL-*`) and oversight follow‑through for pattern failures (`36`, `32`, `55`, `76`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect workers and organizers from retaliation and enforcement entanglement; safe filing + anti‑retaliation monitoring + interim protections (`83`, `98`, `77`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)
**Mercy / interim protection:** where enforcement actions create immediate deprivation (job loss, work stoppage, immigration entanglement), define interim protection/stay triggers and auditable exceptions (`82`, `36`, `85`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**As-of & corrections:** decisions and receipts MUST state the as‑of basis (rules, data, releases) and MUST propagate corrections (reopen/undo downstream holds/penalties when upstream records change); do not strand people in stale status. (See `31-records-foi-and-government-memory.md`, `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)
**Proof burdens:** publish evidence classes and least‑burdensome alternatives; treat state-held payroll/inspection facts as once‑only retrievable; adverse outcomes cite `RC-*` + an `AL-*` lane (`47`, `44`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)

**Canonical move:** every rights-affecting labor action emits joinable artifacts:
- standards and wage rules are queryable “as‑of” (`RULE-*`, `STD-*`, PRR),
- determinations, citations, and remedies emit **decision receipts** (`DRR-*`) with portable reasons (`RC-LAB-*`) and clear remedy lanes (`AL-*`),
- inspections/investigations and sanctions are logged as joinable enforcement events (`ENF-*`),
- aggregate outcomes and methods are published as versioned releases (`REL-*`) with revision logs,
- recurring failures route into oversight follow‑through (`OFR-*`).

This memo composes with MVGS (`80-implementation-roadmap.md`) and the interfaces in `70-interoperability.md`.

**Countervailing power (don’t pretend inspection alone works):** labor governance only becomes contestable when workers can organize and safely use the infrastructure.
- Unions/worker orgs and legal aid SHOULD have **standing** to initiate representative complaints, pattern filings, and audits where individual filing is risky.
- Publish usable aggregate enforcement + wage‑recovery outcomes (`REL-*`), and provide controlled access to case-level evidence where lawful (`33-...`).
- Retaliation discipline is part of enforcement: complaints MUST be safe, and reprisals must route to enforcement + remedy (`98-persons-path-and-accessibility-invariants.md`, `08-...`).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (safe filing; offline/non-reading access), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Decision receipts (person-facing) default to `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- Protective legibility + power reality: `99-protective-legibility-and-adoption-dynamics.md` and [TM-29] (retaliation/fear collapses contestation).
- Retaliation/whistleblowing protections: `83-...` (safe reporting; interim protections).
- Enforcement/coercion logging and integrity controls (where the state acts): `43-...`, `05-...`, and publication integrity `53-...`.
- Systemic follow-through: `32-...`, `55-...`, and pattern remediation `76-...`.

## Named tensions (design must surface these)
- Visibility/enforcement vs worker safety (retaliation, migration entanglement, dependency).
- Flexibility/innovation vs basic protections (prevent “flexibility” from becoming arbitrage).
- Public disclosure of firms/violations vs due process + privacy (publish aggregates/methods where needed).
- Rapid hazard abatement vs procedural fairness (speed is safety; haste can be arbitrary power).
- Local enforcement discretion vs national floors/portability (avoid postcode labor rights).

### Adjacent-domain causal chain checks (labor ↔ benefits ↔ education)
Labor enforcement outcomes often propagate into benefits status and family stability, and can be suppressed by adjacent-domain coercion. When auditing or designing labor interfaces, explicitly check:
- benefits determinations (`64-...`) that depend on employment classification or wage records,
- education exclusion/attendance impacts (`68-...`) driven by work schedules, instability, or enforcement actions,
- migration enforcement entanglement (`67-...`) that chills reporting and shifts bargaining power.

(See `101-claude-rev142-normative-requirements.md` (NR-04).)

---

## A) What “labor & work” covers (scope)
This spine covers the *state’s role* in:
- wage-and-hour rules and recovery (minimum wage, overtime, payroll compliance)
- employment relationship/status determinations (employee vs contractor, joint employer, agency work)
- occupational safety/health and hazard abatement
- collective bargaining and freedom of association protections (where applicable)
- anti-retaliation protections for complaints and organizing
- algorithmic management constraints and contestability (where work is mediated by systems)

It does **not** attempt to be a full employment-law treatise. It specifies the **minimum public artifacts** required for auditability and remedy.

---

## B) Minimum Viable Labor & Work Spine (MVLWSG)

### B0) Public artifacts and where they live
**Rules and standards (publish “as‑of”):**
- Wage floors, working time rules, deductions, overtime rules, scheduling rules (if any): `RULE-*`
- Calculation methods (rates tables, overtime multipliers, pay-period rules), hazard standards, inspection protocols: `STD-*`
- Binding operational enforcement manuals/scripts/config tables: PRR entries (often flagged `GLAW`) with versioning (`39-rulebook-and-instruments-registry.md`)

**Journeys and channels (make access real):**
- Worker complaint intake (anonymous options where lawful), employer self-correction, inspection scheduling: `SRV-*` journeys (`47-service-catalog-and-access-journeys-register.md`)
- Publish **queue statistics** (median time to first contact, time to closure) as `REL-*` releases.

**Case events and receipts:**
- Complaint/inspection case opening → investigation steps → findings → remedies → closure:
 - Findings, status determinations, citations, penalty decisions, abatement orders, backpay calculations, settlement approvals: **emit `DRR-*`**
 - On-site inspections, evidence collection, interviews (when logged), citations issued, work stoppage orders: **log as `ENF-*`** and link to the authorizing/disposing `DRR-*`
 - Each `DRR-*` MUST include `RC-LAB-*` reason(s) + a discoverable `AL-*` lane (and deadlines) (`08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`)

**Employer / counterparty legibility:**
- Use **Entity Identifiers** (`EID`) for employers, labor contractors, and high-volume platforms so outcomes can be joined without doxxing (`70-interoperability.md`).

### B1) The labor decision object (what must be receipted)
For any rights-affecting labor action, issue a `DRR-*` with:
- **who**: the worker(s) (as protected identifiers) and employer `EID`
- **what**: decision type (status, finding, remedy, sanction, settlement approval)
- **why**: one or more `RC-LAB-*` reason codes (+ minimal free-text facts)
- **how computed**: wage arrears calculation method reference, penalty basis, standard/rule IDs (“as‑of”)
- **what next**: remedy lane(s) `AL-*` + deadlines; compliance/abatement timeline; escalation trigger
- **links**: related `ENF-*` events, supporting `REL-*` methods, and any relevant contract/permit objects

**Rule:** if it can cost a worker money, time, safety, or status — it gets a receipt.

### B2) Enforcement pipeline (inspection → citation → remedy → closure)
A minimal, audit-friendly loop:
1) **Intake / trigger** (`SRV-*`):
 - complaint, random audit, targeted sector campaign, procurement-triggered check, incident report
2) **Investigation / inspection** (`ENF-*`):
 - log that an action occurred, when, under what authority, and what was observed (redact sensitive witness details as required)
3) **Finding / determination** (`DRR-*`):
 - violation/no-violation, classification decision, unsafe condition order, pay determination
4) **Remedy and compliance** (`DRR-*` + `AL-*`):
 - backpay owed, abatement required, penalty assessed, settlement approved/denied
5) **Closure** (`REL-*` + `OFR-*` where needed):
 - closure reason, recovery amount, repeat-offender flag (where lawful), and publication as aggregate metrics

**Anti-retaliation is part of the pipeline:** retaliation allegations are not “separate HR issues”; they are enforcement events and MUST be receipted and routed to remedy.

### B3) Status / classification decisions (employee vs contractor)
Worker status is a common *arbitrage edge* (avoid benefits, taxes, and protections). Treat status decisions as first-class:
- publish the **status rubric** (factors, presumptions, burdens) as `RULE-*` (or PRR instrument)
- require `DRR-*` receipts for determinations with `RC-LAB-001`
- publish overturn rates and reclassification outcomes as `REL-*` (methods + revision logs)
- if algorithmic allocation or rating systems materially affect control/subordination, register the system (`ADS-*`) and require contestability (`IOP-5`; see `06-digital-and-algorithmic-governance.md`)

### B4) Procurement as leverage (labor clauses without “accountability laundering”)
Where government procures labor-intensive work (construction, cleaning, care, security, logistics), it can enforce decent work by contract — but only if the clauses are legible and auditable:
- require contract clauses that bind subcontractors and require wage/working-condition compliance (see [BIB-ILO-C94-1949])
- when a labor clause is invoked (noncompliance, withholding payment, termination), issue joinable `DRR-*` and log related `ENF-*`
- publish whether such clauses exist as part of the contracting register’s CLC discipline (`38-contracting-and-procurement-register.md`)

### B5) Publication discipline (REL releases that matter)
Publish **small, versioned** `REL-*` releases (monthly/quarterly) with method notes:
- complaint volumes, time-to-first-contact, time-to-closure
- inspection counts and coverage (by sector/region), violation rates
- wage recovery totals and distributional summaries (privacy-preserving)
- retaliation allegations and outcomes
- repeat-offender/recidivism indicators (where lawful and methodologically justified)

If publication is sensitive (e.g., small-n), publish coarser aggregates but keep **internal auditability** and external oversight access (`ACC-*`, `55-...`).

---

## C) Failure modes to design against (and the countermeasures)
- **Retaliation + chilling effects:** workers don’t complain. Counter: anonymous intake options (where lawful), rapid interim relief where possible, and explicit retaliation reason codes (`RC-LAB-005`) with tight response SLAs.
- **Under-enforcement via backlog:** “rights delayed = rights denied.” Counter: queue metrics published as `REL-*`, and backlog thresholds that automatically open `OFR-*` follow-through.
- **Misclassification arbitrage:** harms cascade into taxes, benefits, and education transitions. Counter: publish rubrics as `RULE-*`, treat determinations as receipted `DRR-*`, and follow causal chains into `64-social-protection-and-benefits-governance.md` and `68-education-and-skills-governance.md`.
- **Labor ↔ migration enforcement entanglement:** when workplace enforcement is tied to immigration control, complaints collapse. Counter: separate functions where possible; protect complainants; publish joint protocols and retaliation signals (`67-...`, `83-...`).
- **Fragmented jurisdiction:** city/state/national labor functions overlap or leave gaps. Counter: use compacts (`CMP-*`) and log scope assignments as `DRR-TYPE: SCOPE` (`19-compacts-and-cooperative-governance.md`, `70-...`).
- **Algorithmic management as invisible rulemaking:** ratings, deactivation, and allocation act as discipline without due process. Counter: register systems (`ADS-*`), require reason codes and human review for adverse actions where the state relies on platform outputs (`IOP-5`).
- **Corruption / selective enforcement:** Counter: publish inspection selection methods, use randomization where appropriate, and route anomalies into `OFR-*` with public closure proofs.

---

## D) Reason code starter set (`RC-LAB-*`)
Use these *in addition to* `RC-PROC-*`, `RC-ELIG-*` (when benefits/tax status hinges on labor status), and `RC-ENF-*` (for general enforcement posture).

See: `52-reason-codes-registry.md` (canonical table).

---

## E) Anchor set (high-trust references)
- Labour inspection and enforcement baseline: [BIB-ILO-C81-1947]
- Freedom of association / collective bargaining protections: [BIB-ILO-C87-1948], [BIB-ILO-C98-1949]
- Employment relationship classification guidance: [BIB-ILO-R198-2006]
- Procurement labor clauses anchor: [BIB-ILO-C94-1949]
- Platform/new forms of work policy framing: [BIB-OECD-PLATFORMWORK-2020], [BIB-OECD-NEWFORMS-2019]

---

## F) Where this plugs in
- **Triad note (benefits ↔ education ↔ labor):** failures in one domain often show up as denials/exclusions in the others (benefits eligibility gates school supports; employment-status misclassification gates benefits; migration/labor enforcement can chill complaints). When auditing harms, follow causal chains across `64`, `68`, `69`, and (often) `67`. (See `101-claude-rev142-normative-requirements.md` (NR-04).)
- Remedies and appeal lanes: `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`
- Benefits and eligibility joins (classification and work status): `64-social-protection-and-benefits-governance.md`
- Migration/work authorization joins: `67-migration-and-mobility-governance.md`
- Procurement and contracting legibility: `22-public-integrity-and-procurement.md`, `38-contracting-and-procurement-register.md`
- Oversight follow-through: `55-oversight-findings-and-response-register.md`
- Automated decision systems register: `42-automated-decision-systems-and-model-registry.md`
