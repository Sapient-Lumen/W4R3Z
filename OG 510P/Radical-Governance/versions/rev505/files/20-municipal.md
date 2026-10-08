# Municipal Government (City / Town)

**Cross-stack note:** use `306-scope-design-ideal-government-and-reference-bundles-guide.md` for the canonical route across the scope-design family. This memo is the municipal specialization; `14` / `176` explain the cross-scope logic, `285` gives the default bundle language, `327` gives the scale-sensitive institutional-form default, `328` gives the scale-sensitive legitimacy-channel default, `329` gives the scale-sensitive tempo / time-horizon default, and `330` gives the scale-sensitive epistemic / evidence-mode default, `331` gives the scale-sensitive accountability / review-mode default, `332` gives the scale-sensitive coercion / direct-force-holding default, and `333` gives the scale-sensitive finance / revenue-model default.


**Purpose:** make municipal power **usable from below**: a resident can receive a receipt, understand the rule basis, and reach a safe remedy path for local services, permits, and enforcement.
**Person served:** a city/town resident encountering local services, rules, and enforcement who needs a short, usable path to receipt → reason → remedy at the municipal front door.

**From-below:** This translates city power into concrete interfaces—what must be published and how to appeal—so local discretion can’t quietly trap you.

**EXP pointer:** counters `EXP-01` (Opacity), `EXP-06` (Complexity), and `EXP-02` (Waiting) at the municipal front door (see `98-persons-path-and-accessibility-invariants.md`).

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Minimum service guarantees:** `82-service-standards-and-minimum-service-guarantees.md`.

## Named tensions (design must surface these)
- **Proximity vs capture:** local responsiveness vs local elite domination.
- **Tailoring vs arbitrariness:** context sensitivity vs unequal treatment.
- **Participation vs exhaustion:** engagement as legitimacy vs burnout/exclusion.
- **Promises vs revenue:** local mandates vs fiscal reality (`07-...`, `18-...`).

## Scope card (one-screen)
- **Typical scale / unit types:** ~10,000–10,000,000 residents (city/town; municipal corporations).
- **Owns (and nothing else):** local services + land use; local infrastructure; local public health functions; regulated local safety with strong remedy.
- **Does not own:** macro stabilization, national security/foreign affairs, or cross-regional externalities without compacts (`19-...`).
- **MVG (minimum viable government):** elected council + accountable executive; professional administration; budget + procurement discipline (`07`, `22`); ombuds/admin tribunal (`08`).
- **Interfaces:** publish service catalog (`47-...`), rule inventory (`25-...`), spending/program registers (`28`, `40`); interoperable IDs (`70/71`).
- **Person-facing invariants:** where this scope issues rights/service determinations, require **comprehension-tested receipts/notices**, **no-wrong-door** routing, and **safe remedy** (incl. representation) (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`).
- **Top failure modes:** patronage, zoning capture, uneven distribution, vendor lock-in (TM-1, TM-2, TM-5, TM-6).

## What this level must own (and nothing else)
- local infrastructure: streets, water, sanitation, public spaces
- land-use, housing, permitting
- local public health operations
- primary safety services (with strict coercion controls)
- local economic regulation/enforcement where devolved

## Minimum Viable Government (MVG)

**Baseline:** adopt the **Minimal Viable Governance Stack (MVGS)** artifacts (registers + join-keys) and interfaces; see `80-implementation-roadmap.md`.

**Municipal-specific minimums**
- land-use + permitting discipline: publish zoning/bylaw Rule IDs; publish authoritative plan/zoning text/maps as diffable `REL-*`; log variances/permits in the Permit/Approval Register (`PAR`) with reasons + appeal lane (`LAW-7`; `29-permissioning-and-approvals.md`; see also `62-land-and-housing-governance.md`).
- anti-displacement rail: maintain (or partner with) at least one **land/commons stewardship** mechanism (e.g., CLT/land bank/shared-equity) with joinable asset + allocation records and remedy lanes (see `150-land-commons-stewardship-anti-speculation.md`).
- redress legibility: maintain a public Redress Registry (`ALR`) of `AL-*` lanes and require Decision Receipts (`DRR`) for enforceable actions (see `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md`).
- service standards: publish a small service charter set + queue metrics for high-volume services (`CAD-1/2`; see `03-metrics-and-evidence.md`).
- local revenue + transfers: readable budget + quarterly execution; if multi-level, predictable formula transfers and “no unfunded mandates” (`CAP-2/5`; see `18-intergovernmental-finance.md`).
- safety operations: coercion constraints + independent serious-incident pathway + public reporting (`SAFE-*`; see `05-public-safety-and-coercion.md`; `24-mutual-aid-and-serious-incident-protocol.md`).
- neighborhood interface: charter/recognize micro-local councils where used; give them bounded budgets + remedy access (`10-micro-local.md`).
- participation legibility: log major consultations, PB cycles, and citizens' assemblies as `ENG-*` entries (decision hook + duty-to-respond) and link the official response as a `DRR` (`IOP-17`; see `41-...`); for high‑volume online input, publish a joinable **input provenance summary** (`REL-*`) so manipulation/deduping is contestable.
- automated decisions used in permits/benefits: list systems in the ADS register and guarantee human review + appeal (`IOP-5`; see `06-digital-and-algorithmic-governance.md`; `08-remedy-and-grievance.md`).
- benefits delivery (where local): define intake/recert journeys as `SRV-*`; determinations/suspensions emit `DRR-*` with discoverable `AL-*` lanes; publish backlog and (program-level) payment timeliness as `REL-*` where lawful (see `64-social-protection-and-benefits-governance.md`).
- education delivery (where municipal): define enrollment/transfer and support journeys as `SRV-*`; publish placement/discipline rules as `RULE-*`; require `DRR-*` receipts for denials/placements/discipline/credentials with discoverable `AL-*` lanes; publish minimal access/condition indicators as `REL-*` and route safeguarding failures into `OFR-*` (see `68-education-and-skills-governance.md`).

## Ideal institutional stack (template)
### A) Council + professional executive (council-manager)
- Council sets policy and budgets; manager runs operations with performance review.
- Reduces personality-cult risk while preserving democratic control (`CAP-1`).

### B) Representation that discourages zero-sum politics
- Prefer multi-member districts with proportional allocation where feasible (`DEC-5`).
- Add a standing Citizens’ Assembly for major plans (zoning, policing, climate) with duty-to-respond (`DEC-2`); log each cycle as an `ENG-*` process with a linked response `DRR`.
- Require “future impact statements” for 10–30 year plans (housing, infrastructure, climate) and empower review triggers (`DEC-6`).

See `21-legitimacy-architecture.md` for decision-typing and composition patterns (elected + deliberative + rights + remedy).

### C) Service charters + measurable guarantees
- Publish service baselines (permit timelines, maintenance cycles, response targets) and maintain a public Permit/Approval Register (PAR) for permits/variances (`LAW-7`; see `29-permissioning-and-approvals.md`).
- Use ombuds + tribunal pathways for fast remedies (`ACC-3`, `LAW-3`).

### D) Transparent budgets + procurement
- Proactive publication of contracts, budgets, and outcomes (`OPEN-1`).
- Use OCDS-style contracting disclosure (`OPEN-2`): see [BIB-OCDS].

## Safety & coercion controls (municipal-specific)
- Separate response functions:
 - unarmed crisis teams for behavioral health and social crises,
 - civil enforcement where possible without weapons,
 - armed response narrowly scoped to imminent violence.
- Oversight board publishes force, stops, complaints, and discipline outcomes (`SAFE-1/2`).

## Top failure modes + countermeasures
- **Zoning capture:** conflict disclosures + transparent variances + audit trail, with variance/permit decisions logged in PAR and reasons tied to criteria (`ACC-4`, `OPEN-1`, `LAW-7`).
- **Procurement fraud:** open contracting + independent audit closure (`OPEN-2`, `ACC-1/2`; see `22-public-integrity-and-procurement.md`).
- **Legitimacy collapse:** institutionalize deliberation + PB in bounded budgets (`DEC-2/3`).

## Interfaces downward and upward
- Downward: fund and legally recognize neighborhood councils (`10-micro-local.md`).
- Upward: join regional compacts for transit, watersheds, housing targets, and disaster response (`IOP-1`).
- Boundary / structure changes (annexation, merger, splits, responsibility transfers): use the MV-BRP tests and process (`17-jurisdiction-formation-and-boundaries.md`).

## Success metrics (minimal set)
Use metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- service reliability (water, sanitation, transit) [CAD-1]
- housing affordability (local add-on) + permit cycle time (median + 90p) [LRR-4]
- procurement competitiveness (single-bid share) [IPM-2] + vendor concentration [IPM-3]
- safety outcomes (serious harm rate) [SAC-6] + coercion incidents [SAC-1]
