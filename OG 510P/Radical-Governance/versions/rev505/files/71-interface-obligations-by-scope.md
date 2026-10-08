# Interface Obligations by Scope (MVGS in Practice)

**Cross-stack note:** use `306-scope-design-ideal-government-and-reference-bundles-guide.md` for the canonical route across the scope-design family. This memo is the interface-obligation substrate: it answers what any scope must publish once it exercises authority, not the broader question of which scope should own what or what the government at that scope should be made of.


**Purpose:** set the minimum interface obligations each scope owes (receipts, reasons, routing, records) so boundaries don’t break rights.

**Person served:** A governed person whose rights/resources are affected and who needs every scope to emit the minimum artifacts (receipts, rules, lanes) that make power contestable.

**From-below:** This tells you what each level must publish and how to reach a human, so you can’t be stranded in an agency maze.
**EXP pointer:** counters `EXP-02` (Waiting) and `EXP-06` (Complexity) by requiring degraded-mode variants for every interface obligation (`98-persons-path-and-accessibility-invariants.md`).

This memo prevents “scope drift” by making **interface obligations** explicit: if a unit exercises authority, it MUST emit the minimal public artifacts that make power **legible + contestable** (authority, rules, reasons, money, remedy).

See `70-interoperability.md` for the join-key map and canonical memo homes.

**Material floor (one sentence):** interface obligations MUST be satisfiable under severe capacity/low infrastructure; disclose the staffing/budget assumptions and the lowest‑infrastructure variant (paper receipts, low‑bandwidth publishing), or route explicitly to Phase −1 / degraded‑mode planning. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-17).)

## Kernel anchors (do not repeat)
- **Join-key map + memo homes:** `70-interoperability.md` (avoid duplicate schemas).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (interfaces can harm).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (access, safety, no wrong door).
- **Records + receipts:** `31-records-foi-and-government-memory.md` (DRR; as-of).
- **Remedy lanes:** `08-remedy-and-grievance.md`, ALR `36-...` (effective relief, time bounds).

## Named tensions (design must surface these)
- **Minimum floors vs autonomy:** scope-appropriate obligations without flattening local forms.
- **Comprehensiveness vs cognitive budget:** publish the spine; resist scope creep (`96-...`).
- **Enforcement vs capacity:** obligations must have degraded-mode implementations, not only ideal-state.
- **Standardization vs pluralism:** shared keys without forcing identical institutions.

## A. Universal obligations (any unit with *public* authority)

A unit is “in scope” if it has a competence-ledger entry (Unit ID) and can affect rights/resources.

**MUST publish**
- **Competence / mandate record:** Unit ID entry with scope, powers, funding linkages, and effective dates (`34-...`).
- **Rules-in-force inventory:** decisions cite `RULE-*` (as-of) and any controlling `STD-*` (`39-...`, `27-...`).
- **Decision receipts:** rights- or resource-affecting acts emit `DRR-*` with reason codes (`RC-*`) and remedy lanes (`AL-*`) (`31-...`, `52-...`, `36-...`).
- **Time bounds + no‑response rule:** publish ack/decision deadlines and what happens if the unit misses them (safe filing + auto‑escalation / interim protection / deemed outcome), and publish tail waits for high‑harm classes (`82-...`; receipt semantics: `31-...`).
- **Residual / no-category-fit path:** publish how a person who does not fit predefined categories is handled (authorized human adjudication + reasoned receipt + measurable “edge review”), so “no category” cannot function as denial. (`47-...`, `82-...`, `12-...`; see `101-claude-rev142-normative-requirements.md` (NR-10).)
- **Person-facing usability (non-optional):** any required `DRR`/`AL` interface MUST satisfy the **receipt comprehension test** and **navigation duty** (“no wrong door”), and MUST name how people who cannot effectively contest are represented (children/custody/incapacity). Treat fear/retaliation and delay as defects, not user errors. See `98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`, `83-...`. **No AI-only or digital-only front door:** if a unit requires a `DRR`/`AL` interaction, it MUST provide at least one staffed, non-digital path (in-person/phone/paper) and must not deny service or remedy solely due to lack of digital access. Do not make the person the integrator across units: routing and handoffs are an institutional duty; receipts are for verification/contestation, not document‑shuttling.
- **Money traces:** budgets/spend/transfer hooks are joinable via `REL-*` releases; contracts via `CON-*`/OCDS where applicable (`51-...`, `38-...`, `07-...`).
- **Records + access:** retention + FOI/disclosure logs (`31-...`).

## B. Conditional obligations (only where the power exists)

**Coercive powers (policing, custody, sanctions, forced removal)**
- MUST: `ENF-*` event register joined to authorizing `DRR-*` + `RULE-*` as-of + `AL-*` lanes (`43-...`, `05-...`).
- MUST: independent oversight case/finding tracking (`OFR-*`) with closure evidence (`55-...`, `32-...`).

**Secrecy / sensitive information constraints (classification, redaction, operational security)**
- MUST: withholding/classification decisions emit `DRR-*` receipts with `RC-*` reason category, legal basis, and **review/declassification date**.
- MUST: publish a withholding log (existence metadata) and provide an independent review lane with protective access to unredacted records.
- See: `77-sensitive-information-and-secrecy-governance.md`, `31-...`, `53-...`.

**Internal control / assurance (money, coercion, high-stakes automation)**
- SHOULD: publish a `REL-*` **control map** (material risks → controls → basis) and a periodic control **test plan + results** (methods noted; diffable; no silent edits).
- MUST: material exceptions open an `OFR-*` case with deadlines + closure evidence; missed publication cadence is itself an auditable incident.
- See: `84-internal-controls-and-continuous-assurance.md`, `55-...`, `07-...`, `81-...`.

**Verification / inspection authority (auditing compliance across parties)**
- MUST: publish a verification schedule (cadence + coverage + sampling logic) as a `REL-*` release and make inspector/auditor authority explicit in the competence ledger (and by delegation receipts where applicable).
- MUST: material findings emit typed `DRR-*` receipts that cite controlling `RULE-*`/`STD-*`/`CMP-*` (as‑of), the supporting `REL-*`, and the contestation lane(s) (`AL-*`).
- MUST: systemic or high-severity findings open an `OFR-*` case with timeline + closure evidence; secrecy constraints follow `77-...` (publish receipts even when payload is withheld).
- See: `81-verification-inspection-and-compliance-ladders.md`, `55-...`, `36-...`, `78-...`, `79-...`.

**Emergency powers (EMR) (exception logging across scopes)**
- MUST: every exceptional measure logged as `EMR-*` with legal basis, scope, sunset, review trigger, and after-action evaluation plan (`45-...`, `23-...`).

**Waivers / variances / exemptions (non-emergency rule departures)**
- MUST: departures from `RULE-*`/`STD-*`/`SRV-*`/control baselines emit `DRR-*` tagged `DRR-TYPE: EXCEPTION` with legal basis, bounds, expiry, and contestation lane(s) (`AL-*`).
- SHOULD: publish an exception log as a `REL-*` release at a stated cadence (existence metadata + review dates even when details are withheld).
- MUST: renewals/revocations emit new receipts; variance creep beyond a published threshold triggers a scoped `OFR-*` corrective case.
- See: `85-waivers-variances-and-exceptions-discipline.md`, `77-...`, `76-...`, `84-...`.

**Delegation / acting authority (who is allowed to sign)**
- MUST: publish a role-level authority schedule pointer (per Unit ID) and include `SIGNATORY-ROLE` on consequential `DRR-*` receipts.
- MUST: delegations/acting appointments/revocations emit `DRR-*` tagged `DRR-TYPE: DELEGATION` with time bounds, limits, legal basis, and a dispute/appeal lane.
- See: `78-delegation-and-acting-authority-discipline.md`.

**Integrity / influence transparency (capture risk)**
- MUST: maintain `INF-*` and `INT-*` coverage for Tier-1 roles and above-threshold decisions; publish `INT` status (filed/overdue/verified) and `INF` interaction disclosures with no silent edits.
- MUST: for covered decision classes, the `DRR-*` receipt cites `INF-*` IDs or `INF: NONE DECLARED`; recusals/management actions that affect authority emit `DRR-TYPE: INTEGRITY` and link to `INT-*`.
- SHOULD: publish [IPM-20] at a stated cadence and treat chronic low disclosure/overdue status as a trigger for a scoped `OFR-*` audit case.
- MUST: maintain protected disclosure lane(s) (`AL-*`) with at least one independent channel; retaliation determinations emit `DRR-TYPE: INTEGRITY-RETALIATION`; publish disclosure/retaliation stats as `REL-*`; systemic patterns open `OFR-*` follow‑through.
- See: `46-influence-and-interests-register.md`, `79-conflict-of-interest-and-revolving-door-discipline.md`, `22-public-integrity-and-procurement.md`.

**High-volume decision systems / grievance risk**
- MUST: publish appeal-lane coverage (ALR) and contestation health metrics (appeal volume/outcomes and `AO-NORESP` share by lane) at a stated cadence.
- MUST: define and publish systemic-trigger thresholds; when triggered, open a scoped systemic `OFR-*` case with deadlines and corrective action tracking (see `76-systemic-redress-and-pattern-remediation.md`, `08-...`, `36-...`, `55-...`).

**Service delivery / access journeys (where people experience authority as services)**
- MUST: maintain `SRV-*` coverage for material services (service catalog + access journey), including decision points where `DRR-*` receipts MUST be issued and the controlling `RULE-*` as-of.
- MUST: publish a service standard pointer and performance cadence for material services; performance snapshots publish as `REL-*` (method-noted) keyed by `SRV-*`.
- MUST: chronic underperformance triggers a scoped `OFR-*` corrective case; patterned harms use systemic redress triggers.
- See: `47-service-catalog-and-access-journeys-register.md`, `82-service-standards-and-minimum-service-guarantees.md`, `76-...`, `08-...`.

**High-discretion programs / systems (safety-case discipline)**
- MUST: publish an `AC-*` assurance case summary (claim–argument–evidence + monitoring + stop-conditions) for any coercive/emergency/high-stakes automated/critical-infrastructure regime.
- MUST: tag material incidents and oversight findings to the relevant `AC-ID` so postmortems cannot ignore the governing argument.
- See: `73-assurance-case-and-governance-safety-case.md`.

**Lifecycle / sunset discipline (keep authority reversible)**
- MUST: publish review/sunset dates and current status for major `RULE-*` (PRR), `PROG-*`, `EMR-*`, and any high-discretion `AC-*` regimes.
- MUST: renewals/terminations are joinable `DRR-*` receipts citing the governed object IDs and evidence docket pointers (`REL/EVAL/OFR`).
- SHOULD: treat missed review dates as a governance incident (open `OFR-*` `LEGIBILITY-GAP` case).
- See: `74-sunsetting-and-deprecation-discipline.md`.
**Personal data processing / automation in consequential decisions**
- MUST: Data Processing Register entries (`DPR-*`) and (where used) ADS / model registry links; human review + appealability (`33-...`, `42-...`, `06-...`).

**Intergovernmental compacts / cross-unit delegation**
- MUST: compact record `CMP-*` (parties, scope, metrics, enforcement ladder, dispute path, exit/upgrade rules) and any enforcement action emits `DRR-*` that cites the compact (`19-...`).

**Transfers / conditionality**
- MUST: Transfer Register entries `TRF-*` for material transfers/conditions and a joinable compliance story (reason codes + remedy) (`35-...`, `18-...`).

## C. Scope readiness scorecard (one-screen)

Use this to audit whether a scope is *governable* (legible, contestable, and capable) without adding a new “tier.”

- **Legibility spine present?** Unit ID + `RULE` + `DRR` + `AL` + `REL`
- **Authority chain present?** `SIGNATORY-ROLE` on `DRR` + `DRR-TYPE: DELEGATION` when acting/delegated authority applies
- **No dark coercion?** `ENF` + `OFR` (if coercive power exists)
- **No dark exceptions?** `EMR` (if emergency power exists)
- **No dark data?** `DPR` (+ ADS registry links) (if personal data / automation exists)
- **Boundary discipline?** `CMP` + `TRF` (if delegation / transfers exist)

If any required artifact is missing, treat it as an **auditable governance incident** (see `04-threat-models.md` and `53-publication-integrity-and-tamper-evident-logs.md`).
