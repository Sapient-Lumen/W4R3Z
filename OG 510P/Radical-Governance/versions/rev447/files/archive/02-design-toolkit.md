# Design Toolkit (Reusable Primitives)

**Purpose:** provide reusable governance *primitives* (receipts, joins, safeguards) so power stays visible, contestable, and safe across domains.

**Person served:** the governed person whose outcome depends on how designers choose scopes, interfaces, and oversight hooks—and who must be able to understand and challenge decisions without insider access.

**From-below:** These building blocks make it harder for agencies to disappear you into process: they force receipts, reasons, safe contestation, and follow‑through across every domain.

**EXP pointer:** EXP-01–EXP-08 (primitives that counter all eight governed experiences; see `98-persons-path-and-accessibility-invariants.md`).
**Material floor (one sentence):** every primitive MUST specify its lowest‑infrastructure implementation (paper/phone/in‑person) and MUST NOT require apps, accounts, or AI-only front doors to be usable. (See `101-claude-rev142-normative-requirements.md` (NR-13).)

Use these as “lego bricks” across scopes. Each module is a *minimal spec* with common failure modes.

**Module keys:** `DEC` (decision & legitimacy), `ACC` (accountability & integrity), `LAW` (rule of law & remedy),  
`OPEN` (transparency & participation), `SAFE` (coercion controls), `CAP` (capacity & finance), `IOP` (interfaces & infrastructure).



**New interface primitive:** **Service Promise + Time Budget** (make delay enforceable) — see `108-service-standards-and-time-budgets.md`.
---

## Normative language (spec semantics)

This archive uses **MUST / SHOULD / MAY** in the sense of RFC‑style design specifications: obligations are testable, exceptions are explicit, and interfaces can interoperate without trust. Implementers SHOULD treat deviations from a MUST as a governance defect unless an explicit exception path is published and appealable. (See `96-archive-governance.md` “Language note”; and for LLM editing discipline see `126-llm-archive-operator-protocol.md` and `101-claude-rev142-normative-requirements.md` (NR-18, NR-01).)

**Dual-audience authoring:** when adding a primitive/module here, include one plain‑language line (≤40 words) stating what it protects or enables for the governed person, placed adjacent to the spec obligations. Keep it tight; no long vignettes.
(See `96-archive-governance.md` (Dual-audience rule) and `101-claude-rev142-normative-requirements.md` (NR-01, NR-04).)

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Scope + interface obligations:** `14-scope-ladder.md`, `71-interface-obligations-by-scope.md`.
- **Closed loops + brakes:** `104-governance-control-loops.md`, `105-institutional-circuit-breakers.md`.
- **Legitimacy protocol + tests:** `106-legitimacy-protocols.md`, `107-governance-test-suite.md`.

- **Interjurisdictional dispute lane (no ping‑pong):** `114-interjurisdictional-dispute-and-coordination.md`.

## Named tensions (design must surface these)
- **Reuse vs context:** reusable primitives vs locally legitimate functional equivalents (`01-principles.md`).
- **Legibility vs safety:** publishing for accountability vs creating targets (`99-protective-legibility-and-adoption-dynamics.md`, `77-sensitive-information-and-secrecy-governance.md`).
- **Precision vs adaptability:** tight interface contracts vs brittle bureaucracy.
- **Measurement vs gaming:** metrics as learning vs incentives to lie (`03-metrics-and-evidence.md`).

### Using functional equivalents (cultural pluralism)
These primitives describe **interface obligations**, not a single bureaucratic form. In relational, consensus, restorative, or oral governance settings, implementers SHOULD map each required artifact to a locally legitimate **functional equivalent** while preserving the minimum properties that keep power contestable:
- **Receipt + reasons:** a witnessed decision + an audio note + a minimal ledger entry can satisfy `DRR-*` if it is referencable, comprehensible, and durable.
- **Contest path:** the community’s review forum (council meeting, elders’ circle, restorative conference) can satisfy `AL-*` if it is time‑bounded, safe, and produces an outcome receipt.
- **Durable memory:** where writing undermines legitimacy or safety, keep a *minimal archival record* with an explicit custodian and retrieval path (`31-records-foi-and-government-memory.md`), plus a non‑reading front door (`98-persons-path-and-accessibility-invariants.md`).
Design memos MUST include a one‑screen mapping when functional equivalents are used (what counts as the receipt, the join keys, the contest lane, and the durable record), and MUST treat missing properties as defects—not “local flavor.”
(See `101-claude-rev142-normative-requirements.md` (NR-17, NR-13).)

## DEC — Decision & deliberation (legitimacy generators)

- **DEC-0 Binding:** Any deliberation/participation that claims influence MUST include a duty-to-respond + Decision Receipt binding (see `111-deliberation-to-decision-binding.md`).

For how to **compose** these modules into a small “legitimacy pipeline” (by decision type and by scope), see `21-legitimacy-architecture.md`.

**DEC-1 Elected body (representation)**
- MUST: competitive elections; fair districts; transparent party finance; accessible voting.
- Best at: scalable allocation and trade-offs.
- Fails via: gerrymander, money/capture, polarization.

**DEC-2 Sortition / citizens’ assembly (deliberation)**
- SHOULD: stratified random selection; compensation; expert testimony rules; public evidence pack; duty-to-respond.
- Best at: agenda-setting, constitutional review, high-salience long-horizon issues.
- Design evidence base: see [BIB-OECD-DEL] (principles) and OECD comparative cases (use bibliography anchors).

**DEC-3 Participatory budgeting (bounded allocation)**
- MUST: fixed % or per-capita envelope; clear eligibility; public results; audit trail.
- Best at: local capital + services where preferences differ by neighborhood.

**DEC-4 Direct democracy (guard-railed)**
- MAY: initiative/referendum with (a) constitutional review, (b) fiscal note, (c) deliberative phase, (d) signature integrity.
- Fails via: manipulation, minority rights erosion, fiscal sabotage.

**DEC-5 Electoral system as a design variable**
- MUST: choose representation incentives intentionally (fragmentation vs. inclusion, localism vs. proportionality).
- Anchor: see [BIB-IDEA-ESD].

**DEC-6 Future generations review (long-horizon constraint)**
- SHOULD: require “future impact statements” for major laws/plans; publish assumptions; mandate to trigger review or deliberation when long-term risks are ignored.
- MAY: create a Future Council/Commission with independence protections and a duty-to-respond from elected bodies.
- Anchor: see [BIB-UN-DFG].

**DEC-7 Independent election administration + verifiable tabulation**
- MUST: election management insulated from partisan control; transparent procedures; publish results/corrections as `REL-*` releases with methods + revision logs.
- MUST: outcomes independently checkable via an auditable trail and post‑election verification (prefer risk‑limiting audits where feasible).
- MUST: election disputes are time-bounded and discoverable (`AL-*` lanes) and operational decisions emit `DRR-*` receipts.
- Anchors: [BIB-VENICE-ELECT], [BIB-IDEA-EMD], and verification guidance ([BIB-NASEM-SECURINGTHEVOTE-2018], [BIB-NIST-RLA-GENTLE]).
- See: `56-elections-and-electoral-administration.md`.

**DEC-8 Public health governance as an auditable pipeline**
- MUST: publish surveillance/capacity signals as `REL-*` releases with methods + revision logs; no silent overwrites.
- MUST: response triggers and major measures are grounded in published `RULE-*` rubrics and emit `DRR-*` receipts (reasons + cited `REL-*` evidence + `AL-*` lanes).
- MUST: exceptional powers are logged as `EMR-*` episodes with sunsets, renewals, and after-action closure artifacts.
- Anchors: cross-border obligations and alert levels via IHR ([BIB-WHO-IHR-TEXT-2025]; [BIB-WHO-IHR-AMEND-EIF-2025]).
- See: `57-public-health-and-biosecurity-governance.md`.

**DEC-9 Constitutional / charter change with integrity-grade procedure**
- MUST: the top-tier instrument is inventoried in PRR (`39-...`) with as-of queries; proposals and ratification outcomes publish as `REL-*` with method notes + revision logs.
- MUST: eligibility/clarity gates emit `DRR-TYPE: INTEGRITY` dockets (single-subject, clarity/neutrality, rights-floor, emergency-window).
- MUST: disputes are time-bounded and discoverable (`AL-*`); influence/finance joins via `INF/INT` where relevant.
- Anchors: referendum good practice ([BIB-VENICE-REFERENDUMS-2007], [BIB-VENICE-REFERENDUMS-2022]), direct democracy design ([BIB-IDEA-DIRECTDEMO]), and amendment discipline ([BIB-ALBERT-CONSTAMEND]).
- See: `58-constitutional-change-and-amendment-discipline.md`.

**DEC-10 Public communication as auditable infrastructure**
- MUST: publish authoritative guidance as versioned `REL-*` releases (methods + change logs) with “as-of” access; never silently edit public advisories.
- MUST: if a communication has coercive effects (restrictions, eligibility, enforcement posture), it MUST be grounded in `RULE-*` and emit `DRR-*` (reasons + cited `REL-*` evidence + `AL-*` lanes).
- SHOULD: maintain a two-way intake + rumor response workflow; major harms/noncompliance SHOULD trigger independent follow‑through (`OFR-*`).
- Anchors: emergency risk communication guidance ([BIB-WHO-RCCE], [BIB-CDC-CERC-2024]) and human-rights compatible platform/media governance ([BIB-UNESCO-PLATFORM-GUIDELINES], [BIB-UN-SG-INFOINTEGRITY-2023], [BIB-COE-PSM-GOV-2012]).
- See: `61-public-communication-and-information-integrity.md`.

**DEC-11 Land-use & housing governance as an auditable pipeline**
- MUST: inventory binding plans/zoning instruments in PRR; zoning/plan maps publish as versioned `REL-*` releases with diffs + changelogs (no silent edits).
- MUST: variances/rezones/high-impact permits emit `DRR-*` (reasons + cited `RULE-*`/`REL-*` + `AL-*` lane) and are logged in `PAR`.
- MUST: join material decisions to influence/interest disclosures where relevant (`INT/INF`) and publish method notes for capacity/impact claims.
- Anchors: tenure governance norms ([BIB-FAO-VGGT-2012]) and comparative reform agenda ([BIB-OECD-HOUSING-REFORM-2024]).
- See: `62-land-and-housing-governance.md`.

**DEC-12 Climate adaptation & disaster risk governance as an auditable pipeline**
- MUST: publish hazard/vulnerability baselines as versioned `REL-*` releases (methods + revision logs); any posture-changing thresholds are explicit `RULE-*` trigger rubrics.
- MUST: alerts/closures/evacuations and other rights-affecting activations emit `DRR-*` (reasons + cited `REL-*` evidence + `AL-*` lanes); exceptional authority is logged as `EMR-*` episodes with sunsets + closure artifacts.
- MUST: discretionary risk-acceptance exceptions are time-bounded `DRR-*` (expiry/review date + compensating controls) using `RC-DRR-*` where applicable.
- SHOULD: join resilience investments to `AST-*`/`SRV-*` and `PROG-*`/`EVAL-*`; drills and after-action follow-through use `OFR-*`.
- Anchors: Sendai + adaptation baselines ([BIB-UNDRR-SENDAI-2015], [BIB-IPCC-AR6-WG2-2022]) and adaptation planning/risk assessment standards ([BIB-ISO-14090], [BIB-ISO-14091]).
- See: `63-climate-adaptation-and-disaster-risk-governance.md`.

**DEC-13 Social protection & benefits governance as an auditable pipeline**
- MUST: define benefits as `SRV-*` service journeys (intake + recertification) with accessible channels + queue metrics; treat administrative burden as a measurable failure mode.
- MUST: eligibility and benefit-calculation criteria are `RULE-*` and queryable “as-of”; determinations/suspensions/recoupments emit `DRR-*` with `RC-*` reasons and `AL-*` lanes.
- MUST: publish program-level payment and reconciliation releases as `REL-*` with privacy protections; join delivery systems and automation to `IDN-*`/`DPR-*`/`ADS-*`.
- Anchors: social protection floors ([BIB-ILO-SPF-R202-2024]) and social registry / digital delivery guidance ([BIB-WB-SOCIALREG-2017], [BIB-WB-DIGDELIVERY-2025]).
- See: `64-social-protection-and-benefits-governance.md`.

**DEC-14 Energy & decarbonization governance as an auditable mitigation pipeline**
- MUST: publish emissions/energy baselines and accounting methods as versioned `REL-*` releases; targets/budgets are `RULE-*` that cite the baseline “as‑of” and pinned measurement `STD-*`.
- MUST: long‑lived asset decisions (generation/transmission/fuel infrastructure) emit `DRR-*` receipts with lock‑in and affordability impacts; reliability risk acceptance is explicit and time‑bounded.
- MUST: instrument execution (auctions, pricing, subsidies, procurement) is joinable via `PROG-*`, `REL-*` MRV, and `OFR-*` follow‑through; affected parties have discoverable `AL-*` lanes.
- Anchors: [BIB-IPCC-AR6-WG3-2022], [BIB-IEA-NETZERO-2023], inventory standards ([BIB-GHGPROTOCOL-CORP], [BIB-ISO-14064-1-2018]).
- See: `65-energy-and-decarbonization-governance.md`.

**DEC-15 Migration & mobility governance as an auditable pipeline**
- MUST: admissibility/eligibility and evidence burdens are expressible as `RULE-*` and queryable “as-of”; status-affecting decisions emit `DRR-*` receipts with `RC-*` reasons and discoverable `AL-*` lanes.
- MUST: custody/detention and removal/return (where used) are logged as `ENF-*` joined to authorizing `DRR-*`; publish aggregate delay/error/overturn metrics as versioned `REL-*` releases (methods + revision logs).
- MUST: outsourcing/offshoring cannot break accountability: contracts/compacts must carry receipt + audit + remedy clauses and independent follow-through uses `OFR-*`.
- Anchors: refugee status determination guidance ([BIB-UNHCR-HANDBOOK-2019], [BIB-UNHCR-RSD-PS-2020]) and migration cooperation principles ([BIB-UN-GCM-2018]).
- See: `67-migration-and-mobility-governance.md`.

---

**DEC-16 Education & skills governance as an auditable pipeline**
- MUST: enrollment/placement/discipline/credential decisions are expressible as `RULE-*` and emit `DRR-*` receipts with `RC-EDU-*` reasons and discoverable `AL-*` lanes.
- MUST: curriculum/assessment/qualification requirements are published as pinned `STD-*` (or PRR instruments) with as-of access, change logs, and integrity controls via `REL-*`.
- MUST: publish minimal access/learning-condition indicators as versioned `REL-*` releases (methods + revision logs) and route recurring safeguarding/exclusion failures into `OFR-*` with verified closure.
- Anchors: [BIB-UNESCO-ED2030-2015], learning crisis framing ([BIB-WB-WDR2018]), assessment framework exemplars ([BIB-OECD-PISA-SCI-2025]), safeguarding standards ([BIB-UNICEF-SAFEGUARD-2025]).
- See: `68-education-and-skills-governance.md`.

**DEC-17 Labor & work governance as auditable infrastructure**
- MUST: publish wage/time/safety standards as queryable “as‑of” `RULE-*` and pinned `STD-*` (and inventory enforcement manuals/scripts/config tables in PRR with versioning).
- MUST: rights-affecting labor actions (status/classification, citations, backpay calculations, abatement orders, settlements, sanctions) emit `DRR-*` receipts with `RC-LAB-*` reasons and discoverable `AL-*` lanes; inspections/investigations are logged as joinable `ENF-*`.
- MUST: publish small, versioned enforcement and recovery releases as `REL-*` (queue times, inspection coverage, violation rates, recovery totals) with method notes + revision logs; recurring failures route into `OFR-*` follow-through.
- SHOULD: when government procures labor-intensive work, require auditable labor clauses and join any enforcement to the contract register (`CON-*` + CLC discipline).
- Anchors: labour inspection baseline ([BIB-ILO-C81-1947]); organizing/bargaining protections ([BIB-ILO-C87-1948], [BIB-ILO-C98-1949]); employment relationship guidance ([BIB-ILO-R198-2006]); procurement labor clauses ([BIB-ILO-C94-1949]); platform work policy framing ([BIB-OECD-PLATFORMWORK-2020]).
- See: `69-labor-and-work-governance.md`.

## ACC — Accountability & integrity (anti-capture core)

**ACC-1 Supreme audit / independent audit office**
- MUST: publish audits; protected budget formula; access to records; follow-up requirements.
- Anchors: see [BIB-INTOSAI-P10]; [BIB-INTOSAI-P1].
- Pairs with: OPEN (budget/procurement transparency).
- See: `32-oversight-institutions-and-follow-through.md` (independence + follow-through loop + OFRR).
- See also: `130-audit-and-inspection-integrity.md` (receipts + clocks + follow-through ledger).

**ACC-2 Inspector general / anti-corruption bureau**
- SHOULD: subpoena power; protected leadership removal rules; publish redacted findings.
- Norm anchor: see [BIB-UNCAC].

**ACC-3 Ombuds + low-cost remedy channel**
- MUST: rapid timelines; compel agency response; publish patterns; protect complainants.
- Anchor: see [BIB-VENICE-OMB-2019].
- See: `32-oversight-institutions-and-follow-through.md` (independence + pattern reporting + follow-through).

**ACC-4 Public integrity system (whole-of-government)**
- SHOULD: integrity strategy, risk assessments, conflict-of-interest rules, enforcement, culture, and open engagement.
- SHOULD: procurement integrity baseline + open contracting discipline (see `22-public-integrity-and-procurement.md`).
- Anchor: see [BIB-OECD-PI].

**ACC-5 Influence transparency (lobbying / revolving door)**
- SHOULD: disclosure of lobbying and political finance; cooling-off periods; foreign influence transparency.
- SHOULD: adopt **ICIP** primitives (registers + receipts) from `120-conflicts-of-interest-and-influence-integrity.md`.
- Anchors: see [BIB-OECD-LOB-2024]; [BIB-OECD-LOB-2010]; [BIB-UNCAC].

**ACC-6 Oversight stack + follow-through (OFRR)**
- MUST: treat oversight as a closed loop (publish findings → duty-to-respond → action plan → independent closure verification).
- MUST: maintain an Oversight Files & Responses Register (OFRR) conforming to `IOP-9` (stable IDs + change logs).
- See: `32-oversight-institutions-and-follow-through.md`.

**ACC-7 Audit lotteries + incentive-compatible compliance**
- SHOULD: mix **risk scoring** with **random selection** for audits/spot checks; publish the selection policy and keep an auditable trail.
- SHOULD: create **compliance dividends** where high artifact-conformance earns faster approvals/disbursement and lighter reporting, while persistent nonconformance escalates to typed sanctions.
- MAY: use bounded whistleblower rewards / integrity bounties with anti-retaliation and due process (avoid “bounty hunting” dynamics).
- Evidence: randomized audits/monitoring can reduce leakage; public audit disclosure can shift electoral accountability (see [BIB-OLKEN-2007]; [BIB-FERRAZFINAN-2008]).

**ACC-8 Safe harbor + self-correction (reduce concealment incentives)**
- SHOULD: provide a typed **self-report** path for agencies and contractors to disclose artifact failures (missing receipts/logs, wrong `RULE-*` basis, data-release errors) using a correction `DRR` (often `DRR-TYPE: INTEGRITY`) that links the affected artifacts.
- SHOULD: calibrate incentives—**timely self-report + correction** (and restitution where relevant) earns reduced sanctions and faster normalization; *no immunity* for intentional rights violations or serious harm.
- MUST: log self-reports and their disposition in the OFRR so repeat patterns trigger deeper audit (see `32-oversight-institutions-and-follow-through.md`).
- ASSUMPTION: safe-harbor design can shift behavior from concealment to correction when paired with credible audits (see `ACC-7`).

**ACC-9 Compliance & sanctions integrity (CSIP)**
- SHOULD: treat enforcement as a **versioned, receipt-bound interface**: every sanction produces a `CFR-*` (case file receipt) with rule-version linkage (`118`), contest window (`08/106`), and an auto-review date.
- SHOULD: prefer **assistance → correction → compliance agreements** before punitive steps; escalation requires a proportionality/reversibility check (`PRC-*`). (See `131-compliance-and-sanctions-integrity.md`; [BIB-OECD-REI-2014]; [BIB-OECD-REI-TOOLKIT-2018].)

---



**ACC-7 Protected disclosure / whistleblowing interface (WRR/WTR/WCR)**
- MUST: provide safe internal/external reporting lanes with **receipts + clocks + anti-retaliation**; publish aggregate outcomes.
- SHOULD: follow ISO whistleblowing management systems guidance; multi-channel reporting + protection principles.
- See: `121-whistleblowing-and-protected-disclosure.md`.
- Anchors: see [BIB-ISO-37002]; [BIB-OECD-WB-2016]; [BIB-COE-WB-2014]; [BIB-UNCAC-ART33].

## LAW — Rule of law & dispute resolution (constraints + remedy)

**LAW-1 Rights charter / constitution with justiciable rights**
- MUST: participation rights, due process, equality, remedies; supremacy over ordinary law.

**LAW-2 Independent courts + constitutional review**
- SHOULD: appointments insulated from partisan capture; transparent decisions; enforceable remedies.

**LAW-3 Administrative tribunals (fast specialized review)**
- SHOULD: appealable; published decisions; accessible to non-lawyers.

**LAW-4 Rule-of-law checklist method**
- SHOULD: periodic “rule-of-law health check” using a stable rubric (legality, oversight, equality, access to justice, checks & balances).
- Anchor: Venice Commission Updated Rule of Law Checklist (2025) ([BIB-VENICE-ROL-2025]).

**LAW-5 Effective remedy (grievance + enforceable fixes)**
- MUST: accessible complaint intake; time-bound escalation; independent review for high-risk harms.
- MUST: for rights-/resource-affecting actions, issue a Decision Record/Receipt (`DRR`) with reasons + cited Rule IDs, portable reason code(s) (`RC-*`), and appeal lane(s) (`AL-*`).
- MUST: when a challenge/review is decided, issue a review-result `DRR` that includes `AO-*` outcome code(s) + the challenged `DRR` (so contestation is measurable).
- SHOULD: ombuds + tribunals to absorb volume; courts set rights standards.
- SHOULD: for listings/watchlists/sanctions, publish a delisting path with independent review and time bounds (anchors: [BIB-UNSC-OMB]; [BIB-UNSC-OMB-PROC]).
- Anchors (effective remedy): [BIB-UN-REMEDY-60147], [BIB-ICCPR], and [BIB-EU-CHARTER-A47].
- See: `08-remedy-and-grievance.md`.

**LAW-6 Emergency powers & derogations discipline**
- MUST: formal declaration; typed and time-bounded powers; renewal votes; independent review remains on; publish an Emergency Measures Register.
- SHOULD: heightened constraints on election changes; ex-post audits for emergency procurement and fiscal actions.
- See: `23-emergency-governance-and-exceptions.md`.

**LAW-7 Permissioning & approvals discipline**
- MUST: publish criteria + legal basis (Rule IDs) and (where relevant) referenced `STD-*` IDs.
- MUST: time bounds and queue discipline by permit type; define deadline-miss behavior (deemed approval only when safe; otherwise escalation or deemed denial with reasons).
- MUST: maintain a Public Permit/Approval Register (PAR) conforming to `IOP-9` (stable IDs + change logs); publish aggregate queue stats.
- SHOULD: risk-tier permits; fast paths for low-risk; randomized assignment/rotation for high-risk classes; separation-of-duties for review vs inspection.
- See: `29-permissioning-and-approvals.md`.

**LAW-8 Personal data governance (privacy baseline)**
- MUST: lawful basis + purpose limitation for major processing; prohibit function creep without a new legal basis.
- MUST: minimization + retention discipline linked to the records/retention system (`OPEN-9`).
- MUST: enforceable rights channel for access/correction/objection with time bounds + appeal path (`LAW-5`).
- MUST: maintain a Public Data Processing Register (DPR) conforming to `IOP-9` (stable IDs + change logs); link `DPR-*` IDs to `ADS-*` registers and `PROG-*` IDs where relevant.
- SHOULD: high-risk processing gate for sensitive/coercion-adjacent or rights-affecting use cases.
- Anchors: see [BIB-EU-GDPR]; [BIB-OECD-PRIV-2013]; [BIB-COE-C108].
- See: `33-data-protection-and-personal-data-governance.md`.

---

**LAW-9 Courts & administrative justice spine (publishable decisions + enforceable remedy)**
- MUST: court/tribunal forums are discoverable as `AL-*` lanes (jurisdiction, deadlines, remedies, accessibility).
- MUST: binding decisions emit `DRR-TYPE: JUDGMENT` with cited `RULE-*` (as‑of), reasons (plain language + `RC-*`), and next `AL-*`.
- SHOULD: publish decisions as integrity‑grade releases (`REL-*` decision feed with “as-of” access + change logs); follow `53-...`.
- See: `66-justice-and-administrative-justice-governance.md`, `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md`.
**DEC-18 Exit / Fork / Federation (anti‑monopoly legitimacy)**
- MUST: define **exit lanes** with portability + continuity receipts (`EXIT-*`) and non‑retaliation (see `117-exit-voice-fork-federation.md`, `109-portability-and-cross-jurisdiction-continuity.md`).
- MUST: define **fork protocol** for bounded splits (`FORK-*`) including asset/liability inventory, fiscal settlement, rights-floor preservation, and a dispute lane (`114-interjurisdictional-dispute-and-coordination.md`).
- MUST: publish **federation compacts** as `COMP-*` with delegated powers, funding flows, audit hooks, amendment/exit clauses, and conflict resolution.


**LAW-7 Rulemaking & change control (rules as versioned power)**
- MUST: maintain a Rule Registry (`RID-*`) and issue Rule Change Receipts (`RCR-*`) with diffs, effective times, transition policy, impact statement, contest window, and rollback plan.
- MUST: decisions reference the exact rule version used (past-rule replay).
- Anchor: `118-rulemaking-and-change-control.md`.

**LAW-8 Constitutional amendment & entrenchment discipline**
- MUST: treat foundational change as gated, receipt-driven change control: Foundational Rule Registry (`FID-*`/`FVER-*`), Amendment Proposal Packets (`APP-*`), and Constitutional Change Receipts (`CCR-*`).
- MUST: anti-bundle rule, tiered notice periods, contestable deliberation, independent review window, and past-rule replay.
- Anchor: `124-constitutional-amendment-and-entrenchment.md` (see [BIB-VENICE-CONST-AMEND-2010], [BIB-VENICE-REFERENDUM-2022], [BIB-IDEA-CONST-AMEND-PRIMER]).



**DEC-19 Selection integrity (sortition & lotteries)**
- MUST: publish a **Selection Definition** (eligibility frame, stratification targets, disqualification rules, privacy plan) *before* any draw (see `119-selection-and-sortition-integrity.md`).
- MUST: use an independently **verifiable randomness source** (public beacon or equivalent) and emit a reproducible **Draw Receipt (`DR-*`)** with seed derivation + algorithm version.
- SHOULD: treat the eligibility frame as a capture surface: periodic frame audits + contestability (“I should be eligible / I should not be listed”).

**DEC-20 Intergenerational & future protection (make long-term harms contestable)**
- MUST: major changes include a **Future Impact Statement (`FIS-*`)** with irreversibility score, horizon, and monitoring plan.
- MUST: high‑irreversibility changes carry an automatic **Sunset & Review Receipt (`SRR-*`)** with rollback triggers.
- SHOULD: provide intergenerational standing via an advocate/ombud lane (contest + investigate + publish), without blank‑check veto.
- Anchor: `122-intergenerational-and-future-protection.md`.


**DEC-21 Association & collective power (make voice workable)**
- MUST: provide a protected **association lane** (staffed + non‑digital) that yields an Association Access Receipt (`AAL-*`) and anti‑retaliation triggers.
- MUST: provide a **collective filing lane** with a Collective Filing Receipt (`CFL-*`) for systemic harms (pattern claims + bundled cases).
- SHOULD: where bargaining applies, enforce a **duty‑to‑respond** with clocked Negotiation Response Receipts (`NTR-*`) and a bounded impasse pathway.
- Anchor: `123-association-and-collective-power.md`.
**DEC-22 Identity, membership & civil status (treat status as power)**
- MUST: every status grant/denial/change yields a **Civil Status Receipt** (`CSR-*`) with effective dates, evidence pointers, and a contest lane.
- MUST: publish an **Evidence Ladder** per status (at least two fallback routes; no impossible-proof).
- MUST: apply a **non-reset transfer rule** and provisional continuity for essentials during verification (see `109`, `114`, `108`).
- Anchor: `125-identity-membership-and-civil-status.md`.


## OPEN — Transparency & participation (public learning)

**Constraint:** transparency must attach to enforceable contestation and safety (anti‑retaliation / non‑targeting); otherwise it becomes theater or a weapon. (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-08).)

**OPEN-1 FOI + proactive disclosure**
- MUST: budgets, contracts, outcomes, audits; clear exemptions; appeal channel.
- Rights anchor: see [BIB-COE-TROMSO].
- Precondition: FOI works only if records are captured and retained (see `31-records-foi-and-government-memory.md`). For a portable interface spec (stable record pointers, disclosure clocks, FOI receipts), see `115-information-integrity-and-record-interfaces.md`.
- Norm anchor: see [BIB-OECD-OG].
- Note: for governing public evidence-building, statistics, and public-interest R&D as infrastructure, see `149-public-science-and-r-and-d-governance.md`.


**OPEN-2 Open contracting**
- SHOULD: publish all contracting stages with stable IDs; enable monitoring, competition, and anti-capture auditing.
- See: `22-public-integrity-and-procurement.md` for Minimum Viable Procurement Integrity (MVPI).
- Anchor: see [BIB-OCDS].



**OPEN-4 Algorithmic Decision Register (ADR)**
- MUST: register any automated/assisted system that influences eligibility, triage, enforcement, or risk scoring; publish a public card (purpose, data categories, evaluation summary, recourse); log material changes.
- See: `115-information-integrity-and-record-interfaces.md` (ADR + disclosure/record interfaces).


**OPEN-11 Data governance & privacy interfaces**
- MUST: publish Data Asset Cards for personal-data systems; log access and sharing with retrievable receipts; bind purposes to decisions and provide correction/contest lanes.
- See: `127-data-governance-and-privacy-interfaces.md` (DATA/PDR/ALR/SHR/COR).

**OPEN-12 Interoperability & interface standards**
- MUST: maintain an Interface Registry with Interface Cards, Change Receipts, and a conformance policy; treat interoperability as a rights-preserving seam-control problem.
- See: `128-interoperability-interfaces-and-standards.md`.


**OPEN-13 Public sphere & epistemic infrastructure**
- MUST: treat shared attention/knowledge as critical infrastructure; require amplification transparency, correction propagation, and safety-to-speak floors.
- See: `129-public-sphere-and-epistemic-infrastructure.md`.

**OPEN-14 Legibility & complexity budgets**
- MUST: publish complexity budgets (steps/time/cost/docs/language) for person-facing lanes; trigger circuit breakers when budgets are exceeded; maintain a Complexity Incident Ledger.
- See: `134-legibility-and-complexity-budgets.md`.

**OPEN-15 Taxation & revenue integrity**
- MUST: publish versioned revenue rules (TRR-*); issue replayable assessment/payment/refund receipts (TAR/TPR/TRF); enforce clocks with breach triggers; treat complexity as auditable policy (joins OPEN-14).
- See: `135-taxation-and-revenue-integrity.md`.
**OPEN-16 Land, housing, and commons integrity**
- MUST: publish parcel/commons cards (PCR/CCR); issue land-use decision receipts (LDR) and housing allocation receipts (HAR); enforce displacement/relocation continuity (DRP) with non-reset clocks; keep land-use complexity within budgets (joins OPEN-14).
- See: `136-land-housing-and-commons-integrity.md`.
**OPEN-17 Critical infrastructure & utilities integrity**
- MUST: publish service cards (USC-*), outage/degradation receipts (OER-*), and scarcity prioritization receipts (PRR-*); maintain a maintenance/asset integrity register (MAIR-*); enforce restoration clocks with circuit breakers.
- See: `137-critical-infrastructure-and-utilities-integrity.md`.

**OPEN-18 Public investment & capital projects integrity**
- MUST: publish a versioned Project Card (PC-*), issue Stage-Gate Receipts (SGR-*) for spend authorization, enforce Change Control Receipts (CCR-PI-*) for scope/budget/schedule deltas, and require Benefits Realization Receipts (BRR-*) that gate future tranches.
- See: `138-public-investment-and-capital-projects-integrity.md`.





**OPEN-19 Risk & safety assurance governance**
- MUST: publish Safety Case Cards (`SCC-*`) for high‑hazard systems; issue time‑bounded Safety Assurance Case Receipts (`SACR-*`) at go‑live and material change; maintain Risk Register Entries (`RRE-*`) and Incident Report Receipts (`IRR-*`); treat waivers as logged, time‑bounded receipts (`SVR-*`).
- See: `139-risk-and-safety-assurance-governance.md`.

**OPEN-20 Queues & prioritization integrity**
- MUST: publish Queue Cards (QC-*), a versioned Priority Criteria Registry (PCR-*), and issue Queue Position Receipts (QPR-*) and Priority Decision Receipts (PDR-*) with bounded overrides, seam-safe transfers, and clocked remedies (joins 108/109/114/134).
- See: `140-queues-and-prioritization-integrity.md`.

**OPEN-21 Delegation & representation integrity**
- MUST: issue delegation receipts (DLR-* grant, DVR-* use, DRR-* revoke) and representative mandate receipts (RMR-*) with revocation clocks, conflict joins (`120`), and authority-of-record pointers (`115/118`).
- See: `141-delegation-and-representation-integrity.md`.

**OPEN-22 Metrics & indicators integrity**
- MUST: publish Metric Cards (`MIC-*`) for any metric used in decisions; issue Metric Change Receipts (`MCR-*`) on definition changes; and include Metric Use Receipts (`MUR-*`) inside Decision Receipts for high‑stakes outcomes (eligibility, sanctions, funding, queues).
- See: `142-metrics-and-indicators-integrity.md`.

**OPEN-3 Environmental information + participation rights**
- SHOULD: access to environmental information, participation in decisions, access to justice.
- Anchor: see [BIB-AARHUS].

**OPEN-4 Public statistics office / measurement independence**
- MUST: publish methods; protect independence; open microdata where safe; audit trails.
- See: `26-epistemic-infrastructure-and-public-knowledge.md` (Minimum Viable Epistemic Infrastructure).

**OPEN-5 Information integrity (public knowledge commons)**
- MUST: publish official information with provenance (source, method, uncertainty); separate facts from policy arguments.
- SHOULD: protect independence of official statistics and evaluation; publish corrections/errata; ensure equal access.
- For digital/public discourse risks: align transparency and accountability with the Global Digital Compact ([BIB-UN-GDC]).
- Anchor for statistics governance: see [BIB-UNFPOS].
- See: `26-epistemic-infrastructure-and-public-knowledge.md`.

**OPEN-6 Commons & ecological budgets**
- SHOULD: define ecological ceilings/floors, publish registries (permits/emissions/discharges), allocate transparently, and provide standing + access to justice.
- SHOULD: govern at ecological scales (watershed/airshed/bioregion) using compacts and joint bodies; prevent leakage with comparable measurement.
- Anchors: see [BIB-UNGA-76300]; [BIB-SEEA-CF]; [BIB-SEEA-EA]; [BIB-UNECE-WATER]; [BIB-PARIS]; [BIB-CBD-GBF].
- See also: `11-commons-and-ecological-governance.md`.

**OPEN-7 Public rules register (legal legibility)**
- MUST: a canonical public rules register with stable IDs, effective dates, and versioning (and binding guidance discipline).
- SHOULD: decisions cite Rule IDs so enforcement logs and appeals can travel across systems.
- See: `25-legal-legibility-and-rule-inventory.md`.

**OPEN-8 Program register & evaluation commitments (testable governance)**
- MUST: a public Program Register for major programs/policies with stable `PROG-*` IDs, legal basis (Rule IDs), predicted effects, and ≤10 success metrics (metric IDs where possible).
- MUST: an Evaluation Registry with stable `EVAL-*` IDs, publication timelines, independence/conflict disclosure, and a decision hook (revise/scale/stop).
- SHOULD: a small learning agenda (≤15 questions) and an annual evaluation plan mapping questions → `EVAL-*` IDs.
- See: `28-program-register-and-evaluation-commitments.md`.
- Implementation scaffold: use an OGP-style action-plan cycle with co-creation + “reasoned response” for public commitments (see [BIB-OGP-NHB-2025]).

**OPEN-9 Records + government memory (FOI precondition)**
- MUST: define “official records” (decisions + reasons + legal basis); capture official communications; retention schedule + legal holds.
- Anchors: see [BIB-COE-TROMSO]; [BIB-ISO-15489-1]; [BIB-ICA-ACCESS-2012].
- MUST: FOI/RTI request pipeline with Request IDs, time bounds, typed exemptions, disclosure log, and an appeal path.
- SHOULD: archival transfer + declassification cadence for high-stakes categories.
- See: `31-records-foi-and-government-memory.md`.

**OPEN-10 Influence transparency (regulatory footprint)**
- MUST: lobbying register + senior-official meeting log for major decisions; enforce revolving-door restrictions.
- SHOULD: “legislative/regulatory footprint” linking consultation inputs → draft text → final Rule IDs (publish dispositions).
- SHOULD: advisory committee/expert registers with conflicts, terms, and outputs.
- Anchor: see [BIB-OECD-LOB]; integrity framing: [BIB-OECD-PI].

---

## SAFE — Coercion controls (minimum-violence constraint)

**SAFE-1 Use-of-force policy codified in law**
- MUST: legality; necessity + proportionality; de-escalation-first; medical aid; mandatory reporting for *all* force.
- SHOULD: independent review of serious incidents; publish training doctrine + outcome audits (injury, complaints, racial equity).
- Anchors: see [BIB-UN-BPUFF].  
  UNODC resource book (implementation guidance): see [BIB-UNODC-UOF-RB].
- See: `116-coercion-use-of-force-and-detention-governance.md` (FER/DER receipts + serious-incident routing + coercion circuit breakers).


**SAFE-2 Independent oversight for coercive agencies**
- MUST: independent appointment + protected budget; investigatory access (incl. documents/bodycam); complaint intake; referral power; public reporting.
- SHOULD: separate (a) integrity/corruption and (b) rights/use-of-force review; random audits of stops/searches/detentions.

**SAFE-3 Emergency powers protocol**
- MUST: narrow scope; sunsets; renewal votes; judicial review; after-action report; compensation for rights infringements.
- SHOULD: strict documentation for “exceptions” (incl. emergency procurement); publish an “exceptions ledger.”
- See: `23-emergency-governance-and-exceptions.md` (Minimum Viable Emergency Governance + Emergency Measures Register) and `112-exception-control-and-emergency-powers.md` (Four Locks + Exceptions Ledger).

**SAFE-4 Custody & detention safeguards**
- MUST: prompt access to counsel; medical screening; time limits + judicial review; recording of interviews; humane minimum conditions; independent inspection access.
- SHOULD: a national preventive mechanism / regular visiting bodies for all places of detention.
- Anchors: Nelson Mandela Rules (UNODC edition): see [BIB-MANDELA].  
  Optional Protocol to CAT (OPCAT): see [BIB-OPCAT].  
  Méndez Principles on Effective Interviewing (2021): see [BIB-MENDEZ-2021].
  Code of Conduct for Law Enforcement Officials (OHCHR): see [BIB-UN-LEO-CODE].
- See: `116-coercion-use-of-force-and-detention-governance.md` (detention receipts + independent serious-incident pathway).


**SAFE-5 Security-sector governance (anti-politicization)**
- MUST: clear mandates and separation (police vs intelligence vs military); civilian control with legislative oversight; transparent procurement; sanctions for partisan enforcement.
- SHOULD: mutual aid agreements with audit trails; demilitarization defaults; rotation rules in sensitive units; protection for internal reporting.

---

## CAP — Capacity & finance (making decisions executable)

**CAP-1 Civil service merit + professional administration**
- MUST: protected hiring rules; transparent procurement; performance reviews; whistleblower protection.
- Anchor: see [BIB-OECD-PSLC].

**CAP-2 Budget system with readable public accounts**
- MUST: comprehensible budget; program objectives; quarterly execution reporting; public balance sheet.

**CAP-3 Fiscal transparency + risk management**
- SHOULD: publish fiscal risks, contingent liabilities, and tax expenditures; independent fiscal scrutiny.
- Anchor: see [BIB-IMF-FTC-2019].

**CAP-4 Independent fiscal institution (IFI)**
- SHOULD: independent forecasts/costings and rule compliance analysis; public methods; access to data.
- Anchor: see [BIB-OECD-IFI].
- See: `07-fiscal-and-budgetary-governance.md`.

**CAP-5 Intergovernmental fiscal transfers + equalisation**
- SHOULD: formula-based transfers; predictable timing; transparent objectives; “no unfunded mandate” rule; hard budget constraints (avoid bailout expectations).
- See: `18-intergovernmental-finance.md`.
- Anchor: see [BIB-OECD-IGFT-2025].
- Anchor: see [BIB-IMF-IGF-2018].
- Anchor: see [BIB-WB-IGFT-2007].

**CAP-6 Procurement + contracting integrity**
- MUST: default open competition; publish justifications for exceptions; publish contract lifecycle data where feasible.
- SHOULD: independent complaints channel; debarment with due process; bid-rigging pattern checks.
- See: `110-budget-procurement-integrity.md`.
- Anchor: see [BIB-OECD-PROC].
- Anchor: see [BIB-OCP-OCDS].

**CAP-7 Participatory allocation for bounded local discretionary spend**
- SHOULD: reserve a bounded portion of discretionary local spend for participatory budgeting (PB) with accessibility and auditability.
- See: `110-budget-procurement-integrity.md`.
- Anchor: see [BIB-WB-PB-GUIDE].


**CAP-8 Public service leadership + capability**
- SHOULD: workforce planning; competency frameworks; training pipelines; mobility; protected technical roles.
- Anchor: see [BIB-OECD-PSLC].
- See: `09-public-service-and-state-capacity.md`.

**CAP-9 Regulatory policy + rulemaking quality**
- MUST: public regulatory inventory; publish drafts; allow public comment; publish responses.
- SHOULD: RIA for major rules; publish assumptions; ex-post review triggers (sunset/review clauses).
- Anchor: see [BIB-OECD-RPG-0390].
- Measurement anchor: see [BIB-WB-GIRG].
- See: `13-regulation-utilities-and-soes.md`.

**CAP-10 State-owned enterprise (SOE) governance**
- SHOULD: explicit ownership policy; professional boards; separate ownership from regulation; competitive neutrality where relevant.
- MUST: publish audited financials and state support/guarantees; consolidate fiscal risks (`CAP-3`).
- Anchor: see [BIB-OECD-SOE-2024].
- See: `13-regulation-utilities-and-soes.md`.

**CAP-11 Appointments & tenure integrity (personnel power)**
- MUST: publish role criteria, process, conflicts, and reasons for appointments/removals (bounded by safety needs).
- MUST: time‑bound acting/interim roles and publish the plan to fill permanently; prohibit “acting‑forever”.
- SHOULD: cooling‑off/incompatibilities for capture‑sensitive roles; staggered terms for boards.
- See: `113-appointments-and-tenure-integrity.md`.


**CAP-12 Mandates & jurisdiction scope integrity (authority surface)**
- MUST: publish one-page Mandate Cards (`MC-*`) with competences + non‑competences, contest lanes, and interface outputs.
- MUST: receipt any delegation (`DLG-*`) and any competence shift (`SCR-*`); maintain an overlap/gap register (`OGR-*`).
- See: `132-mandates-and-jurisdiction-scope-integrity.md`.

---

## IOP — Interfaces & infrastructure (how systems plug together)

**IOP-1 Compacts (contract-like intergovernmental agreements)**
- MUST: scope + competence boundaries; contributions and money discipline; transparency + audit; 3–10 metrics; enforcement ladder; dispute path; exit/sunset + continuity plan.
- See: `19-compacts-and-cooperative-governance.md`.

**IOP-2 Mutual recognition, portability, and continuity**
- MUST: a portability kit that prevents boundary cliffs (Continuity Receipts, provisional continuity, non-reset evidence, appeal jurisdiction). See `109-portability-and-cross-jurisdiction-continuity.md`.
- SHOULD: mutual recognition for credentials/benefits/judgments with a small minimum standard + published deltas.

**IOP-3 Shared data schemas (interoperability with privacy)**
- SHOULD: standard schemas for budgets/procurement/outcomes; role-based access; audit logs.

**IOP-4 Digital public infrastructure as a public good**
- SHOULD: open standards, open source where feasible, privacy-by-design, “do no harm”.
- Anchors: DPG Standard [BIB-DPG-STANDARD] and UN framing of digital public goods: see [BIB-UN-DPG].

**IOP-5 Automated decision systems (ADS) governance**
- MUST: public `ADS-*` system register (purpose, legal basis, vendor/`CON-*`, data sources/`DPR-*`, risk tier, appeal `AL-*`).
- **Canonical spec:** `42-automated-decision-systems-and-model-registry.md` (includes optional `MOD-*` model entries for reused/high-impact models).
- MUST: audit logs, versioning, and **Reason Code(s)** (`RC-*`, portable taxonomy in `52-reason-codes-registry.md`) sufficient for accountability and remedy.
- SHOULD: risk-tiered review (impact assessment + independent audit for high-stakes domains).
- MUST: meaningful human review + fast appeal channel for rights-affecting decisions (`LAW-3`, `ACC-3`).
- SHOULD: procurement clauses for auditability, portability/exit, security, and independent testing rights.
- Anchors: see [BIB-OECD-AI]; [BIB-NIST-AIRMF]; [BIB-EU-AIACT]; [BIB-COE-AI].

**IOP-6 Identity, civil registration, and recognition (who counts)**
- MUST: universal CRVS backbone (birth/death at minimum) with practical access and late-registration paths.
- MUST: legal identity issuance that avoids exclusion-by-design (non-discrimination, feasible enrollment without perfect documents).
- MUST: correction + appeal pathways for identity/status errors (`LAW-5`).
- MUST: purpose limitation + minimization + independent oversight to prevent function creep.
- SHOULD: cross-boundary document authentication / recognition rules (default recognize; document exceptions).
- SHOULD: open standards for digital credentials and portability (avoid proprietary lock-in).
- Anchors: see [BIB-UN-LIA]; [BIB-WB-ID-PRINCIPLES]; [BIB-HCCH-APOSTILLE]; [BIB-W3C-VC2].

**IOP-7 Mutual aid & serious incident protocol (cross-scope safety operations)**
- MUST: mutual-aid activation log (who requested/assisted/command/legal basis/time bounds/cost rules).
- MUST: independent serious-incident pipeline (case IDs, evidence integrity, public timelines).
- See: `24-mutual-aid-and-serious-incident-protocol.md`.

**IOP-8 Standards register & open standards governance (technical rules as governance)**
- MUST: a **Public Standards Register (PSR)** for any standard that is required for access, incorporated by reference, or required in essential procurement; include pinned versions and transition/deprecation plans.
- MUST: conformance statement + test/validator link (standards without tests are aspirational).
- MUST: incorporated standards are publicly accessible (avoid “paywalled law”); PRR Rule IDs MUST reference PSR `STD-*` IDs.
- SHOULD: open, balanced process with conflict disclosure and a light appeals route; disclose licensing/IP terms.
- See: `27-standards-and-technical-governance.md`.

**IOP-9 Public registers & stable IDs (register pattern)**
- MUST: any governance register (rules, standards, data releases, compacts, emergency measures, transfers, ADS) assigns stable IDs, publishes machine-readable entries, and keeps a change log (no silent revisions).
- SHOULD: for core feeds and high-stakes releases, use signed bundles (hash manifest + signature) and optional append-only transparency logs to prevent silent rewrites (see `53-publication-integrity-and-tamper-evident-logs.md`).
- MUST: IDs are join-keys referenced in notices/reasons, audits, and remedies.
- SHOULD: rights-affecting decisions issue a short **decision receipt** with a stable Decision ID (`DRR`), citing Rule IDs, **Reason Code(s)** (`RC-*`), evidence/release IDs, and the appeal lane (`AL-*`) / time limits (see `08-remedy-and-grievance.md`, `31-records-foi-and-government-memory.md`).
- SHOULD: exemptions and non-public entries are typed, justified, and time-bounded where feasible.
- See: `70-interoperability.md` (register pattern) and the specific register memos (`18`, `19`, `23`, `25`, `26`, `27`, `06`).

**IOP-10 Scope assignment & mandate transfer protocol (subsidiarity made auditable)**
- MUST: creating a new authority, delegating decision rights in a compact, changing boundaries, or transferring a mandate produces a public `DRR` tagged `DRR-TYPE: SCOPE` that records:
  - the scope tests (local knowledge, spillovers, scale economies, rights/capture risk, enforceability),
  - funding alignment (who pays/bears residual risk),
  - remedy continuity (where appeals go during/after transition),
  - the competence-ledger change (old → new entry/version) and effective date,
  - the review/sunset trigger (when we reconsider the assignment).
- SHOULD: cite the smallest credible evidence (spillover mapping, scale/capex constraints, capacity floor) rather than narratives.
- Canonical test + docket: `54-subsidiarity-and-scope-assignment-test.md`.
- See: `14-scope-ladder.md`, `17-jurisdiction-formation-and-boundaries.md`, `70-interoperability.md`. Anchors: [BIB-FAGUET-2014-WORLDDEV]; [BIB-WEINGAST-MPF-1995-JLEO]; [BIB-OSTROM-POLYCENTRIC-2010].

**IOP-11 Competence ledger & mandate registry (public jurisdiction map)**
- MUST: publish and maintain a versioned competence ledger of **Unit IDs** that states who can decide what, who funds it, and where remedy goes.
- MUST: include functional authorities / special districts (otherwise they become “hidden government”).
- SHOULD: publish a ledger staleness report (entries not reviewed in X months) and treat it as a governance risk.
- SHOULD: tag fiscal-facing mandates using a shared taxonomy (baseline: **COFOG**) to keep scope transfers auditable.
- See: `34-competence-ledger-and-mandate-registry.md`, `70-interoperability.md`.
- Anchors: [BIB-UNSD-COFOG]; [BIB-IMF-GFSM-2014]; [BIB-USCENSUS-SPECIALDIST-2022].

**IOP-12 Transfer register & conditionality log (make money portable and contestable)**
- MUST: publish a versioned **Transfer Register** of `TRF` objects for all material intergovernmental flows (formula, amounts, timing, payer/recipient Unit IDs, and any conditions).
- MUST: type any conditionality and publish withholding/clawback events with reasons and a dispute path (no discretionary fiscal punishment).
- SHOULD: link transfers to compacts (`CMP`) where relevant and to `DRR-TYPE: SCOPE` when transfers finance mandate moves.
- See: `35-transfer-register-and-conditionality.md`, `18-intergovernmental-finance.md`, `70-interoperability.md`.
- Anchors: [BIB-OECD-IGFT-2025]; [BIB-IMF-IGF-2018]; [BIB-IMF-FTC-2019].

**IOP-13 Appeal lanes & redress registry (ALR) (contestability interface)**
- MUST: publish a versioned **Redress Registry** of `AL-*` lanes (coverage, deadlines, filing channels, remedies, interim protection, costs/waivers, and independence notes).
- MUST: every enforceable rights-/resource-affecting decision receipt (`DRR`) cites ≥1 `AL-*` lane that can provide **effective relief** (or a narrow, logged exception).
- MUST: lane changes publish a crosswalk (old → new) and effective date; scope/competence changes (`DRR-TYPE: SCOPE/COMPETENCE`) include a remedy-continuity plan mapping decisions to lanes.
- SHOULD: define an urgent-protection lane for high-stakes harms (stay/suspension or equivalent) and publish aggregate outcomes (`AO-*`) + timeliness/backlog signals by lane.
- See: `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md`, `31-records-foi-and-government-memory.md`, `70-interoperability.md`.
- Anchors: [BIB-EU-CHARTER-A47]; [BIB-COE-GOODADMIN-2007]; [BIB-UN-REMEDY-60147]; [BIB-VENICE-OMB-2019].

**IOP-14 Claims & evidence discipline (make predictions joinable)**
- MUST: major programs/policies maintain ≥1 testable claim (`CLM-*`) that names the outcome, metrics, baseline, target range, plausible harms/guardrails, and a review trigger.
- MUST: evaluations (`EVAL-*`) cite the `CLM-*` IDs they test and publish a response (program revision or follow-on `DRR`) that updates claim status (supported/contested/falsified/retired).
- SHOULD: decision receipts (`DRR`) cite `CLM-*` when asserting predictions, alongside the evidence docket (`REL/EVAL/OFR/EXT`).
- See: `37-claims-evidence-and-update-discipline.md`, `28-program-register-and-evaluation-commitments.md`, `03-metrics-and-evidence.md`, `70-interoperability.md`.
- Anchors: [BIB-UK-MAGENTA-2025]; [BIB-US-EVIDENCEACT-EVALGOV]; [BIB-OECD-GAAG2025-EXPOST].

**IOP-15 Open contracting (make procurement joinable)**
- MUST: publish a Contracting & Procurement Register keyed by a stable `CON` (prefer OCID where using OCDS) covering tender→award→delivery→close-out, including amendment/change-order logs.
- MUST: awards and major amendments cite a `DRR` (legal basis + reason) and name the `AL-*` lane(s) for bid protest / supplier sanctions.
- SHOULD: link procurement to funding (`TRF` when transferred) and programs/claims (`PROG` / `CLM`) when procurement is part of a policy intervention.
- See: `38-contracting-and-procurement-register.md`, `22-public-integrity-and-procurement.md`, `70-interoperability.md`, `07-fiscal-and-budgetary-governance.md`.
- Anchors: [BIB-OCDS]; [BIB-OECD-PROC]; [BIB-UNCAC].

---

## Cross-cutting anti-capture patterns (use everywhere)
- **Budget independence** for watchdogs (formula-based; difficult to starve quietly).
- **Staggered terms + transparent appointments** with multi-branch approval.
- **Rotation + cooling-off periods** for high-risk roles.
- **Randomized audits + red-team reviews** for programs with discretion.

## GATE — Shipping discipline (meta-engineering)

**GATE-0 Problem framing (fast, written, required for anything that expands discretion)**
Before designing a new rule/program/system, write (and publish where feasible) one tight page:

- **Problem:** what harm/failure mode are we fixing (and what happens if we do nothing)?
- **Scope/authority:** which unit and competence boundary owns this?
- **Threat scan:** pick the top 3 plausible `TM-*` failures and name the smallest design countermeasure for each.
- **Baseline:** pick ≤10 metric IDs (and, where possible, the Release IDs) that will govern revision/sunset.
- **Non-goals:** what this does *not* attempt to solve (prevents mandate creep).

**GATE-1 Pre-launch design review (one page, required for high-impact changes)**
Before shipping a new rule/program/system (especially anything coercive, rights-affecting, or high-budget), publish a short review that answers:

- **Authority:** which competence-ledger entry + `RULE-*` IDs authorize this?
- **Contestability:** what is the appeal lane (`AL-*`), and what is the Decision Receipt / `DRR` plan?
- **Openness:** what registers/releases will be public by default (and what exemptions are typed/time-bounded)?
- **Threats:** which `TM-*` failure modes are plausible, and which mitigations are in the design?
- **Metrics:** which ≤10 metric IDs will govern revisions (and what is the decision hook)?
- **Exit:** what is the rollback/sunset plan (and what happens to ongoing cases/contracts/data)?

This prevents “policy by slide deck” and keeps the archive’s primitives operational.

**GATE-2 Post-launch reality check (fast, published)**
After deploying a high-impact rule/program/system, publish a short review on a fixed cadence (e.g., 90 days, then annually):

- **What happened vs. predicted:** the ≤10 metric IDs used at launch, what moved, and what didn’t.
- **Harms and contestation:** incidents (`DAG-4`), appeals/complaints volume, time-to-remedy, and any pattern findings (`OFR-*`).
- **Exceptions and drift:** emergency/exception usage, scope expansion, and any new data processing (`DPR-*`) since launch.
- **Procurement and vendor claims:** uptime/outages, audit results, portability/exit readiness (no “forever pilots”).
- **Decision hook:** keep / revise / scale / sunset, with a dated next review.

This keeps “ideal” designs reversible and forces learning loops into the default lifecycle.

**IOP-16 Public Rules Register (make enforceable norms queryable)**
- MUST: maintain a Public Rules Register (PRR) with stable `RULE` IDs, effective windows, versioning, and `AL-*` appeal lanes.
- MUST: enforcement-facing `DRR`s cite `RULE` **versions/as-of**; prohibit “dark enforcement” (rules that are enforced but not findable).
- SHOULD: flag guidance that functions like law (`GLAW`) until clarified; sunset low-value rules.
- MAY: publish machine-readable legal interchange and derivative “rules as code” implementations, explicitly subordinate to the legal text.
- See: `39-rulebook-and-instruments-registry.md`, `25-legal-legibility-and-rule-inventory.md`, `31-records-foi-and-government-memory.md`, `70-interoperability.md`.
- Anchors: [BIB-OECD-RPG-0390]; [BIB-OASIS-AKN-2018]; [BIB-CIGI-RAC-2025].

**IOP-17 Participation & Deliberation Register (make legitimacy inputs joinable)**
- MUST: maintain a Public Participation & Deliberation Register keyed by stable `ENG` IDs for any process intended to influence public decisions (consultations, PB, citizens' assemblies, etc.).
- MUST: every `ENG` entry names a **decision hook** (authorizing or target `DRR`) and a **duty-to-respond** deadline; the official response MUST be a linked `DRR`.
- MUST: publish a process complaint lane (`AL-*`) and link any facilitation/platform procurement (`CON`) and funding (`TRF`) when relevant.
- SHOULD: for representative deliberative processes, publish sampling and inclusion parameters (aggregates; protect participant safety) and evaluate against minimum standards.
- See: `41-public-participation-and-deliberation-register.md`, `21-legitimacy-architecture.md`, `70-interoperability.md`.
- Anchors: [BIB-OECD-CITPART-2022]; [BIB-OECD-DEL-EVAL-2021]; [BIB-IAP2-COREVALUES].
**IOP-18 Enforcement & custody event logging (no dark enforcement)**
- MUST: maintain an Enforcement & Custody Event Register keyed by `ENF` IDs for any action affecting liberty/property/bodily integrity (stop/search/seizure/arrest/detention/use-of-force).
- MUST: subjects receive a Decision Receipt that cites `ENF-*`, `RULE-*` basis (as-of), and the complaint/review lane `AL-*`—unless a documented safety exception applies.
- MUST: custody episodes are logged start→end with welfare/medical checkpoints; serious incidents trigger independent pipeline and link to `OFR-*`.
- SHOULD: publish a de-identified public release (with `REL-*` revision logs) plus typed FOI exemptions for protected details.
- **Canonical spec:** `43-enforcement-and-custody-event-register.md` (see also `05-...`, `24-...`, `31-...`, `36-...`, `70-...`).

**IOP-19 Identity & credential gate transparency (make access gates auditable)**
- MUST: maintain an Identity & Credential Systems Register keyed by `IDN` IDs for any identity proofing / credential issuance / verification system used to gate access to public services or status.
- MUST: any denial/restriction due to identity/eligibility MUST issue a `DRR` receipt citing `RULE` basis (as-of), the relevant `IDN-*`, and the appeal lane `AL-*` (and `ADS-*`/`MOD-*` when automation is material).
- MUST: link identity-gate procurement (`CON-*`) and conditional funding (`TRF-*`) when relevant; link the data processing activity (`DPR-*`) and correction deadlines.
- SHOULD: publish explicit “prohibited joins” to prevent identity infrastructure from becoming stealth surveillance; cross-boundary recognition should be governed by compacts (`CMP-*`) and prefer verifiable claims where feasible.
- **Canonical spec:** `44-identity-credential-and-eligibility-systems-register.md` (see also `12-...`, `33-...`, `36-...`, `39-...`, `42-...`, `70-...`).
- Anchors: [BIB-NIST-800-63-4]; [BIB-OECD-DIGID-REC]; [BIB-W3C-VC2].

**IOP-20 Emergency Measures Register (no “dark emergency government”)**
- MUST: publish an Emergency Measures Register keyed by stable `EMR` IDs (episode + measures) with explicit sunsets and renewal/termination receipts.
- MUST: declaration/renewal/termination are `DRR` decisions citing `RULE` versions/as-of and relevant `AL-*` lanes.
- MUST: any emergency exception in procurement (`CON`), data access (`DPR`), coercion (`ENF`), transfers (`TRF`), or permitting (`PAR`) MUST cite `EMR-*`.
- SHOULD: require after-action review and closure artifacts (`OFR-*`/`EVAL-*`).
- **Canonical spec:** `45-emergency-measures-register.md` (see also `23-...`, `70-...`, `80-...`).

**IOP-21 Influence & Interests Register (make influence joinable)**
- MUST: maintain a public Influence & Interests Register keyed by `INF` (influence interactions: meetings/contacts/gifts/travel above threshold) and `INT` (interest declarations / COI management actions).
- MUST: for high-risk decision classes, issuing `DRR`s MUST either cite relevant `INF-*` disclosures or declare `INF: NONE DECLARED` (ex parte disclosure discipline).
- MUST: recusals / ethics determinations that alter decision authority MUST be issued as `DRR`s citing the relevant `INT-*` and (when needed) competence-ledger updates.
- SHOULD: link procurement (`CON-*`) and transfer conditionality (`TRF-*`) to relevant `INF/INT` integrity joins where conflicts exist.
- **Canonical spec:** `46-influence-and-interests-register.md` (see also `22-...`, `32-...`).

**IOP-22 Service Catalog & Access Journeys Register (make service power legible)**
- MUST: maintain a public Service Catalog & Access Journeys Register keyed by stable `SRV` IDs (service definitions, not personal cases).
- MUST: each `SRV` entry cites `RULE` basis (versions/as-of), owning Unit ID, channels/fees/time commitments, and `AL-*` remedy lanes.
- MUST: rights-/resource-affecting decisions inside a service MUST issue `DRR` receipts that cite `SRV-*` + `RULE-*` (as-of) + `AL-*` (and `IDN` / `ADS` / `CON` / `TRF` / `EMR` when relevant).
- SHOULD: publish a small “burden budget” (step/doc/time/abandonment/rework) keyed by `SRV-*` and feed it into delivery metrics (CAD-2).
- **Canonical spec:** `47-service-catalog-and-access-journeys-register.md` (see also `09-...`, `31-...`, `08-...`, `70-...`).
- Anchors: [BIB-RSF-ADMINBURDEN-2018]; [BIB-OECD-GPP-SERVICE-2022]; [BIB-UK-SERVICESTANDARD].

**IOP-23 Asset & Infrastructure Register (make physical power auditable)**
- MUST: maintain a public Asset & Infrastructure Register keyed by stable `AST` IDs for material public/critical assets.
- MUST: capital approvals/awards and major maintenance deferrals MUST cite affected `AST-*` (and link `CON-*` / `PROG-*` / `TRF-*` / `EMR-*` when relevant).
- SHOULD: publish condition grades + inspection cadence, and a backlog estimate, with methods referenced via `REL-*` releases (prevents “hand-wavy” condition claims).
- SHOULD: link critical service outages to `AST-*` and affected `SRV-*` for accountability and learning.
- **Canonical spec:** `48-asset-and-infrastructure-register.md` (anchors: [BIB-OECD-INFRA-2020]; [BIB-IMF-PIMA-2022]; [BIB-ISO-55000]).

**IOP-24 Oversight Findings & Response Register (OFRR) (make follow-through auditable)**
- MUST: oversight findings/cases issue a stable `OFR-*` and appear in a public OFRR with a duty‑to‑respond, remediation milestones, and closure verification.
- SHOULD: OFRR links to `DRR` receipts, `RULE` basis (as‑of), evidence releases (`REL-*`), and any relevant appeal lanes (`AL-*`).
- SHOULD: for constitutional feeds, apply tamper‑evident publication discipline (see `53-publication-integrity-and-tamper-evident-logs.md`).
- See: `55-oversight-findings-and-response-register.md` (register spec) and `32-oversight-institutions-and-follow-through.md` (oversight stack + independence protections).

**IOP-25 Critical infrastructure & cyber resilience spine (MV‑CICRG)**
- MUST: treat service‑critical IT/OT as `AST-*`; publish a baseline controls profile as a `REL-*` release (mapped to pinned `STD-*`); log material incidents as `DRR-TYPE: INCIDENT` and open an `OFR-*` case with follow‑through; log emergency cyber actions as `EMR-*` where exceptional authority is used.
- SHOULD: publish coarsened public notices and postmortems as `REL-*` (two‑layer model); make risk‑acceptance/exception approvals time‑bounded `DRR`s with `RC-*` reason codes and review dates; bind procurement to baseline controls (CLC + security obligations).
- See: `59-critical-infrastructure-and-cyber-resilience-governance.md`.

**IOP-26 Assurance case & monitoring (governance safety case for high-discretion power)**
- MUST: for coercion, emergency powers, high-stakes automated decisions, critical infrastructure operations, cross-boundary regimes with weak exit, or material fiscal tail-risk, publish an `AC-*` assurance case summary (claim–argument–evidence) with assumptions, monitoring thresholds, stop/review triggers, and remedy lanes.
- MUST: evidence is pointers by stable IDs (`REL/EVAL/OFR/DRR/STD/CON`), not bulky annexes; revisions are versioned (no silent edits).
- SHOULD: require independent challenge for high-risk `AC-*` and publish an `AC` staleness report (missed review dates as governance risk).
- See: `73-assurance-case-and-governance-safety-case.md`.
- Anchors: [BIB-ISO-IEC-15026-2]; [BIB-OMG-SACM-2-1]; [BIB-GSN-COMMUNITY-STD-2011]; [BIB-HSE-COMAH-SAFETYREPORTS].

**IOP-27 Sunset & deprecation discipline (keep power reversible)**
- MUST: every high-discretion power, high-spend program, and major rule set publishes a review date and renewal standard; default is **sunset unless renewed**.
- MUST: renewals/terminations emit joinable `DRR-*` receipts that cite the governed object(s) (`RULE/PROG/AC/EMR/STD/ADS/DPR/CON`) and the evidence docket (`REL/EVAL/OFR`).
- MUST: missed review dates are treated as governance incidents: open an `OFR-*` case (`LEGIBILITY-GAP`) with remediation deadlines.
- MUST: deprecations include continuity rules (no orphaned cases, remedy lane crosswalks) and a minimal decommission plan for records/data.
- See: `74-sunsetting-and-deprecation-discipline.md`.

**IOP-28 Retrospective review / regulatory lookback (keep rules fit for purpose)**
- MUST: for high-impact `RULE-*` regimes, publish a forward **review plan** (what will be reviewed when) and embed a review clock at creation (or justify why not).
- MUST: renew/repeal/replace decisions emit `DRR-*` receipts citing the affected `RULE-*` and the review evidence (`REL/EVAL/OFR`) (no “silent continuation”).
- SHOULD: publish a one-screen **review packet** at creation (metrics + distributional checks + remedy health + renewal standard) and update it at review time (pointer bundle only).
- See: `74-sunsetting-and-deprecation-discipline.md`, `39-rulebook-and-instruments-registry.md`, `28-program-register-and-evaluation-commitments.md`.
- Anchors: [BIB-OECD-STOCK-REVIEW-2020]; [BIB-UK-BRF-GUIDE-2023]; [BIB-EU-BR-TOOLBOX-2023]; [BIB-US-EO13563-2011].

**IOP-29 Systemic redress & pattern remediation (turn recurring harms into correction loops)**
- MUST: publish systemic-trigger thresholds for remedy health (volume spikes, `AO-NORESP` ceilings, disparity signals).
- MUST: when triggered, open a scoped systemic `OFR-*` case (sample `DRR-*`, cite `RULE-*` as-of, publish corrective actions + deadlines, close only with evidence).
- MUST: lane records disclose whether collective filing is supported (`COLLECTIVE-FILING` in `36-...`); if not, they MUST name the substitute mechanism and record the gap as design debt (`08`, `36`, `76`).
- SHOULD: high-discretion regimes include systemic redress triggers in the `AC-*`.
- See: `76-systemic-redress-and-pattern-remediation.md` and `08-remedy-and-grievance.md`.

**IOP-30 Sensitive information & secrecy governance (make exceptions auditable)**
- MUST: if the payload cannot be public, publish the **receipt** (withholding/classification `DRR-*` with `RC-*` category + legal basis + review/declassification date + `AL-*` lane).
- MUST: maintain a public withholding log (existence metadata) and ensure independent review with protective access to unredacted records.
- See: `77-sensitive-information-and-secrecy-governance.md`, `31-records-foi-and-government-memory.md`, `53-publication-integrity-and-tamper-evident-logs.md`.

**IOP-31 Delegation & acting authority discipline (make authority chains auditable)**
- MUST: publish a role-level **Authority Schedule** (signatory matrix) per Unit ID as a versioned `REL-*` release (diffable; no silent edits) and link it from the competence ledger entry.
- MUST: delegations/acting appointments/revocations emit `DRR-*` receipts tagged `DRR-TYPE: DELEGATION` (scope + limits + time bounds + legal basis + remedy lane).
- SHOULD: consequential decision receipts include `SIGNATORY-ROLE` and cite the relevant delegation `DRR` when acting/delegated authority applies.
- MUST: outsourcing/automation cannot expand authority: vendor-operated workflows cite `CON-*` (CLC pack) and automation cites `ADS-*`; discretion limits remain those of the authorizing role.
- See: `78-delegation-and-acting-authority-discipline.md` (and `34-...`, `31-...`, `38-...`, `06-...`).

**IOP-32 Conflict-of-interest & revolving door discipline (bind influence to decisions)**
- MUST: covered roles maintain `INT-*` declarations (public status + categories; sensitive detail in protected layer with audit logs) and management actions emit `DRR-*` receipts tagged `DRR-TYPE: INTEGRITY` when they change authority or decision participation.
- MUST: for covered decision classes (procurement awards/amendments, permits/variances, major regulatory changes, enforcement discretion), the `DRR-*` receipt cites `INF-*` interactions or `INF: NONE DECLARED`.
- MUST: revolving-door entry/exit restrictions and any waivers are time-bounded `DRR-TYPE: INTEGRITY` receipts linked to `INT-*` (and to `INF-*` when contact will occur).
- SHOULD: publish [IPM-20] and treat chronic low disclosure/overdue status as an audit trigger (`OFR-*`).
- See: `79-conflict-of-interest-and-revolving-door-discipline.md`, `46-influence-and-interests-register.md`, and `22-public-integrity-and-procurement.md`.

**IOP-33 Verification & inspection spine (make obligations checkable)**
- MUST: any regime that relies on compliance (treaty/compact, regulated standard, conditional funding, safety/cyber baseline) defines a Minimum Viable Verification & Inspection spine:
  - obligations inventoried (`RULE-*` / `STD-*` / `CMP-*` as‑of),
  - evidence published as `REL-*` with methods + revision logs,
  - a published verification schedule (coverage + sampling logic),
  - material findings emit typed `DRR-*` with `RC-*` reasons + `AL-*` lanes,
  - and material/non‑recurring findings open `OFR-*` follow‑through with closure evidence.
- SHOULD: pre-commit a public compliance ladder (assist → warn → corrective plan → penalty → suspension/referral).
- See: `81-verification-inspection-and-compliance-ladders.md` (and `51-...`, `55-...`, `73-...`, `77-...`).

**IOP-34 Service standards & minimum service guarantees (make service power measurable)**
- MUST: core services define a Service Standard (SS) and (for essential services) a Minimum Service Guarantee (MSG) keyed to `SRV-*`.
- MUST: publish service performance as `REL-*` with method notes; chronic misses trigger a systemic `OFR-*` (and interim protections for `ESS-1` services).
- MUST: service-facing denials/restrictions issue `DRR` receipts citing `SRV-*` + `RULE-*` (as-of) + `AL-*`.
- MUST: person-facing interfaces (receipts, notices, portals) satisfy **comprehension + navigation** invariants (and the dignity standard): plain-language reasons, next steps, and a “no wrong door” route that preserves clocks/tracking. See `98-persons-path-and-accessibility-invariants.md` and `82-...`.
- See: `82-service-standards-and-minimum-service-guarantees.md` (and `47-...`, `08-...`, `76-...`).

**IOP-35 Protected disclosures & anti-retaliation (make integrity speakable)**
- MUST: maintain protected disclosure lane(s) (`AL-*`) with at least one **independent** channel that can bypass the implicated chain of command.
- MUST: publish a finite triage taxonomy + timelines; intake and retaliation determinations emit typed `DRR-*` with `RC-*` reasons.
- MUST: publish periodic disclosure/retaliation statistics as `REL-*` (method noted); systemic patterns trigger `OFR-*` follow‑through.
- See: `83-whistleblowing-and-protected-disclosures.md` (and `22-...`, `79-...`, `77-...`).

**IOP-36 Internal controls & continuous assurance (make execution defensible)**
- SHOULD: for units with material money/coercion/high-stakes automation, publish a `REL-*` **control map** (material risks → controls → basis) and a periodic **control test plan + results** (methods noted; no silent edits).
- MUST: material exceptions route into follow‑through (`OFR-*`) with deadlines and closure evidence; missing required control artifacts are incidents (contestable).
- See: `84-internal-controls-and-continuous-assurance.md` (and `55-...`, `07-...`, `81-...`, `77-...`).

**IOP-37 Waivers / variances / exceptions discipline (no discretion without a receipt)**
- MUST: non-emergency departures from `RULE-*`/`STD-*`/`SRV-*`/control baselines emit `DRR-*` tagged `DRR-TYPE: EXCEPTION` with legal basis, bounds, expiry, and `AL-*` contestation lane(s).
- SHOULD: publish a periodic exception log as a `REL-*` release (existence metadata + review dates even when details are withheld).
- MUST: renewals/revocations emit new receipts (no silent extensions); variance-creep triggers route to a scoped `OFR-*` case.
- See: `85-waivers-variances-and-exceptions-discipline.md`.

**IOP-38 Regulatory experimentation / sandboxes discipline (safe-to-fail with explicit learning + exit)**
- MUST: any live testing under relaxed conditions is governed as a `PROG-*` with objectives, eligibility, protections, monitoring, and stop conditions; admissions emit receipts (`DRR-TYPE: EXCEPTION`).
- MUST: publish cohort closeouts as `REL-*` learning releases (including negative results) and treat missing closeouts as incidents.
- MUST: scaling requires rule updates (`RULE-*`/`STD-*`)—no “pilot-to-permanent” without a public rationale receipt.
- See: `86-regulatory-experimentation-and-sandboxes.md`.
**IOP-39 Evaluation & learning receipts (close loops; prevent policy zombies)**
- MUST: for material programs/rules/budget lines, publish a joinable chain: `DRR-*` → `CLM-*` → `EPR-*` → `EFR-*`/`PIRR-*` → `DUR-*` (continue/modify/pause/retire).
- MUST: maintain a lightweight Learning Register (`LR-*`) so any reform’s evidence and updates are replayable.
- SHOULD: evaluation commitments travel with transfers (no reset at seams); negative findings trigger a scoped circuit breaker (`104`/`105`).
- See: `133-evaluation-and-learning-integrity.md` (protocol), `37-claims-evidence-and-update-discipline.md`, `28-program-register-and-evaluation-commitments.md`.
- Anchors: [BIB-US-EVIDENCEACT-EVALGOV]; [BIB-UK-MAGENTA-2025]; [BIB-OECD-GAAG2025-EXPOST]; [BIB-OECD-DAC-EVAL-2019].
