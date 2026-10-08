# Implementation Roadmap (From “Today” to “Ideal”)

This roadmap prioritizes **reversible, compounding upgrades**: build legitimacy and auditability first, then expand capability.


## Minimal Viable Governance Stack (MVGS)
Ship these **public artifacts** first. They create join-keys for legitimacy, auditability, and remedy across scopes.

| Artifact | What it makes possible | Join keys / IDs | See |
|---|---|---|---|
| Competence ledger | clarity on who decides what; prevents “hidden government” | Unit IDs | `34-competence-ledger-and-mandate-registry.md`, `70-interoperability.md` |
| Public Rules Register (PRR) | decisions cite Rule IDs + versions/as-of; enforce and appeal consistently | `RULE` | `39-rulebook-and-instruments-registry.md` |
| Decision Records / Receipts | reasons + legal basis + appeal lanes become portable across scopes (including scope assignment decisions) | `DRR` (+ linked `RULE`/`REL`/`DPR` where relevant; include `RC-*` reason codes; use `DRR-TYPE: SCOPE` for mandate transfers) | `31-records-foi-and-government-memory.md`, `08-remedy-and-grievance.md` |
| Service Catalog & Access Journeys Register | services become legible; reduces procedural denial and channel exclusion; ties delivery metrics to a defined service **and** publishes essentiality/continuity floors for stress periods | `SRV` | `47-service-catalog-and-access-journeys-register.md`, `09-public-service-and-state-capacity.md` |
| Asset & Infrastructure Register | makes capex, maintenance, and outages auditable; reduces deferred-maintenance failure and “emergency repair” corruption | `AST` | `48-asset-and-infrastructure-register.md`, `07-fiscal-and-budgetary-governance.md` |
| Enforcement & custody event register (where coercive units exist) | no dark enforcement; joinable oversight and harm reduction | `ENF` (linked to `DRR` receipts + `RULE` as-of + `AL-*`) | `43-enforcement-and-custody-event-register.md`, `05-public-safety-and-coercion.md`, `24-mutual-aid-and-serious-incident-protocol.md` |
| Redress Registry (ALR) | appeal lanes are discoverable; urgent protection is explicit; lane changes are cross-walked | `AL` / `AL-*` | `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md` |
| Participation & Deliberation Register | participation is auditable; prevents consultation-washing; links inputs → official response | `ENG` | `41-public-participation-and-deliberation-register.md` |
| Budget + execution + fiscal risk notes | credible commitments; early warning on hidden liabilities | (budget line IDs) | `07-fiscal-and-budgetary-governance.md` (anchors: [BIB-IMF-FTC-2019], [BIB-PEFA-2016]) |
| Contract register (open contracting) | anti-capture audit; competition monitoring; amendment/change-order legibility | `CON` (prefer OCID where used) | `38-contracting-and-procurement-register.md` (anchor: [BIB-OCDS]) |
| Grants/subsidies/tax expenditures register | closes “spend without contracts”; makes subsidy policy contestable | `GRT`, `TEX` | `49-grants-subsidies-and-tax-expenditures-register.md` |
| Influence & interests register | make lobbying/meetings/gifts and COI management joinable to decisions | `INF`, `INT` | `46-influence-and-interests-register.md`, `22-public-integrity-and-procurement.md` |
| Transfer + compact registers | money-map and cooperation map match the competence map; conditionality is auditable and can’t hold essential services hostage | `TRF`, `CMP` | `35-transfer-register-and-conditionality.md`, `18-intergovernmental-finance.md`, `19-compacts-and-cooperative-governance.md` |
| Program Register + Evaluation Registry | policy becomes testable; revise/scale/stop decisions are auditable | `PROG`, `EVAL` | `28-program-register-and-evaluation-commitments.md` |
| Data Release Register (PDRR) | shared “official facts” with revision logs | `REL` | `26-epistemic-infrastructure-and-public-knowledge.md` |
| Records/FOI log + disclosure log | FOI becomes feasible; disclosure is trackable | `FOI` | `31-records-foi-and-government-memory.md` |
| Data Processing Register + ADS/MOD register | constrain digital discretion; enable appeal/audit | `DPR`, `ADS`, `MOD` | `33-data-protection-and-personal-data-governance.md`, `42-automated-decision-systems-and-model-registry.md` |
| Identity & Credential Systems Register | identity/eligibility gates become auditable; reduces exclusion-by-design and stealth surveillance | `IDN` | `44-identity-credential-and-eligibility-systems-register.md`, `12-identity-and-recognition.md` |
| Emergency Measures Register + Oversight Findings Register | exceptions get logged, reviewed, and closed with evidence (including continuity-floor checks when emergency authority alters `ESS-1` services) | `EMR`, `OFR` | `45-...`, `23-...`, `32-...` |

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



## Phase 0 — Map reality + ship MVGS interfaces (0–6 months)
- Stand up the **MVGS** artifacts above (start minimal; publish first versions; iterate).
- Add a small **publication integrity layer** for core feeds (as-of access + changelogs + checksum manifests; optional append-only log later) so “silent revisions” become detectable.
- Run at least one cross-scope **emergency drill** that exercises renewal, oversight, logs, and after-action review (AAR) (no “paper plans”).
- Inventory boundary and responsibility anomalies (overlaps, gaps, arbitrage edges) and stand up a boundary/reorganisation process (`17-jurisdiction-formation-and-boundaries.md`).
- Inventory functional authorities / special districts and pull them into consolidated reporting and the competence ledger (`15-functional-authorities.md`).
- Map the metropolitan governance surface area (compacts, MPOs, special districts) and pull it into the competence ledger + consolidated reporting (`16-metropolitan-governance.md`, `70-interoperability.md`).
- Use the scope ladder to (re)assign mandates intentionally (`14-scope-ladder.md`) and record non-trivial assignments/transfers as `DRR-TYPE: SCOPE` (see `IOP-10` in `02-design-toolkit.md`).
- Map discretion hotspots: permits, procurement, enforcement, benefits eligibility; publish queue stats + time bounds where feasible (`29-permissioning-and-approvals.md`).
- Map identity/registration gaps: CRVS coverage, ID issuance bottlenecks, and correction backlogs (`IOP-6`; see `12-identity-and-recognition.md`).
- Map ecological discretion hotspots (permits, discharges, land-use conversions) and publish environmental registries (`OPEN-6`; see `11-commons-and-ecological-governance.md`).
- Inventory **enforcement-facing operational policy** (manuals, scripts, and configuration tables) that materially determines outcomes; register them in the PRR (often flagged `GLAW`) and link them to the relevant service/system entries (`39-rulebook-and-instruments-registry.md`, `47-service-catalog-and-access-journeys-register.md`, `42-automated-decision-systems-and-model-registry.md`).
- Map **algorithmic** discretion hotspots (ADS/AI in eligibility, triage, risk scoring); ensure public registers + appeal paths (`IOP-5`; see `06-digital-and-algorithmic-governance.md`).
- For new/renewed high-risk contracts (especially those operating `ESS-1` services or rights-affecting systems), require the **CLC pack** (receipt/record emission, rule traceability, audit access, portability/exit, FOI/records continuity) and publish whether it is present in the CPR (`38-...`).
- Publish an **Entity Identifier (`EID`) profile** for non-state counterparties (vendors, grantees, lobby entities) and require it for above-threshold awards; for high-risk instruments, require beneficial ownership disclosure and publish joinable statements (often as a BODS-formatted `REL-*` release) with verification status.
- Map coercive discretion hotspots (stops, arrests, detention, emergency orders) and add audit trails (`SAFE-*`; see `05-public-safety-and-coercion.md`).
- Map critical public/regulated assets (start with top 50–200) and publish a first AIR release keyed by `AST-*` (coarse locations, condition grades, backlog estimates) linked to `SRV-*` where possible (`48-asset-and-infrastructure-register.md`).
- Baseline measurement set + data owners (`03-metrics-and-evidence.md`).
- Produce a first-pass **fiscal risk map** (off-budget entities, guarantees, SOEs/PPPs, tax expenditures) (`CAP-3`; see `07-fiscal-and-budgetary-governance.md`).

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
- expand participatory budgeting in bounded envelopes (`DEC-3`) and log cycles/results as `ENG-*` entries linked to the budget decisions
- reform representation incentives where feasible (`DEC-5`)
- adopt the Minimum Viable Legitimacy Stack (MVLS) decision-typing and routing rules (`21-legitimacy-architecture.md`)

## Phase 3 — Build compacts and interfaces (24–60 months)
- convert ad-hoc cooperation into compacts with metrics and exit clauses (`IOP-1`)
- add ecological commons compacts (watersheds/airsheds/corridors) with shared monitoring + leakage controls (`OPEN-6`; `70-interoperability.md`)
- standardize fiscal transfer formulas and public balance sheets (`CAP-2/3/5`)
- standardize data schemas for budgets/procurement/outcomes (`IOP-3`, `OPEN-2`)

## Phase 4 — Safe-to-fail experimentation (ongoing)
- pilot policy changes with pre-committed evaluation windows and stop conditions
- sunset high-risk programs by default unless evidence sustains them
- publish “what we learned” memos to prevent repeating failures

## Minimal rule
If a reform increases discretion, it MUST also increase:
- transparency (`OPEN-*`),
- auditability (`ACC-*`),
- remedy (`LAW-*`),
- and sunset/review capacity (`SAFE-3` + metrics loops).