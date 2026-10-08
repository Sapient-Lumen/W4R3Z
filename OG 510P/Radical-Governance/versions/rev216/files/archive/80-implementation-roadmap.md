# Implementation Roadmap (From “Today” to “Ideal”)

**Purpose:** sequence adoption under real constraints, starting with receipt-first bootstraps that create enforceable footholds.

This roadmap prioritizes **reversible, compounding upgrades**: build legitimacy and auditability first, then expand capability.

**Material floor:** the MVGS is “cheap” relative to many reforms, but it is not free. It requires:
- **revenue** to run oversight/records/remedy infrastructure,
- **staff capacity** (supervision, training, caseload control),
- **safety** for both frontline staff and complainants, and
- person‑side **time/literacy** to navigate systems.

Where these are missing, treat them as **parallel workstreams** and start with Phase −1 receipt‑first bootstraps that reduce burden rather than adding it (`99-protective-legibility-and-adoption-dynamics.md`, `98-persons-path-and-accessibility-invariants.md`, `09-...`).

## Kernel anchors (do not repeat)
- Complexity budget / archive governance: `96-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md`.
- Person-facing floors (no AI-only gate; assisted channels): `98-persons-path-and-accessibility-invariants.md`.
- Publication integrity and minimal join keys: `53-...`, `70-...`.

## Named tensions (design must surface these)
- Ambition vs capacity (build floors first; avoid brittle “big bang”).
- Sequencing discipline vs urgency (triage without abandoning rights).
- Standardization for interoperability vs plural institutions and functional equivalents.
- Publishing constraints vs safety (avoid exposing targets while enabling contestation).

---



## Minimal Viable Governance Stack (MVGS)
Ship these **public artifacts** first. They create join-keys for legitimacy, auditability, and remedy across scopes.

| Artifact | What it makes possible | Join keys / IDs | See |
|---|---|---|---|
| Competence ledger | clarity on who decides what; prevents “hidden government” | Unit IDs | `34-competence-ledger-and-mandate-registry.md`, `70-interoperability.md` |
| Public Rules Register (PRR) | decisions cite Rule IDs + versions/as-of; enforce and appeal consistently | `RULE` | `39-rulebook-and-instruments-registry.md` |
| Decision Records / Receipts | reasons + legal basis + appeal lanes become portable across scopes (including scope assignment decisions) | `DRR` (+ linked `RULE`/`REL`/`DPR` where relevant; include `RC-*` reason codes; use `DRR-TYPE: SCOPE` for mandate transfers) | `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md`, `52-reason-codes-registry.md` |
| Service Catalog & Access Journeys Register | services become legible; reduces procedural denial and channel exclusion; ties delivery metrics to a defined service **and** publishes essentiality/continuity floors for stress periods | `SRV` | `47-service-catalog-and-access-journeys-register.md`, `82-service-standards-and-minimum-service-guarantees.md`, `09-public-service-and-state-capacity.md` |
| Asset & Infrastructure Register | makes capex, maintenance, and outages auditable; reduces deferred-maintenance failure and “emergency repair” corruption | `AST` | `48-asset-and-infrastructure-register.md`, `07-fiscal-and-budgetary-governance.md` |
| Enforcement & custody event register (where coercive units exist) | no dark enforcement; joinable oversight and harm reduction | `ENF` (linked to `DRR` receipts + `RULE` as-of + `AL-*`) | `43-enforcement-and-custody-event-register.md`, `05-public-safety-and-coercion.md`, `24-mutual-aid-and-serious-incident-protocol.md` |
| Redress Registry (ALR) | appeal lanes are discoverable; urgent protection is explicit; lane changes are cross-walked | `AL` / `AL-*` | `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md` |
| Participation & Deliberation Register | participation is auditable; prevents consultation-washing; links inputs → official response | `ENG` | `41-public-participation-and-deliberation-register.md` |
| Budget + execution + fiscal risk notes | credible commitments; early warning on hidden liabilities | (budget line IDs) | `07-fiscal-and-budgetary-governance.md` (anchors: [BIB-IMF-FTC-2019], [BIB-PEFA-2016]) |
| Contract register (open contracting) | anti-capture audit; competition monitoring; amendment/change-order legibility | `CON` (prefer OCID where used) | `38-contracting-and-procurement-register.md` (anchor: [BIB-OCDS]) |
| Grants/subsidies/tax expenditures register | closes “spend without contracts”; makes subsidy policy contestable | `GRT`, `TEX` | `49-grants-subsidies-and-tax-expenditures-register.md` |
| Influence & interests register | make lobbying/meetings/gifts and COI management joinable to decisions | `INF`, `INT` | `46-influence-and-interests-register.md`, `79-conflict-of-interest-and-revolving-door-discipline.md`, `22-public-integrity-and-procurement.md` |
| Transfer + compact registers | money-map and cooperation map match the competence map; conditionality is auditable and can’t hold essential services hostage | `TRF`, `CMP` | `35-transfer-register-and-conditionality.md`, `18-intergovernmental-finance.md`, `19-compacts-and-cooperative-governance.md` |
| Program Register + Evaluation Registry | policy becomes testable; revise/scale/stop decisions are auditable | `PROG`, `EVAL` | `28-program-register-and-evaluation-commitments.md` |
| Data Release Register (PDRR) | shared “official facts” with methods + revision logs; joins to decisions and claims | `REL-*` | `51-release-registry.md`, `26-epistemic-infrastructure-and-public-knowledge.md` |
| Records/FOI log + disclosure log | FOI becomes feasible; disclosure is trackable | `FOI` | `31-records-foi-and-government-memory.md` |
| Data Processing Register + ADS/MOD register | constrain digital discretion; enable appeal/audit | `DPR`, `ADS`, `MOD` | `33-data-protection-and-personal-data-governance.md`, `42-automated-decision-systems-and-model-registry.md` |
| Identity & Credential Systems Register | identity/eligibility gates become auditable; reduces exclusion-by-design and stealth surveillance | `IDN` | `44-identity-credential-and-eligibility-systems-register.md`, `12-identity-and-recognition.md` |
| Emergency Measures Register + Oversight Findings & Response Register (`55-...`) | exceptions get logged, reviewed, and closed with evidence (including continuity-floor checks when emergency authority alters `ESS-1` services) | `EMR`, `OFR` | `45-...`, `23-...`, `32-...` |

## Adoption dynamics and Phase −1 (don’t pretend politics away)

**Adoption requirement:** implementation plans MUST name the political economy: who loses discretion, who gains contestation capacity, and what incentives/coalitions make adoption stable (see `99-protective-legibility-and-adoption-dynamics.md`).

**Coalition prompts (keep tight):**
- **Internal champions:** auditors, ombuds, service delivery managers, and integrity staff who gain from clarity.
- **External pressure points:** courts, media, unions/civil society, donor/credit/trade conditions, and procurement market access requirements.
- **Demonstration wins:** start where benefits are immediately felt (high‑volume `ESS-1` services and coercive interactions) so receipts/standards create visible constituency.
- **Compliance ratchet:** design for durability (mirrors + checksum logs + person‑held receipts) so rollback is costly.
- **Hostile environments:** prioritize receipts + rules inventory + one record‑compelling front door; treat deeper stacks as direction‑of‑travel.


**Minimum political substrate (diagnostic):** the MVGS assumes *some* contestation/enforcement capacity exists (courts, auditors, ombuds, media, unions/civil society, or external monitors). Where it doesn’t, treat the stack as a direction‑of‑travel and prioritize the smallest artifacts that can survive hostile environments (Phase −1 receipts + independent record capture).

**Phase −1 (severe constraint):** where digital/capacity is absent, start with paper, numbered receipts at the highest‑coercion/highest‑harm points (detention, checkpoints, tax collection, aid distribution, benefits cutoffs) plus a public place to post rules/standards and a mobile/front‑door ombuds intake. Where multiple authorities operate, record them in the competence ledger *as they are* (descriptive, not legitimating).

**If you can only do three things (minimal loop):**
1) **Rights‑affecting receipts** (`DRR-*`, with `RULE-*` as‑of, ≥1 `RC-*`, and ≥1 `AL-*`).
2) **A public rules inventory** (`RULE-*` as‑of), so people can know what is being enforced.
3) **One independent front door with teeth** (ombuds/tribunal or equivalent) that can accept filings offline, **compel production of records**, and trigger interim protection / escalation where stakes are high (`AL-*`).

If (3) is not politically feasible yet, ship the **remedy front door** first and add compel powers as soon as feasible. Everything else can accrete around these.


## MVGS implementation profiles (start cheap; upgrade later)
The MVGS does **not** require a full data platform on day one. Minimal workable implementations:

1) **Static site + CSV/JSON** (default)
- publish registers as versioned CSV/JSON + human pages; stable IDs in filenames/rows; changelog per file.
- for core registers, add a **checksum manifest + signature** per release and at least one public mirror (see `31-...`).

2) **Spreadsheet-first** (small jurisdictions)
- one workbook per register; monthly export to a public `REL-*` bundle; keep change logs and “as-of” dates.

3) **Paper/receipt-first** (high-coercion / high-volume interactions)
- enforce person-facing receipts (`DRR` + `AL`) even before the full registry stack is online; backfill the public logs from the receipt system.

**Practical sequencing tip:** start with the **top 10 services** (`SRV-*`) and **top 10 rights-affecting decision types** (permits, benefits, enforcement actions). Expand only when the loops work.



## Phase −1 — Bootstrap under severe constraint (when institutions barely function)
When capacity, trust, or infrastructure is near‑zero, start with **the simplest person‑protecting artifacts** and publish them in whatever medium exists.

- **Receipt‑first at high coercion points:** checkpoints, detention, tax collection, aid distribution. A numbered paper receipt with date, reason, authority, and complaint contact is a minimum viable constraint.
  - Operational minimum: a **pre‑numbered carbon‑copy receipt pad** (one copy to the person, one retained) can implement `DRR` discipline without electricity; later, transcribe to `REL-*` releases.
- **Map reality before redesign:** if multiple authorities operate, record them in the competence ledger *as they are*; the ledger describes reality and makes disputes visible.
- **External verification first:** civil society monitors, community scorecards, observers—build internal capacity behind external accountability.
- **No‑electricity publishing:** bulletin boards, community radio, traveling ombuds/mobile courts, and periodic printed `REL-*` releases can carry standards, backlogs, and rules.

## Phase 0 — Map reality + ship MVGS interfaces (0–6 months)
- Stand up the **MVGS** artifacts above (start minimal; publish first versions; iterate).

- Prefer starting pilots where the person’s path is shortest and outcomes are visible: **micro-local governance** (`10-micro-local.md`) + receipt-first points of coercion (`05-...`, `31-...`).
- Add a small **publication integrity layer** for core feeds (as-of access + changelogs + checksum manifests; optional append-only log later; see `53-publication-integrity-and-tamper-evident-logs.md`) so “silent revisions” become detectable.
- Publish a first **review/sunset calendar** for major `RULE-*` and `PROG-*` items (and any `AC-*` regimes): list IDs with next review dates and name the renewal evidence standard; treat missed dates as governance incidents (`74-...`, `32-...`).
- Run at least one cross-scope **emergency drill** that exercises renewal, oversight, logs, and after-action review (AAR) (no “paper plans”).
- Inventory boundary and responsibility anomalies (overlaps, gaps, arbitrage edges) and stand up a boundary/reorganisation process (`17-jurisdiction-formation-and-boundaries.md`).
- Inventory functional authorities / special districts and pull them into consolidated reporting and the competence ledger (`15-functional-authorities.md`).
- Map the metropolitan governance surface area (compacts, MPOs, special districts) and pull it into the competence ledger + consolidated reporting (`16-metropolitan-governance.md`, `70-interoperability.md`).
- Use the scope ladder to (re)assign mandates intentionally (`14-scope-ladder.md`) and record non-trivial assignments/transfers as `DRR-TYPE: SCOPE` (see `IOP-10` in `02-design-toolkit.md`).
- Map discretion hotspots: permits, procurement, enforcement, benefits eligibility; publish queue stats + time bounds where feasible (`29-permissioning-and-approvals.md`); for benefits, define intake/recert journeys as `SRV-*` and enforce determination receipts (`DRR-*`) with discoverable `AL-*` lanes (see `64-social-protection-and-benefits-governance.md`).
- Map education and skills decision surfaces (enrollment/transfer, placement/tracking, discipline, accommodations, credentialing): define journeys as `SRV-*`, inventory binding rules in PRR, enforce `DRR-*` receipts with `RC-EDU-*` and discoverable `AL-*` lanes, and publish minimal access/learning-condition indicators as versioned `REL-*` releases (methods + revision logs). Route recurring safeguarding/exclusion failures into `OFR-*` follow-through. See `68-education-and-skills-governance.md`.
- Map administrative justice forums (internal review, tribunals, courts) and publish them as `AL-*` lanes; begin publishing binding tribunal/court decisions as `DRR-TYPE: JUDGMENT` and a versioned `REL-*` decision feed (see `66-justice-and-administrative-justice-governance.md`).
- Map migration/mobility decision surfaces (status determinations, work authorization, detention/custody, and return/removal where used): inventory gateway rules in PRR, enforce person-facing `DRR-*` receipts with `RC-MIG-*` and discoverable `AL-*` lanes, and ensure any custody events are logged as `ENF-*` joined to the authorizing `DRR-*` (publish aggregate delay/overturn/custody metrics as versioned `REL-*`). See `67-migration-and-mobility-governance.md`.
- Map labor & work decision surfaces (status/classification, wage theft, OSH hazards, retaliation/organizing where applicable): inventory governing rules in PRR, publish wage/time/safety standards as `RULE-*` + pinned `STD-*`, define complaint/inspection journeys as `SRV-*`, enforce `DRR-*` receipts with `RC-LAB-*` and discoverable `AL-*` lanes, and log inspections/citations as `ENF-*` joined to their authorizing `DRR-*` (publish small queue/coverage/recovery releases as versioned `REL-*`). See `69-labor-and-work-governance.md`.
- Map land-use and housing discretion hotspots (rezonings, variances, major permits) and publish a first plan/zoning inventory + map releases (diffable `REL-*`), with decisions emitting `DRR-*` and logged in `PAR` (see `62-land-and-housing-governance.md`).
- Map identity/registration gaps: CRVS coverage, ID issuance bottlenecks, and correction backlogs (`IOP-6`; see `12-identity-and-recognition.md`).
- Map climate/hazard risk baselines (flood/heat/fire/storm/seismic where relevant) and publish first versioned `REL-*` releases with methods + revision logs; publish the trigger rubric as `RULE-*` and ensure activations and risk-acceptance exceptions emit `DRR-*` with `RC-DRR-*` and discoverable `AL-*` lanes (see `63-climate-adaptation-and-disaster-risk-governance.md`).
- Map ecological discretion hotspots (permits, discharges, land-use conversions) and publish environmental registries (`OPEN-6`; see `11-commons-and-ecological-governance.md`).
- Inventory **enforcement-facing operational policy** (manuals, scripts, and configuration tables) that materially determines outcomes; register them in the PRR (often flagged `GLAW`) and link them to the relevant service/system entries (`39-rulebook-and-instruments-registry.md`, `47-service-catalog-and-access-journeys-register.md`, `42-automated-decision-systems-and-model-registry.md`).
- Map **algorithmic** discretion hotspots (ADS/AI in eligibility, triage, risk scoring); ensure public registers + appeal paths (`IOP-5`; see `06-digital-and-algorithmic-governance.md`).
- For new/renewed high-risk contracts (especially those operating `ESS-1` services or rights-affecting systems), require the **CLC pack** (receipt/record emission, rule traceability, audit access, portability/exit, FOI/records continuity) and publish whether it is present in the CPR (`38-...`).
- Publish an **Entity Identifier (`EID`) profile** for non-state counterparties (vendors, grantees, lobby entities) and require it for above-threshold awards; for high-risk instruments, require beneficial ownership disclosure and publish joinable statements (often as a BODS-formatted `REL-*` release) with verification status.
- Map coercive discretion hotspots (stops, arrests, detention, emergency orders) and add audit trails (`SAFE-*`; see `05-public-safety-and-coercion.md`).
- Map critical public/regulated assets (start with top 50–200) and publish a first AIR release keyed by `AST-*` (coarse locations, condition grades, backlog estimates) linked to `SRV-*` where possible (`48-asset-and-infrastructure-register.md`).
- Map service‑critical IT/OT for `ESS-1` services and publish a minimal cyber baseline (controls profile as `REL-*`, pinned standard versions where applicable, and an incident logging/follow‑through rule using `DRR-TYPE: INCIDENT` + `OFR-*`) (`59-critical-infrastructure-and-cyber-resilience-governance.md`).
- Baseline measurement set + data owners (`03-metrics-and-evidence.md`).
- Produce a first-pass **fiscal risk map** (off-budget entities, guarantees, SOEs/PPPs, tax expenditures) (`CAP-3`; see `07-fiscal-and-budgetary-governance.md`).
- **Mitigation spine (if decarbonization is in-scope):** publish emissions/energy baseline methods as `REL-*`, register binding targets as `RULE-*` citing pinned `STD-*`, and require `DRR-*` receipts for long‑lived energy asset permits and major market/tariff rule changes (see `65-energy-and-decarbonization-governance.md`).


## Phase 1 — Watchdogs before new powers (6–18 months)
- adopt MV-IGF: no unfunded mandates, predictable equalisation core, debt registry + resolution path (`18-intergovernmental-finance.md`)
- strengthen audit, ombuds, and anticorruption capacity (`ACC-1/2/3/4`)
- adopt the MVPIS + procurement integrity baseline (MVPI) and start publishing the minimal integrity metrics (`22-public-integrity-and-procurement.md`)
- implement open budgets + open contracting (`OPEN-1/2`) (see also [BIB-OGP-NHB-2025] for an action-plan scaffold)
- adopt a regulatory policy baseline (public drafts, comment logs, published responses) and start ex-post review for major rules (`CAP-7`; see `13-regulation-utilities-and-soes.md`)
- publish identity/registry governance baselines (CRVS/ID access, correction deadlines, purpose limitation) and implement high-priority fixes (`IOP-6`; see `12-identity-and-recognition.md`)
- adopt ADS governance baseline for any rights-affecting automation (register, logs, appeal) (`IOP-5`)
- create fast administrative tribunals for high-volume disputes (`LAW-3`)
- define and publish the remedy stack (front-door grievance → ombuds → tribunal → court) (`LAW-5`; see `08-remedy-and-grievance.md`)
- adopt emergency powers protocol with sunsets and after-action reporting (`SAFE-3`)
- implement a public service capability baseline (merit hiring, core skills in procurement/digital/evaluation, retention) (`CAP-6`; see `09-public-service-and-state-capacity.md`)
- publish an SOE ownership policy + consolidated disclosure of guarantees/support where applicable (`CAP-8`, `CAP-3`)

## Phase 2 — Add legitimacy channels (12–36 months)
- institutionalize citizens’ assemblies for constitutional/major plan review (`DEC-2`) and log them in the Participation & Deliberation Register (`ENG-*`) with a duty-to-respond (`IOP-17`)
- implement constitutional/charter change discipline (MVCCD) so top-tier rule changes are publishable and contestable (`DEC-9`; proposal bundles as `REL-*` + gating dockets as `DRR-TYPE: INTEGRITY`; see `58-constitutional-change-and-amendment-discipline.md`).
- expand participatory budgeting in bounded envelopes (`DEC-3`) and log cycles/results as `ENG-*` entries linked to the budget decisions
- reform representation incentives where feasible (`DEC-5`)
- adopt the Minimum Viable Legitimacy Stack (MVLS) decision-typing and routing rules (`21-legitimacy-architecture.md`)

## Phase 3 — Build compacts and interfaces (24–60 months)
- convert ad-hoc cooperation into compacts with metrics and exit clauses (`IOP-1`)
- add ecological commons compacts (watersheds/airsheds/corridors) with shared monitoring + leakage controls (`OPEN-6`; `70-interoperability.md`)
- standardize fiscal transfer formulas and public balance sheets (`CAP-2/3/5`)
- standardize data schemas for budgets/procurement/outcomes (`IOP-3`, `OPEN-2`)

## Phase 4 — Safe-to-fail experimentation (ongoing)
- pilot policy changes via bounded experimentation/sandboxes with pre-committed evaluation windows and stop conditions (`86-regulatory-experimentation-and-sandboxes.md`)
- sunset high-risk programs by default unless evidence sustains them
- publish “what we learned” memos to prevent repeating failures

## Minimal rule
If a reform increases discretion, it MUST also increase:
- transparency (`OPEN-*`),
- auditability (`ACC-*`),
- remedy (`LAW-*`),
- and sunset/review capacity (`SAFE-3` + metrics loops).
