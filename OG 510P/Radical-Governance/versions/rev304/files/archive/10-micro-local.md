# Micro-Local Government (Building / Block / Neighborhood)

**Purpose:** show how to start where governance is closest to people, enabling fast, visible accountability wins with minimal infrastructure.

**Person served:** the neighbor or tenant or parent in a small jurisdiction who needs low‑cost ways to contest, coordinate, and prevent capture without needing professional advocates.

**From-below:** This helps you and your neighbors win fast, visible accountability—clear roles, clear receipts, and follow‑through—without needing expensive bureaucracy.

**EXP pointer:** EXP-08 (Invisibility), EXP-05 (Fear), EXP-06 (Complexity) — small-scale power failures (see `98-persons-path-and-accessibility-invariants.md`).

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.

At this scale, the archive’s “interfaces” can be **human‑scale**: the person at the counter may be a neighbor, and the shortest path to remedy may be a meeting.

**Start-here reminder:** don’t let the larger-scale machinery overshadow this. Micro‑local governance is where the person’s path is shortest and where legitimacy can be rebuilt through visible follow‑through. (See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04, NR-17).)

**Hope (not optimism):** this scope is where legitimacy is rebuilt through practiced mutual responsibility—visible follow‑through, shared memory of decisions, and community capacity that can carry people through system failure.
  
This memo explicitly allows **functional equivalents** to the archive’s written/registry posture:
- **Oral / consensus governance** can satisfy the spirit of receipts and reasons if outcomes are *remembered in common* (minutes/posters) and escalation paths are clear.
- **Customary / relational / restorative practices** can be compatible when they still provide (a) a stable, community-legible account of what was decided and why, (b) a safe way to object without retaliation, and (c) a path to correction/repair. Treat “registry” as an implementation choice, not a cultural mandate. (See `101-claude-rev142-normative-requirements.md` (NR-17, NR-08, NR-02).)
- A “receipt” here may be a numbered slip, a posted decision log, or meeting minutes—so long as it is **portable enough** for someone to contest upward when needed (`98-persons-path-and-accessibility-invariants.md`, `71-...`).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Person-facing path + accessibility floors (including offline and assisted routes): `98-persons-path-and-accessibility-invariants.md`.
- Receipts + records (so micro-decisions remain portable upward): `31-records-foi-and-government-memory.md`.
- Remedy and escalation lanes (so “local” cannot become a trap): `08-remedy-and-grievance.md` + `36-appeal-lanes-and-redress-registry.md`.
- Participation and duty-to-respond discipline: `41-public-participation-and-deliberation-register.md` (and `88-deliberative-institutions-and-sortition.md` where used).
- Mutual aid and serious-incident independence (when crises hit): `24-mutual-aid-and-serious-incident-protocol.md`.

## Named tensions (design must surface these)
- Informality and trust vs durable accountability (oral practices still need portable memory).
- Local autonomy vs exclusion/capture (cliques, HOA/property power, factional coercion).
- Speed and neighborly repair vs due process and rights protection (especially for disputes).
- Local “resolution” vs retaliation/fear (people need safe escalation options).

## Scope card (one-screen)
- **Typical scale / unit types:** ~200–20,000 residents (building/block/neighborhood; commons councils; resident associations).
- **Owns (and nothing else):** hyper-local commons and shared spaces; micro-budgets/maintenance; mutual aid and serious-incident coordination (`24-...`).
- **Does not own:** detention/custody, armed force, or high-discretion enforcement; major land-use zoning beyond micro-allocations; cross-neighborhood externalities.
- **MVG (minimum viable government):** transparent charter; open meetings + minimal PB; simple dispute pathway + referrals (`08-...`); basic records/receipts (`31-...`).
- **Low‑literacy / low‑trust access:** postings and plain speech (bulletin boards / radio / interpreters), plus a navigator/ombuds intake (see `98-persons-path-and-accessibility-invariants.md` and `82-...`).
- **Interfaces:** publish micro-decisions and `SRV-*` touchpoints; clear escalation lanes to municipal (`71-...`).
- **Top failure modes:** exclusion/factionalism; informal coercion; capture by property/HOA power (TM-1, TM-5, TM-11).

## What this level must own (and nothing else)
- no coercive authority (safety roles are non-coercive and interface to municipal services)
- shared spaces and micro-infrastructure stewardship
- hyperlocal conflict prevention (non-police first response where possible)
- mutual aid / care coordination (especially during crises)
- localized externalities (noise, litter, micro-traffic)
- allocation of small, bounded community grants

## Minimum Viable Government (MVG)
- a **recognized charter** from the municipality (clear powers + rights constraints)
- a **bounded budget envelope** (per-capita or formula-based) with public reporting (`CAP-2`, `OPEN-1`)
- a **commons stewardship loop** (monitor → report → fix) for local ecological harms (`OPEN-6`; see `11-commons-and-ecological-governance.md`)
- a **decision channel** with mixed legitimacy (elected + sortition seats) (`DEC-1`, `DEC-2`; composition patterns: `21-legitimacy-architecture.md`)
- a **remedy channel** for administrative unfairness (ombuds or municipal ombuds access) (`ACC-3`)
- a **non-carceral dispute pathway** (mediation/restorative options with escalation) (`LAW-3`-style tribunal access)

## Ideal institutional stack
### A) Neighborhood Commons Council (NCC)
- **Selection:** mixed model:
  - 50–70% elected by neighborhood blocks/districts (`DEC-1`)
  - 30–50% sortition seats (rotating, compensated) (`DEC-2`)
- **Powers:** manage local commons; allocate the neighborhood budget; propose bylaws within municipal charter constraints.
- **Transparency:** public minutes; simple budgets; open agenda pipeline (`OPEN-1`).

### B) Micro-budget + participatory budgeting
- Municipal government MUST allocate a per-capita “neighborhood commons” budget line.
- NCC runs participatory budgeting for small capital, maintenance, and resilience projects (`DEC-3`).
- Each PB cycle SHOULD be logged as an `ENG-*` entry (Participation & Deliberation Register) linked to the authorizing and allocation `DRR` (prevents “PB theatre”; see `41-...`).

### C) Dispute resolution first
- Mediation/restorative options are default for interpersonal conflicts.
- Escalation exists for rights violations, violence, or persistent harm (interface to municipal enforcement and tribunals).

### D) Stewardship & monitoring
- Paid part-time stewards coordinate maintenance, convening, and basic reporting.
- Rules mirror commons best practice (boundaries, participatory rule-making, monitoring, graduated sanctions).  
  Reference: Ostrom design principles (overview): see [BIB-STERN-2011-IJC-305].

## Top failure modes + countermeasures
- **Capture / clique rule:** add sortition seats; rotate stewards; publish conflicts (`DEC-2`, `ACC-4`).
- **Exclusion / discrimination:** charter-level protections + complaint channel (`LAW-1` via municipal charter, `ACC-3`).
- **Informal coercion:** clear escalation, external oversight, and anti-retaliation norms (`SAFE-2` interface upward).

## Interfaces upward
- guaranteed channel to municipal committees (agenda items + testimony)
- standing to challenge municipal actions that violate the neighborhood charter or subsidiarity
- crisis protocol: mutual aid coordination plugs into municipal emergency ops

## Success metrics (minimal set)
Use metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- issue resolution time (median + 90p) [LRR-4]
- participation breadth (demographic reach) [LRR-1]
- commons maintenance uptime / outage duration [CAD-1]
- perceived safety + conflict recurrence [SAC-7]