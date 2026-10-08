# Municipal Government (City / Town)

See `14-scope-ladder.md` for the cross-scope map (what belongs where) and the common “kernel” each scope should carry.

**Typical scale:** ~10,000–10,000,000 residents  
**Primary advantage:** service delivery + land-use authority + public infrastructure  
**Primary risk:** patronage, zoning capture, uneven service distribution (TM-1, TM-2, TM-5, TM-6)

## What this level must own (and nothing else)
- local infrastructure: streets, water, sanitation, public spaces
- land-use, housing, permitting
- local public health operations
- primary safety services (with strict coercion controls)
- local economic regulation/enforcement where devolved

## Minimum Viable Government (MVG)

**Baseline:** adopt the **Minimal Viable Governance Stack (MVGS)** artifacts (registers + join-keys) and interfaces; see `80-implementation-roadmap.md`.

**Municipal-specific minimums**
- land-use + permitting discipline: publish zoning/bylaw Rule IDs; log variances/permits in the Permit/Approval Register (`PAR`) with reasons + appeal lane (`LAW-7`; `29-permissioning-and-approvals.md`).
- redress legibility: maintain a public Redress Registry (`ALR`) of `AL-*` lanes and require Decision Receipts (`DRR`) for enforceable actions (see `36-appeal-lanes-and-redress-registry.md`, `08-remedy-and-grievance.md`).
- service standards: publish a small service charter set + queue metrics for high-volume services (`CAD-1/2`; see `03-metrics-and-evidence.md`).
- local revenue + transfers: readable budget + quarterly execution; if multi-level, predictable formula transfers and “no unfunded mandates” (`CAP-2/5`; see `18-intergovernmental-finance.md`).
- safety operations: coercion constraints + independent serious-incident pathway + public reporting (`SAFE-*`; see `05-public-safety-and-coercion.md`; `24-mutual-aid-and-serious-incident-protocol.md`).
- neighborhood interface: charter/recognize micro-local councils where used; give them bounded budgets + remedy access (`10-micro-local.md`).
- participation legibility: log major consultations, PB cycles, and citizens' assemblies as `ENG-*` entries (decision hook + duty-to-respond) and link the official response as a `DRR` (`IOP-17`; see `41-...`); for high‑volume online input, publish a joinable **input provenance summary** (`REL-*`) so manipulation/deduping is contestable.
- automated decisions used in permits/benefits: list systems in the ADS register and guarantee human review + appeal (`IOP-5`; see `06-digital-and-algorithmic-governance.md`; `08-remedy-and-grievance.md`).

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