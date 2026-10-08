# Scope Ladder (Ideal Government by Scale)

**Purpose:** define how responsibilities are assigned across scopes so people know who owes what and where to contest.

This memo answers: **what an “ideal government” looks like at each scope**, from micro-local to global, *without* turning into a new manifesto.

**Design rule:** assign powers to the *lowest* level that can competently handle the problem (subsidiarity), escalating only for spillovers, scale economies, rights protection, or coordination failure. Make the “why” contestable via a scope-test docket on `DRR-TYPE: SCOPE` (see `54-subsidiarity-and-scope-assignment-test.md`, `01-principles.md`, `70-interoperability.md`, `71-interface-obligations-by-scope.md`).


**Terminology (keep it clean):**
- **MVGS** (Minimal Viable Governance Stack) = cross-scope public artifacts (registers + join-keys) that make authority, money, rules, and remedy *joinable*; see `80-implementation-roadmap.md`.
- **MVG** (Minimum Viable Government) = the per-scope minimum institutions that must exist for basic legitimacy + capability (this memo’s cards + the scope memos).

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Scope assignment tests:** `54-subsidiarity-and-scope-assignment-test.md`.

## Named tensions (design must surface these)
- **Subsidiarity vs equal-rights floor:** local autonomy vs consistent protections.
- **Scale efficiency vs legitimacy:** centralized optimization vs local voice/exit.
- **Uniform interfaces vs plural forms:** joinable systems vs culturally legitimate equivalents.
- **Boundary clarity vs lived reality:** neat tiers vs overlapping authorities (`34-...`).

## Jump map (if you’re reading for “ideal government by scope”)
- Overview: this memo
- Micro-local: `10-micro-local.md`
- Municipal: `20-municipal.md`
- Intermediate local administration (county/prefecture pattern): `87-intermediate-local-administration.md`
- Metro + overlays: `16-metropolitan-governance.md`, `15-functional-authorities.md`, `19-compacts-and-cooperative-governance.md`
- Regional: `30-regional.md`
- National: `40-national.md`
- Supranational: `50-supranational.md`
- Global: `60-global.md`

**Template:** every scope SHOULD have the same minimal “stack”, tuned for the problems it owns:
- **Legitimacy:** elections (`DEC-1`) plus deliberative/sortition capacity for high-salience or long-horizon issues (`DEC-2`, `DEC-6`). See composition patterns in `21-legitimacy-architecture.md`; operational design in `88-deliberative-institutions-and-sortition.md` and register discipline in `41-public-participation-and-deliberation-register.md`.
- **Rule-of-law + remedy:** fast, accessible review and enforceable fixes (`LAW-3`, `LAW-5`).
- **Integrity + accountability:** audit/ombuds/influence transparency as the anti-capture core (`ACC-*`), with follow-through tracking (`ACC-6`; see `32-oversight-institutions-and-follow-through.md`).
- **Capability:** professional administration and readable public accounts (`CAP-1`, `CAP-2`).
- **Fiscal interface:** money matches mandates; predictable transfers/equalisation where multi-level (`CAP-5`; see `18-intergovernmental-finance.md`).
- **Transparency:** budgets/contracts/outcomes open by default (`OPEN-1/2`).
- **Participation:** participation is auditable and decision-linked via the Participation & Deliberation Register (`ENG`) with duty-to-respond triggers (`IOP-17`; see `41-public-participation-and-deliberation-register.md`).
- **Records + access:** capture decisions and official communications; retention schedule; FOI request log + disclosure log (`OPEN-9`; see `31-records-foi-and-government-memory.md`).
- **Personal data protection:** processing is listed with `DPR-*` IDs; minimization + retention; enforceable access/correction (`LAW-8`; see `33-data-protection-and-personal-data-governance.md`).
- **Epistemic infrastructure:** publish core facts with methods + revision logs; protect stats/evaluation independence (`OPEN-4/5`; see `26-epistemic-infrastructure-and-public-knowledge.md`).
- **Policy learning:** a public program register + evaluation commitments so major policy changes are testable (`OPEN-8`; see `28-program-register-and-evaluation-commitments.md`).
- **Standards legibility:** governance-grade technical standards (protocols/schemas/tests) are registered, pinned, and publicly accessible (`IOP-8`; see `27-standards-and-technical-governance.md`).
- **Register discipline:** public registers use stable IDs and change logs (no silent revisions) (`IOP-9`; see `34-competence-ledger-and-mandate-registry.md` and `70-interoperability.md`, `71-interface-obligations-by-scope.md`).
- **Interfaces:** competence ledger + escalation + compacts + portability (`IOP-*`; see `70-interoperability.md`, `71-interface-obligations-by-scope.md`).

## Scope card schema (keep each scope memo one-screen skimmable)

To prevent scope memos from drifting into manifestos, each scope memo SHOULD begin with a one-screen “card” that answers:

- **Typical scale / unit types:** (population + common institutional analogs)
- **Owns (and nothing else):** the problem classes this scope must own (spillovers, rights floors, scale economies)
- **Does not own:** explicit non-ownership boundaries (what must remain below/above)
- **MVG (minimum viable government):** the minimum legitimacy + remedy + capacity stack for this scope
- **Interfaces:** what it must publish upward/downward (join-keys and obligations; see `70/71`)
- **Person’s path:** list the top person‑facing determinations at this scope and confirm the interface works for the least‑resourced person (comprehension‑tested receipts/notices, no‑wrong‑door routing, safe remedy/representation, offline channel) (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `47-...`).
- **Protective legibility + capacity:** name the enforcement/countervailing‑power preconditions and whether they are funded/real at this scope (do not treat transparency as sufficient) (`99-protective-legibility-and-adoption-dynamics.md`, `18-...`, `32-...`).

- **Top failure modes:** 3–6 with the smallest countermeasure each (choose `TM-*`)
- **Success metrics:** ≤10 (choose from `03-metrics-and-evidence.md`)
- **Anchor citations:** ≤5 stable `[BIB-*]` keys (no long quotes)

(Use `95-template-design-memo.md` when writing new designs; treat scope cards as the “front matter” for scope memos.)

## Non-negotiable public artifacts (across all scopes)

A scope cannot be “ideal” if people can’t *see* authority, money, rules, and remedy. Every scope MUST be able to publish (even in minimal form):

- **Unit/competence legibility:** a competence-ledger entry (Unit ID) that names the unit, its mandate, funding responsibility, and remedy path.
- **Rules legibility:** enforceable norms have stable `RULE` IDs and versions/as-of (PRR).
- **Decision legibility:** enforceable actions issue a `DRR` (reasons + rule/evidence joins + appeal lane).
- **Remedy legibility:** an `ALR` makes appeal/grievance lanes discoverable, with explicit escalation across scopes.
- **Money legibility:** any public funds flow through published accounts (budget + execution) as joinable `REL-*` releases.
- **Participation + memory:** major participation/deliberation processes are logged (`ENG-*`) and decisions are recorded/retained (records/FOI baseline).

If a scope can’t meet these, reduce its discretion (treat it as advisory) until it can.

> “Ideal” here means: maximizes legitimacy, capability, adaptability, and harm-limiting under realistic human constraints.


**In-between rule:** when something needs scale but not a full general-purpose government, prefer a **functional authority** (special district) with a narrow charter, strong auditability, and explicit interfaces. See `15-functional-authorities.md` and `16-metropolitan-governance.md`.
**Formation rule:** creating/merging/splitting jurisdictions is a **high-leverage** change; require an independent boundary/reorganisation process, transition plan, and ledger versioning. See `17-jurisdiction-formation-and-boundaries.md`.


## Non-territorial polities (membership-based governance)

Not all “scopes” are territorial tiers. **Indigenous nations**, **diaspora institutions**, **professional bodies**, **platform communities**, **co-ops/unions**, and some **religious or clan systems** exercise real authority by *membership*.

**Design translation:** treat them as a jurisdictional unit in the competence ledger (Unit ID + mandate + coercion ceiling), then force the same joinability:
- publish their enforceable norms as `RULE-*` (or cite external law IDs) and rights-affecting decisions as `DRR-*`;
- expose a remedy lane (`AL-*`) that includes an *exit/portability* option where feasible;
- disclose money flows and cross-government transfers as `REL-*` joins;
- record compacts with territorial governments as `CMP-*` (`19-compacts-and-cooperative-governance.md`).

Where membership authority can coerce (e.g., custody/policing or exclusion from essential services), it must be bound by higher-scope rights baselines and independent review (see `21-legitimacy-architecture.md`, `08-remedy-and-grievance.md`).


---

## One-screen blueprint (ideal institutional shape by scope)

This is a *quick reference* for “ideal government” at each scope. Details live in the scope memos.

**Scope memo structure (standard):** owned problems → MVG → ideal stack → failure modes → interfaces → minimal metrics.

| Scope | Default institutional shape (one-liner) | Anti-failure constraints (must be explicit) |
|---|---|---|
| Household / voluntary association | **Charter + easy exit** + mediation/restorative pathway + lightweight shared-funds accounting | anti-coercion; anti-retaliation; escalation routes for rights violations |
| Micro-local | **Chartered Neighborhood Commons Council** (mixed elected + sortition) running **micro-budget PB** + **restorative dispute pathway** | no coercive authority; anti-exclusion + anti-retaliation; mandatory escalation to municipal remedy |
| Sub-municipal (district / borough) | **District councils** with bounded budgets + **service charters** + standing citizens’ panels for major local plans | competence ledger; anti-patronage controls; escalation deadlines to the municipality |
| Municipal | **Council + professional executive** (council-manager or strong admin cabinet) with **admin tribunal + ombuds** | coercion controls; open contracting; zoning/land-use anti-capture; readable accounts + audits |
| Metropolitan (city-region) | **Metro compact council / authority** coordinating corridor goods (transport, land-use alignment, housing targets, air/watersheds) | representation balance (“people + places”); dedicated revenue/transfer channel; “no shadow state” duplication |
| Functional authority (overlay) | **Narrow-mandate board** for a network good (transit/water/schools) with tariff transparency + audits (education spine: `68-education-and-skills-governance.md`) | competence ledger + sunset/review; appeal for billing/access/enforcement; constrain scope creep |
| Regional | **Dual-legitimacy assembly** (“people + places”) plus corridor/bioregional compacts as first-class law | equalization to prevent postcode lotteries; megaproject audit discipline; portability across member jurisdictions |
| National | **Constitutional democracy** with independent courts + integrity stack + professional civil service | rights justiciability; anti-entrenchment guardrails (TM-14); fiscal risk disclosure; oversight follow-through |
| Supranational | **Conferral treaty** + subsidiarity/proportionality + **dual legitimacy** (states + people) + court/arbitration | competence ledger (anti-creep); graduated compliance tools (funding/peer review) not coercive policing |
| Global | **Layered compacts** (charter norms + topic treaties) with independent measurement + ring-fenced finance + due-process dispute systems | non-unitary / polycentric by design; legitimacy via transparency + people’s channel; credible verification |


---
## Authority profile (what changes with scale)

Across the ladder, the “kernel” stays similar. The big variables are **coercion ceiling** and **money base**.

**Coercion ceiling legend (shorthand):** none → administrative (permits/fines) → policing/custody → military/war powers.

| Scope | Legitimacy | Coercion ceiling | Money base | Must interface |
|---|---|---|---|---|
| Micro-local | municipal **charter** + mixed voice | none | micro‑budget transfer | `DRR` + `AL-*` escalation |
| Municipal | elections + admin law | limited | local taxes/fees + transfers | `PRR`/`PAR`/`ALR` + `ENF-*` |
| Metro / functional | delegation (+ direct election if needed) | bounded | tariffs/fees + earmarks | competence ledger + audit |
| Regional | “people + places” | medium | shared taxes + equalization | `IOP-1` compacts + portability |
| National | constitution + courts + elections | high (constrained) | broad tax + borrowing | constitutional review + integrity |
| Supranational | treaty conferral + dual legitimacy | low | small budget + conditional finance | competence ledger + disputes |
| Global | layered compacts + people’s channel | very low | ring‑fenced funds | verification + remedy |

## A compact map (what each scope is *for*)

| Scope | Typical problem class it must own | Primary institutional shape | Deep memo |
|---|---|---|---|
| Household / voluntary association | consent-based coordination; care; norms | charters + exit rights; mediation | (out of scope as “government”, but included as baseline) |
| Micro-local (building/block/neighborhood) | commons stewardship; hyperlocal conflicts; micro-budgets | chartered council + PB + mediation | `10-micro-local.md` |
| Sub-municipal (district/borough) | representation and service co-design in large cities | district councils + service charters | (folds into municipal) |
| Municipal (city/town) | services + land-use + day-to-day rights impacts | elected council + professional executive | `20-municipal.md` |
| Intermediate local administration (county/prefecture) | shared courts/records/health/social services; back-office capacity | shared-services authority (delegated) + service standards + remedy access | `87-intermediate-local-administration.md` |
| Functional authorities (transit/utility/school districts) | network goods crossing city lines; specialized expertise | narrow-mandate boards + audits | `15-functional-authorities.md` (+ metro context: `16-metropolitan-governance.md`) |
| Regional (metro/watershed/state/province) | cross-municipal externalities; corridors; equalization | dual-legitimacy assembly + compacts | `30-regional.md` + `16-metropolitan-governance.md` |
| National | constitutional rights; redistribution; macro; security | constitutional democracy + integrity stack | `40-national.md` |
| Supranational (unions/regimes) | cross-border markets and spillovers | conferral treaty + court + compliance | `50-supranational.md` |
| Global (planetary) | global public goods; existential risks | layered treaties + measurement + finance | `60-global.md` |

This table is intentionally blunt: it is a **competence boundary aid**, not a theory of history.

---

## Scope cards (ideal governments, kept tight)

Each card names (1) **owned problems**, (2) **ideal stack**, and (3) **interfaces**.

### 0) Household / voluntary association (pre-state baseline)

Not “government” in the coercive sense, but crucial because it’s where consent-based governance is easiest.

- **Owns:** care coordination; shared property decisions; internal norms.
- **Ideal stack:** explicit charter/bylaws; easy exit; mediation/restorative options; lightweight accounting for shared funds.
- **Interface:** escalate disputes to micro-local mediation/tribunal pathways when rights violations or coercion appear.

### 1) Micro-local (building / block / neighborhood)

- **Owns:** shared spaces and micro-infrastructure; conflict prevention; localized externalities; bounded micro-budgets.
- **Ideal stack:** chartered Neighborhood Commons Council + participatory budgeting + non-carceral dispute pathway + stewardship loop (see `10-micro-local.md`).
- **Interface:** guaranteed escalation to municipal services/tribunals; crisis protocol linking mutual aid to city emergency operations (see `23-emergency-governance-and-exceptions.md`, `24-mutual-aid-and-serious-incident-protocol.md`).

### 2) Sub-municipal (district / borough) (only where cities are large)

This tier exists to keep large municipalities “close to the ground” without fragmenting core services.

- **Owns:** neighborhood-scale planning inputs; service co-design; local accountability for frontline issues.
- **Ideal stack:** district councils with (a) bounded budgets and (b) *service charters* that create enforceable response commitments; standing citizens’ panels for major local plans (`DEC-2`).
- **Interface:** competence ledger clarifies what districts can decide vs. merely recommend; district-to-city escalation deadlines.

### 3) Municipal (city / town)

- **Owns:** local infrastructure and utilities; land-use/housing; local public health operations; primary safety services (with strict constraints).
- **Ideal stack:** council + professional executive (e.g., council-manager) + open contracting + administrative tribunal + ombuds + coercion controls (see `20-municipal.md`, plus `05/07/08/09/13`).
- **Interface:** legally recognize and fund micro-local councils; join regional compacts for corridors, housing targets, watershed/airshed plans.

### 4) Functional authorities (overlay scopes)

These are *purpose-built governments* for network goods that don’t fit cleanly inside one municipality.

- **Owns:** a single network or portfolio (transit corridor, water basin utility, regional electricity operator, school district).
- **Ideal stack (minimum):**
  - **narrow mandate + sunset/review** for scope creep (`DEC-6`),
  - **board with mixed legitimacy:** users/places + technical members + public interest seats,
  - **transparent tariffs/fees** and open rulemaking (`CAP-7`),
  - **audit + appeal:** ombuds/tribunal access for billing, access, and enforcement (`LAW-3`, `LAW-5`).
- **Interface:** compacts define funding and performance targets (`IOP-1`); publish registries/IDs so people can see *who controls what* (`OPEN-1`).

### 5) Regional (metro / watershed / state- or province-like)

- **Owns:** cross-municipal externalities (transport, housing pressures, pollution); corridors; basin-scale ecology; disaster surge capacity; equalization.
- **Ideal stack:** dual-legitimacy assembly (“people + places”) + compacts as first-class law + megaproject audit discipline (see `30-regional.md`).
- **Interface:** portability across member jurisdictions (identity/credentials/benefits) and intergovernmental dispute resolution (see `70-interoperability.md`, `71-interface-obligations-by-scope.md`).

### 6) National (nation-state)

- **Owns:** constitutional rights; equal citizenship; macroeconomic stabilization; redistribution; national security and foreign affairs (tightly constrained).
- **Ideal stack:** constitutional democracy + independent courts + integrity architecture (audit/anti-corruption/influence transparency) + professional civil service + fiscal transparency and risk disclosure (see `40-national.md`).
- **Interface:** protects local self-organization by default; sets national baselines for rights, remedy, identity, and coercion controls.

### 7) Supranational (unions / confederations / cross-border regimes)

- **Owns:** cross-border market rules and spillovers that states cannot manage alone; mutual recognition with minimum standards; dispute resolution and compliance.
- **Ideal stack:** treaty of **conferral** + subsidiarity/proportionality + dual legitimacy (states + people) + court/arbitration + graduated compliance tools (see `50-supranational.md`).
- **Interface:** competence ledger is mandatory (anti-creep); conditional funding and peer review substitute for coercive policing.

### 8) Global (planetary scope) (layered, not unitary)

- **Owns:** global public goods and existential risks (climate, biodiversity/oceans, catastrophic conflict, pandemics, systemic finance); baseline norms for atrocity accountability and due process.
- **Ideal stack:** a layered architecture of: charter commitments + topic compacts + measurement/verification + ring-fenced finance + due-process dispute systems + structured people’s channel (see `60-global.md`).
- **Interface:** polycentricity by design: where universality fails, coalitions + interoperable standards can still produce public-goods outcomes—*but* measurement and remedy must remain credible.

---

## “Everything in between” as a rule (not more tiers)

You can interpolate intermediate scopes **without inventing new constitutions** by using three patterns (plus one common special case):

1) **Delegation with constraints** (sub-municipal councils, special districts): bounded budgets, narrow mandates, enforceable remedies.
2) **Compacts as law** (`IOP-1`; see `19-compacts-and-cooperative-governance.md`): the “in-between” is often a *treaty-like contract* among governments (regional transit, watershed boards, disaster mutual aid; MASIP activation+review protocol `24-mutual-aid-and-serious-incident-protocol.md`).
3) **Ecological and network overlays** (`OPEN-6`, `CAP-7`): govern where the system boundary is real (basin, grid, corridor), then nest that governance inside democratic and rule-of-law constraints.

4) **Intermediate local administration (county/prefecture pattern):** where municipalities are too small to run courts/records/health/social services reliably, create an *administrative bundle* with **service-delivery mandates** (not a new sovereign). Keep policy discretion narrow, fund by formula transfers, and make its service standards and remedy paths explicit. Treat shared services and inter-municipal arrangements as default where a new tier would be bloat. See `87-intermediate-local-administration.md` for the anti-bloat test, MVG, and interface rules (anchors: [BIB-OECD-MLG], [BIB-OECD-SIGMA-IMC-WBALKANS-2024]).

The anti-bloat test: if a proposed intermediate level doesn’t add **new competence** or reduce **boundary failure**, it should be a committee, not a government.

---

## Quick checks (use when assigning powers)

When deciding “what goes where”, ask:

1) **Local knowledge:** does success require lived context and rapid feedback?
2) **Spillovers:** do harms/benefits cross the boundary?
3) **Scale economies:** do costs drop sharply with size or network integration?
4) **Rights risk:** is there a meaningful risk of rights violations/capture at this tier?
5) **Enforceability:** can this tier actually execute, fund, and audit what it promises?

If 2–3 are “yes”, move upward **but** keep a public justification, proportionality, and an exit/review plan (`70-interoperability.md`, `71-interface-obligations-by-scope.md`).

**Audit rule:** for any non-trivial assignment or transfer, publish a `DRR` tagged `DRR-TYPE: SCOPE` that records the answers, evidence, and the competence-ledger change (old → new). See `IOP-10` in `02-design-toolkit.md`.


---

## Anchor citations (compact)

This memo is intentionally *synthetic*. Key anchors are held in `90-bibliography.md` so the ladder stays short and stable.

Start with:
- Polycentric governance + commons design principles: [BIB-OSTROM-GOVCOMMONS-1990], [BIB-OSTROM-POLYCENTRIC-2010] (overview bridge: [BIB-STERN-2011-IJC-305]).
- Decentralization / “market-preserving” constraints: [BIB-TIEBOUT-1956-JPE], [BIB-WEINGAST-MPF-1995-JLEO], [BIB-FAGUET-2014-WORLDDEV].
- Metro/regional governance typologies and arrangement choices: [BIB-OECD-GOVCITY-2015], [BIB-IDB-METROGOV-2019], [BIB-WB-METROGOV-2020].
- Supranational conferral + subsidiarity discipline: [BIB-TEU-A5].
- Rights + rule-of-law + oversight independence rubrics: [BIB-UDHR]; [BIB-VENICE-ROL-2025]; SAI independence [BIB-INTOSAI-P10]; ombuds/NHRI independence [BIB-UN-PARIS-PRINC-48134].
