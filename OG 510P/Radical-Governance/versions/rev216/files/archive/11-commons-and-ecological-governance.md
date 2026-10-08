# Commons & Ecological Governance (Cross-scope)

**Purpose:** make ecological limits and commons stewardship enforceable through receipts, rules, and fiscal joins (not vibes).

**Problem class:** shared resources + externalities (air, water, climate, habitats, toxins) that don’t respect jurisdictional lines.  
**Design goal:** make ecological limits *governable objects* while preserving subsidiarity and preventing capture.


**Default stance:** favor **polycentric** arrangements (many governing centers with clear interfaces) over single-command designs for complex commons; see [BIB-OSTROM-GOVCOMMONS-1990], [BIB-OSTROM-POLYCENTRIC-2010].

## Kernel anchors (do not repeat)
- Evidence discipline (MRV as a public good; methods + revision logs): `03-metrics-and-evidence.md`, `53-publication-integrity-and-tamper-evident-logs.md`.
- Cross-border and cross-scope wiring: `19-compacts-and-cooperative-governance.md`, `63-climate-adaptation-and-disaster-risk-governance.md`.
- Fiscal substrate (budgets + revenue admin + transfers): `07-fiscal-and-budgetary-governance.md`, `93-tax-and-revenue-administration.md`, `18-intergovernmental-finance.md` (ecological limits require durable funding and auditable spending).
- Permissioning + enforcement must stay contestable and person-safe: `29-permissioning-and-approvals.md`, `05-public-safety-and-coercion.md`, `08-remedy-and-grievance.md`, `98-persons-path-and-accessibility-invariants.md`.
- Protective legibility for land/resource registries (avoid weaponizable disclosure): `99-protective-legibility-and-adoption-dynamics.md`, `77-sensitive-information-and-secrecy-governance.md`.

## Named tensions (design must surface these)
- **Measurement vs surveillance:** monitoring can become policing; publish methods/aggregates and constrain use.
- **Local autonomy vs ecological limits:** subsidiarity cannot be a license to exceed shared thresholds.
- **Openness vs exploitation:** location data can enable poaching/land grabs; default to protective releases.
- **Present benefit vs future harm:** irreversible thresholds require standstill rules and reviewable exceptions.


## Ecology-specific constraints (why “normal admin design” is not enough)
- **Non-linearity & irreversibility:** many harms are thresholded (crossing them triggers discontinuous damage). Design defaults should be precautionary: publish trigger thresholds, use standstill rules for irreversible harm, and require explicit justification for risk-taking.
- **Misaligned governance units:** watersheds/airsheds/bioregions rarely match political borders → compacts + joint bodies are the default interface, not an exception.
- **Monitoring is contested and expensive:** treat measurement (MRV) as a public good: independent monitoring rights, open methods, and community/third‑party verification channels.

## When a compact partner is captured (dominant real-world failure mode)
Design compacts and ecological joint bodies so they can fail *gracefully* under partial compliance:
- independent measurement/verification (publish methods + audits; avoid partner-controlled baselines),
- conditional finance/transfer backstops (funds released against verified milestones),
- dispute clauses with escalation ladders (including to higher-scope bodies where available), and
- emergency “harm stop” provisions for irreversible thresholds (time-bounded, reviewable).
## Core primitives
1) **Ecological budgets:** define measurable ceilings (e.g., emissions, withdrawals, nutrient loads) and protection floors (ecosystem integrity).  
   - Scientific framing anchors: Planetary Boundaries (Stockholm Resilience Centre) and “safe & just Earth system boundaries” (Earth Commission).  
     References: [BIB-SRC-PLANETARY-BOUNDARIES] ; [BIB-NATURE-ESB-2023]

2) **Environmental rights + standing:** access to information, participation, and justice as a baseline.  
   - Anchors: Aarhus Convention; UNGA A/RES/76/300.
     References: see [BIB-AARHUS]; [BIB-UNGA-76300].

3) **Accounts that link ecology ↔ economy:** integrate environmental stocks/flows into official statistics and fiscal planning.  
   - Anchor: UN SEEA (Central Framework; Ecosystem Accounting).  
     References: see [BIB-SEEA-CF]; [BIB-SEEA-EA].

4) **Boundary governance units:** manage ecological systems at their natural scale (watershed/airshed/bioregion) using compacts and joint bodies.  
   - Anchor: UNECE Water Convention (transboundary waters framework).  
     Reference: see [BIB-UNECE-WATER].


## Wiring to MVGS artifacts (make ecological limits auditable)
To avoid “environmental policy as narrative,” ecological constraints MUST use the same joinable discipline as fiscal constraints.
- **Ceilings/floors are rules:** binding ecological ceilings and protection floors SHOULD be inventoried as `RULE-*` entries (with methods and “as‑of” access).
- **Allocations emit receipts:** permits, allocations, exemptions, and enforcement actions that draw down or relax a budget SHOULD emit `DRR-*` citing the relevant `RULE-*` (as‑of) and any allocation method `REL-*`.
- **Monitoring is published as releases:** the measurement streams that determine compliance (MRV, inventories, baselines) SHOULD be published as versioned `REL-*` releases with method notes and revision logs.

## Minimum viable ecological governance (MV-ECO)
**MV-ECO-1 Measurement:** open monitoring, inventories, and registries (permits, emissions, discharges, protected areas).  
**MV-ECO-2 Allocation:** publish how budgets/limits are allocated (across sectors and sub-jurisdictions) and the rules for revision.  
**MV-ECO-3 Enforcement:** independent inspection + credible sanctions; “paper rules” are treated as failure.  
**MV-ECO-4 Remedy:** fast pathways for harms (see `08-remedy-and-grievance.md`).  
**MV-ECO-5 Finance:** predictable funding for prevention/restoration and for places bearing conservation burdens; treat funding sources and fiscal commitments as joinable (`REL-*`) and tie them to `PROG-*`/`RULE-*` where relevant (`07`, `93`).

## Scope patterns (how this composes)
- **Micro-local:** stewardship groups, commons rules, community monitoring, rapid reporting; no coercive powers.  
- **Municipal:** land-use/transport and utility governance as ecological levers; local disclosure; restoration budgets (see `62-land-and-housing-governance.md` for the land-use/housing audit spine). For climate adaptation and disaster-risk governance (baselines + triggers + recovery), see `63-climate-adaptation-and-disaster-risk-governance.md`.  
- **Regional (watershed/bioregion):** cross-jurisdiction compacts for water/air/habitat corridors; joint monitoring; dispute clause.  
- **National:** national carbon/land/water strategies; environmental regulator; SEEA-based accounts; integrity protections.  
- **Supranational:** harmonize standards and leakage controls; shared funds for transitions; mutual recognition only with auditability.  
- **Global:** treaty regimes + reporting + finance + compliance for global public goods.  
  - Climate anchor: Paris Agreement. See [BIB-PARIS].  
  - Biodiversity anchor: Kunming–Montreal Global Biodiversity Framework (CBD COP15 Decision 15/4). See [BIB-CBD-GBF].

## Common failure modes → countermeasures
- **Capture by extractive interests** → full permit transparency; conflict-of-interest rules; independent science panels; rotating oversight.  
- **Leakage & jurisdiction shopping** → comparable measurement, border/transfer rules, shared enforcement in compacts.  
- **Greenwashing / paper parks** → outcome metrics (ecological condition) + independent audits + community monitoring rights.  
- **Shifting baselines (slow degradation)** → publish long-run baselines; require “no-net-loss” accounting; trigger reviews (`DEC-6`).  
- **Overcomplexity** → start with one budget + one registry + one joint body; expand only when indicators justify it.

## Person and community path (standing, safety, and usable contestation)
Ecological governance often fails not because limits are unknown, but because **those harmed cannot safely contest** the actors who profit.

**Minimum person/community-facing requirements (tight):**
- **Standing + collective filing:** environmental harms are often diffuse; remedy systems SHOULD support collective complaints and representative filing (communities, NGOs, unions), not only individual case-by-case contestation (`08`, `36`, `98`).
- **Comprehension + offline notice:** permits, exemptions, and enforcement actions that affect health, land, or livelihood SHOULD produce understandable notices/receipts and low-bandwidth/public posting options (posters/radio/community boards) keyed to `DRR-*` / `RULE-*` (`39`, `61`, `98`).
- **Safety against retaliation:** reporting channels MUST treat intimidation as a defect—support confidential reporting, protective measures, and third-party verification when polluters or local elites can retaliate (`99`, [TM-29]).
- **Protective legibility:** publish what enables accountability (methods, baselines, receipts), but do not require disclosures that create targeting risk for vulnerable reporters; use secrecy governance when necessary (`77`, `99`).
