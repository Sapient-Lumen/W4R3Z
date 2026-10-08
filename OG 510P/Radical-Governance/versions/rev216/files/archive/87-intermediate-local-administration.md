# Intermediate Local Administration (County / Prefecture / Department Pattern)

**Purpose:** make intermediate local administration (districts/wards) accountable where people actually encounter the state.

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `54-subsidiarity-and-scope-assignment-test.md` for the auditable scope test, and `70/71` for join-keys + publication obligations.

Many systems have a tier between **municipal** and **regional/state** that exists mainly to make **core administrative functions reliable** when municipalities are too small (or too unequal) to run them well.  
This memo treats that tier as an **administrative bundle** (service reliability + shared back-office), not a new sovereign.

## Kernel anchors (do not repeat)
- Scope ladder and interface obligations across levels: `14-...`, `71-...`.
- Metro/regional/national boundary memos: `16-...`, `30-...`, `40-...`.
- Adoption dynamics and discretion shifts: `99-protective-legibility-and-adoption-dynamics.md`.
- Person-facing floors when capacity varies: `98-persons-path-and-accessibility-invariants.md`, `82-...`.

## Named tensions (design must surface these)
- Decentralization for responsiveness vs capacity shortfalls and unequal rights.
- Local knowledge vs parochial capture and corruption.
- Coordination across jurisdictions vs autonomy and plural institutions.
- Administrative layering vs cognitive/manageability budget (don’t add a tier “because”).

---


## Scope card (one-screen)
- **Typical scale / unit types:** county/prefecture/department (administrative bundle across municipalities; wide variance).
- **Owns (and nothing else):** shared-services capacity floor (courts/records, public health ops, social services, procurement, emergency coordination) when municipalities can’t sustain it alone.
- **Does not own:** high-discretion local policy; land-use micro-choices; permanent exception-making without receipts.
- **MVG (minimum viable government):** transparent service catalog + standards; complaint/remedy lanes; audited finances; minimal elected oversight or tight delegated authority discipline.
- **Interfaces:** publish inter-municipal service agreements + cost allocation; escalation and appeal lanes; exceptions/waivers logs (`85`).
- **Top failure modes:** opaque administration, “shadow government”, politicized allocation, service denial by distance (TM-2, TM-3, TM-6).

---

## 1) When this tier is justified (anti-bloat test)

Create/maintain an intermediate local administration **only if** it clears at least one of these tests:

- **Capacity floor test:** municipalities cannot meet a defined service or rights floor (e.g., record integrity, tribunal access, basic public health ops) even with shared-services compacts.
- **Scale-economy test:** the function has strong fixed costs (specialized staff, labs, courts/records systems, 24/7 ops) and gets materially cheaper/better at this size.
- **Equal access test:** without this tier (or strong equalization), services become a “postcode lottery” that violates equal citizenship expectations.
- **Network boundary test:** the real system boundary is county-like (hospital catchments, court circuits, emergency logistics zones).

**If none apply:** do not add a tier. Use **compacts/shared services** or a **narrow functional authority** instead (`19-compacts-and-cooperative-governance.md`, `15-functional-authorities.md`, [BIB-OECD-SIGMA-IMC-WBALKANS-2024]).

---

## 2) What this tier should own (and nothing else)

**Own (administrative bundle)**
- **Records + registries** operations (civil records, property/land records where assigned, archives), with publication + FOI discipline (`31-records-foi-and-government-memory.md`).
- **Local administrative justice access** where municipalities are too small to host it (admin tribunal circuits, ombuds access points) (`66-justice-and-administrative-justice-governance.md`, `08-remedy-and-grievance.md`).
- **Public health operations** at “operational region” scale (labs, surveillance, surge staffing) (`57-public-health-and-biosecurity-governance.md`).
- **Social services back-office** (eligibility processing, casework capacity pools) with clear service standards (`64-social-protection-and-benefits-governance.md`, `82-service-standards-and-minimum-service-guarantees.md`).
- **Shared procurement + contracting** services where it reduces cost/corruption risk, with open contracting (`22-public-integrity-and-procurement.md`).
- **Emergency logistics + mutual aid** coordination bundle (`23-emergency-governance-and-exceptions.md`, `24-mutual-aid-and-serious-incident-protocol.md`).

**Do not own (unless explicitly constitutional)**
- high-discretion policy agendas that could be handled municipally or regionally (avoid “mini-states”)
- land-use policy discretion that enables boundary arbitrage (keep policy at the municipal/metro/regional layer; coordination via compacts)

---

## 3) Minimum Viable Government (MVG)

If this tier exists, it MUST meet the cross-scope MVGS obligations (`71-interface-obligations-by-scope.md`). In addition:

- **Service-bundle charter:** a mandate that lists *exactly* which services it runs, which are delegated, and which are advisory; entry is explicit in the competence ledger (`34-competence-ledger-and-mandate-registry.md`).
- **Service catalog + standards:** publish `SRV-*` entries and service standards/guarantees for the bundle (avoid “deny by delay”) (`47-service-catalog-and-access-journeys-register.md`, `82-...`).
- **Money-to-mandate fit:** stable funding formula and transparent transfers so municipalities can predict what they’re paying for (`18-intergovernmental-finance.md`, [BIB-OATES-1999-FISCALFED]).
- **Administrative remedy access:** a clear `AL-*` lane for service denial/delay and billing errors; escalation to regional/national courts where rights are implicated (`36-appeal-lanes-and-redress-registry.md`).
- **Open procurement + audit:** publish contracting and audit artifacts; treat missing releases as incidents (`38-contracting-and-procurement-register.md`, `84-internal-controls-and-continuous-assurance.md`).

---

## 4) Ideal institutional stack (bounded)

### A) Governance: “shared services first”
Default institutional shape is **municipal delegation** (not a new sovereign):

- **Board:** municipalities appoint representatives (plus limited independent seats for technical integrity / public interest).
- **Direct election only if:** the tier sets meaningful distributive policy (tax rates, allocation trade-offs) rather than running an agreed service bundle.

This keeps democratic accountability anchored in municipalities while still pooling capacity ([BIB-OECD-MLG-REFORMS-2017]).

### B) Service charters + circuit delivery
- Services publish **standard operating commitments** and circuit schedules (where relevant: tribunals, clinics, mobile units).
- Material service failures open an `OFR-*` case with deadlines and closure evidence (`55-oversight-findings-and-response-register.md`).

### C) Clear delegation boundaries (no responsibility laundering)
Every delegated function has:
- a delegation record (competence ledger effective dates + `DRR` justification if transferred),
- a service standard and remedy lane,
- a funding rule that prevents cost-shifting games.

### D) Shared digital spine (portable, not monopolistic)
Prefer shared **register infrastructure** (identity/eligibility/service case status) with portability across municipalities, *without* locking municipalities into opaque vendor stacks (`33-data-protection-and-personal-data-governance.md`, `70-interoperability.md`).

---

## 5) Top failure modes + countermeasures

- **Responsibility blur (“call the county” loop):** publish a “who owns what” map at the point of service (service catalog + competence ledger joins).
- **Patronage / jobs machine:** merit hiring rules + open procurement + audit follow-through (`22-...`, `32-oversight-institutions-and-follow-through.md`).
- **Duplication creep:** sunset/review for the tier’s service bundle; migrate functions back down or up when capacity changes (`74-sunsetting-and-deprecation-discipline.md`).
- **Over-centralization:** keep policy discretion bounded; require municipal opt-in for non-essential expansions; log scope changes as `DRR-TYPE: SCOPE` (`54-...`).

---

## 6) Interfaces

**Downward (to municipalities)**
- service-level commitments + escalation timeouts (service charters)
- cost allocation formula + clear billing transparency (`REL-*` joins)
- co-design channel for service changes (logged as `ENG-*`)

**Upward (to region/nation)**
- rights floors + minimum service guarantees
- harmonized standards and portability for identity/eligibility/service journeys

---

## 7) Success metrics (minimal set)

Keep ≤10 total; select from `03-metrics-and-evidence.md`.

- service timeliness (median + 90p) for top services [LRR-4]
- error/appeal rate and reversal rate [JUS-3]
- cost per case / per transaction (trend) [FIS-5]
- FOI response time + disclosure completeness [LEG-2]
- audit findings closure time [ACC-6]

---

## Anchor citations (compact)

- Multi-level governance reform lessons: [BIB-OECD-MLG-REFORMS-2017].
- Decentralization trade-offs and design notes: [BIB-WB-DECENTRALIZATION-BRIEFNOTES].
- Inter-municipal cooperation as an alternative to adding tiers: [BIB-OECD-SIGMA-IMC-WBALKANS-2024].
- Fiscal federalism baseline (heterogeneity vs spillovers): [BIB-OATES-1999-FISCALFED].
