# Regional Government (Metropolitan / Watershed / State- or Province-like)

**Cross-stack note:** use `306-scope-design-ideal-government-and-reference-bundles-guide.md` for the canonical route across the scope-design family. This memo is the regional / state-province specialization; `14` / `176` explain the cross-scope logic, `285` gives the default bundle language, `327` gives the scale-sensitive institutional-form default, `328` gives the scale-sensitive legitimacy-channel default, `329` gives the scale-sensitive tempo / time-horizon default, and `330` gives the scale-sensitive epistemic / evidence-mode default, `331` gives the scale-sensitive accountability / review-mode default, `332` gives the scale-sensitive coercion / direct-force-holding default, and `333` gives the scale-sensitive finance / revenue-model default.


**Purpose:** make cross‑jurisdiction governance **not a black hole**: a resident can trace regional decisions (corridors, equalization, basin systems) to rules/compacts and reach a remedy lane when responsibilities overlap.
**Person served:** someone whose problem is regional (watershed, transit, housing market, labor shed) who needs regional bodies to be legible, bounded, and contestable.

**From-below:** This helps you hold mid‑scale government to account so services that span towns still have clear owners, receipts, and remedies.

**EXP pointer:** counters `EXP-06` (Complexity) and `EXP-01` (Opacity) by making regional authorities and cross-jurisdiction interfaces routable and visible (see `98-persons-path-and-accessibility-invariants.md`).

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Cross-jurisdiction interfaces:** `19-compacts-and-cooperative-governance.md`, `70-interoperability.md`.

## Named tensions (design must surface these)
- **Coordination vs accountability diffusion:** region-wide planning vs nobody responsible.
- **Technical optimization vs lived legitimacy:** expert plans vs local consent.
- **Regional equity vs veto power:** redistribution vs local blockades.
- **Speed vs contestation:** infrastructure urgency vs time-bounded review.

## Scope card (one-screen)
- **Typical scale / unit types:** multi-municipal region/province/state/land (varies widely; designed for spillovers and scale).
- **Owns (and nothing else):** inter-municipal equalization; corridor/watershed transport + land systems; regional healthcare/education capacity planning; standards where local fragmentation fails.
- **Does not own:** hyper-local service delivery and zoning details; foreign policy/war; monetary policy (unless explicitly constitutional).
- **MVG (minimum viable government):** dual legitimacy for people+places; equalization formula (`18-...`); regional oversight/audit; admin court/remedy lanes.
- **Interfaces:** publish transfers and equalization logic (`18`); multi-jurisdiction compacts (`19`); regional standards + exceptions logs (`85`).
- **Person-facing invariants:** where this scope issues rights/service determinations, require **comprehension-tested receipts/notices**, **no-wrong-door** routing, and **safe remedy** (incl. representation) (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`).
- **Top failure modes:** center-periphery domination, cartelization of metros, jurisdiction-shopping, politicized transfers (TM-2, TM-3, TM-8).

## What this level must own (and nothing else)

**Metro overlay:** for the “city-region” arrangement choice (compacts vs metro authorities vs two-tier), see `16-metropolitan-governance.md`.
- regional transportation networks and corridors
- watershed/ecosystem management at basin scale
- disaster preparedness and mutual aid coordination
- standards-setting where constitutionally assigned (education/health)
- equalization to prevent “postcode lotteries”

## Minimum Viable Government (MVG)

**Baseline:** adopt the **MVGS** artifacts (competence ledger, PRR, public accounts + audit, compacts register, Release IDs, DRR decision receipts, etc.); see `80-implementation-roadmap.md`.

**Regional-specific minimums**
- cross-municipal externalities: compacts for corridors, utilities, and shared services with clear dispute/exit clauses (`IOP-1`; see `19-compacts-and-cooperative-governance.md`).
- mutual aid + surge capacity across members, with logged activations and independent serious-incident pathways (`SAFE-5`; `24-mutual-aid-and-serious-incident-protocol.md`).
- watershed/airshed governance: basin-scale ecological budgets + shared monitoring + leakage controls (`OPEN-6`; see `11-commons-and-ecological-governance.md`; pattern pack: `170-watershed-and-water-governance-compacts.md`).
- interjurisdictional portability where relevant (credentials/benefits/document recognition) with privacy + remedy baselines (`IOP-6`; see `12-identity-and-recognition.md`).
- no‑wrong‑door across member jurisdictions for major services: people should not need to know which unit is responsible to file, appeal, or get assistance; publish a crosswalk + routing intake (`47-...`, `36-...`, `98-persons-path-and-accessibility-invariants.md`).
- megaproject governance: open contracting + independent audit + red-team review for high-capex corridor projects (`OPEN-2`, `ACC-1`).
- participation with decision hooks: log major corridor/basin plans and tariff hearings in the Participation & Deliberation Register (`ENG`) with duty-to-respond and published evidence packs (`IOP-17`; see `41-public-participation-and-deliberation-register.md`).

## Ideal institutional stack
### A) Assembly with dual legitimacy
- **Chamber 1 (people):** proportional representation by population.
- **Chamber 2 (places):** representation for municipalities/counties to protect smaller communities.
- Joint committees for transport + housing + climate plans.

### B) Compacts as first-class law
- Municipalities form binding compacts with:
 - funding formulas,
 - joint authorities (transit, water),
 - performance targets,
 - dispute clauses and exit conditions.
- Compacts MUST be published and auditable (`IOP-1`, `OPEN-1`).

### C) Planning authority with constraints
- Professional planning agency produces 10–30 year plans and risk maps.
- Assembly approval requires transparent assumptions, independent review, and periodic update cycles.
- Add long-horizon review triggers for corridor and basin-scale decisions (`DEC-6`).

### D) Regional equalization
- Formula-based transfers for education opportunity, public health capacity, and disaster resilience (`CAP-2`).

## Top failure modes + countermeasures
- **Boundary failure:** competence ledger + compact discipline (`70-interoperability.md`, `IOP-1`).
- **Megaproject capture:** open contracting + audit + red-team review (`OPEN-2`, `ACC-1`).
- **Administrative overload:** simplify mandates; publish service standards; tribunal pathways (`CAP-1/2`, `LAW-3`).

## Interfaces upward
Regional is often the correct scope for:
- climate adaptation at basin scale,
- infrastructure corridors,
- surge capacity for public health and disasters.

Boundary and responsibility realignment (creating/merging/splitting regions; transferring functions across levels) MUST follow the tests and MV-BRP process in `17-jurisdiction-formation-and-boundaries.md`.

## Success metrics (minimal set)
Use metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- commute reliability [CAD-1] + modal share (local add-on)
- watershed/ecosystem trajectory vs targets (e.g., water quality budgets) [ECO-2]
- disaster response time / queue times [CAD-2] + mutual aid activations logged [SAC-5]
- inequality of service access across municipalities [CAD-3]
