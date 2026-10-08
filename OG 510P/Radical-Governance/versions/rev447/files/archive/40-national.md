# National Government (Nation-State)

**Purpose:** make national rights floors and high‑stakes power **contestable**: a person can trace status/benefits/enforcement decisions to law, reasons, and enforceable remedies at scale.
**Person served:** a person whose rights, status, benefits, or enforcement are shaped by national decisions who needs traceable law, reasons, and remedy at scale.

**From-below:** This makes nation‑state power publish, justify, and remedy high‑stakes decisions so you can demand accountability at the highest scope.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-07` (Indifference) by making national-level authority, standards, and remedy hooks legible across scopes (see `98-persons-path-and-accessibility-invariants.md`).

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Constitutional/rights floor:** `58-constitutional-change-and-amendment-discipline.md`, `66-justice-and-administrative-justice-governance.md`.

## Named tensions (design must surface these)
- **Uniform rights vs local variation:** consistent protections vs plural governance forms.
- **Central authority vs subsidiarity:** national coordination vs local autonomy.
- **Security vs contestability:** secrecy/defense claims vs domestic redress (`77-...`).
- **Macro-policy vs person-facing reality:** national goals vs frontline harm (`98-persons-path-and-accessibility-invariants.md`).

## Scope card (one-screen)
- **Typical scale / unit types:** nation-state (constitutional order; full-spectrum fiscal/rights authority).
- **Owns (and nothing else):** constitutional rights floors; redistribution and macro-fiscal capacity; national standards for equal protection; bounded security functions with tight controls.
- **Does not own:** routine local services except via funding/standards; global public goods absent treaty/coordination; unreviewable emergency powers.
- **MVG (minimum viable government):** constitution + courts; legislature/executive separation; integrity + procurement stack (`22`, `79`); independent audit; strong remedy/appeals (`08`, `36`).
- **Interfaces:** publish national rulebook + as-of inventories (`25`, `39`); program/eval registry (`28`); data protection standards (`33`).
- **Person-facing invariants:** where this scope issues rights/service determinations, require **comprehension-tested receipts/notices**, **no-wrong-door** routing, and **safe remedy** (incl. representation) (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`).
- **Top failure modes:** rights backsliding, politicized enforcement, corruption/capture, emergency normalization (TM-3, TM-5, TM-8).

## What the national level must own (and nothing else)
- constitutional rights and the rule-of-law backbone
- macroeconomic stabilization and national fiscal policy
- national defense and foreign affairs (with hard constraints)
- national standards for equal citizenship (anti-discrimination; due process)
- redistribution and equalization across regions where needed

## Minimum Viable Government (MVG)

**Baseline:** adopt the **MVGS** artifacts (registers + join-keys) across the state; see `80-implementation-roadmap.md`.

**National-specific minimums**
- constitutional rights + enforceable rule-of-law backbone (independent courts + constitutional review) (`LAW-1/2`).
- administrative justice at scale: publish a national Redress Registry (`ALR`) of `AL-*` lanes and ensure enforceable remedies for rights-affecting decisions (ombuds/tribunals/courts; urgent protection where high-stakes) (see `36-...`, `08-...`, `32-...`).
- contestation capacity is budgeted: legal aid, translation/interpretation, navigators, and ombuds/court staffing are treated as core governance infrastructure (equalization target where multi-level) (`09-...`, `18-...`, `99-protective-legibility-and-adoption-dynamics.md`).
- competitive elections + independent election administration with auditable tabulation and a hardened process for changing election rules (`DEC-5`).
- macro-fiscal credibility: readable national accounts + fiscal risk disclosure + (where used) an independent fiscal institution (`CAP-2/3/4`; see `07-fiscal-and-budgetary-governance.md`).
- coercive institutions under national standards + oversight (police, security, detention) (`SAFE-*`; see `05-public-safety-and-coercion.md`).
- migration & mobility governance: treat admissibility/eligibility gateways as `RULE-*` (as-of), and require `DRR-*` receipts + `AL-*` lanes for status/conditions/detention/return actions; log any custody events as `ENF-*` and publish aggregate delay/overturn metrics as `REL-*` (see `67-migration-and-mobility-governance.md`).
- redistribution + equal citizenship: predictable intergovernmental finance and equalization where multi-level (`CAP-5`; see `18-intergovernmental-finance.md`).
- social protection at scale: treat benefits eligibility and delivery as an auditable pipeline (service journeys `SRV-*`, identity/eligibility systems `IDN-*`, rules `RULE-*`, receipts `DRR-*`, lanes `AL-*`, and privacy-preserving releases `REL-*`); register any automation (`ADS-*`) and enforce contestability (see `64-social-protection-and-benefits-governance.md`).
- education and skills equity/portability: publish binding education standards and qualification requirements as pinned `STD-*`/PRR instruments; require receipted, appealable decisions for enrollment/placement/discipline/credentialing (`DRR-*` + `RC-EDU-*` + `AL-*`); and publish minimal access/learning-condition indicators as versioned `REL-*` (methods + revision logs) so unequal citizenship is detectable and correctable (see `68-education-and-skills-governance.md`).
- SOE and market-regulation discipline where the state owns operators or sets monopoly rules (`CAP-8`, `CAP-7`; see `13-regulation-utilities-and-soes.md`).
- emergency powers protocol with sunsets + review (`SAFE-3`; see `23-emergency-governance-and-exceptions.md`).
- participation with decision hooks: log consultations/deliberations for major laws, constitutional reviews, and high-salience plans in the Participation & Deliberation Register (`ENG`) with duty-to-respond (`IOP-17`; see `41-public-participation-and-deliberation-register.md`); for high‑volume online input, require a joinable **input provenance summary** (`REL-*`) and sponsor-disclosure policy per `41-...`.

## Ideal institutional stack (bounded)
### A) Bicameralism as a “people + places” compromise
- Chamber 1: proportional representation of people.
- Chamber 2: regional representation to protect federated units.
- Use joint committees for cross-cutting long-horizon issues.

### B) Integrity architecture as a first-class system
- Whole-of-government public integrity strategy (`ACC-4`) aligned with UNCAC: see [BIB-UNCAC].
- Influence transparency (lobbying and political finance disclosure) (`ACC-5`).

### C) Constitutional maintenance without permanent constitutional crisis
- Periodic constitutional review via citizens’ assembly + legislative response (`DEC-2`).
- Rule-of-law health checks using a stable checklist method (`LAW-4`).
- Long-horizon review trigger for high-impact laws/plans (Future Council/Commission) (`DEC-6`).

### D) Fiscal federalism with transparency
- Clear assignment of mandates and revenues (avoid unfunded mandates).
- Predictable transfers and equalization (formula-based) with public reporting.

## Top failure modes + countermeasures
- **Authoritarian drift / emergency normalization:** strict `SAFE-3`, court review (`LAW-2`), open reporting (`OPEN-1`).
- **Electoral rule manipulation / administrative sabotage:** independent election administration, transparent procedures, and auditable tabulation (`DEC-5`, `OPEN-1`); heightened process for election rule changes (tie to `TM-14`).
- **Capture of oversight:** budget formula protections for auditors; transparent appointments (`ACC-1/4/5`).
- **Epistemic failure:** independent statistics + information integrity + evaluation loops (`OPEN-4/5`, `03-metrics-and-evidence.md`).
- **Targeting & surveillance (personal data as power):** enforce MVDP (`LAW-8`) with a public Data Processing Register (DPR) and real rights-to-correct/contest; prevent cross-agency laundering with compacts and auditability (`TM-15`; see `33-data-protection-and-personal-data-governance.md`).

## Interfaces upward/downward
- Downward: constitutional protection of local self-organization where feasible.
- Upward: treaty compliance, mutual recognition regimes, and cross-border coordination (see `50-supranational.md`).

## Success metrics (minimal set)
Use metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- rule-of-law health: case timelines/backlog [LRR-5] + compliance with judgments/orders [LRR-6]
- integrity risk: procurement competitiveness [IPM-2] + audit closure [IPM-5] (+ disclosures/protections where feasible) [IPM-4]
- fiscal sustainability: debt + contingent/off-book exposures [IPM-9] + fiscal risk statement completeness [IPM-8] + consolidation coverage [IPM-7]
- trust + participation breadth [LRR-1] + perceived fairness [LRR-2]
