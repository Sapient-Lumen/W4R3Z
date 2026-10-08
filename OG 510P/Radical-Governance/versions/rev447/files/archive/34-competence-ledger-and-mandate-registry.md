# Competence Ledger & Mandate Registry (Public jurisdiction map)

**Purpose:** map who has authority/competence to act (and under what mandate) so delegation can’t launder reality and responsibilities remain traceable.
**Person served:** a resident trying to get a decision made or harm fixed who needs to know which unit has authority, under what mandate, and how to route remedy.

**From-below:** This lets you see who is authorized and competent to decide about you so power can’t hide behind opaque delegations.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-06` (Complexity) by making authority lanes and mandates discoverable without insider status (see `98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

People lose rights *in practice* when they cannot reliably answer: **who can decide, who must act, and who can fix harm**.  
A **competence ledger** is the smallest public artifact that prevents “hidden government” and responsibility laundering across scopes.

This memo standardizes a ledger that is:
- **public** (human-readable + machine-readable),
- **versioned** (changes are auditable),
- **joinable** (links to rules, decisions, budgets, data systems),
- **complete** (includes special districts / functional authorities).

See also: `25-legal-legibility-and-rule-inventory.md` (Public Rules Register), `31-records-foi-and-government-memory.md` (Decision Records / Receipts), `78-delegation-and-acting-authority-discipline.md` (authority-chain receipts), and `70-interoperability.md` (boundary interfaces).

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Scope + functional authorities: `14-...`, `15-...`.
- Influence/COI joins: `46-...`, `79-...` (who benefits from ambiguity).
- Publication integrity for mandates/charters (“no silent edits”): `53-...`.
- Adoption dynamics: map as-is without laundering legitimacy (`99-protective-legibility-and-adoption-dynamics.md`).

## Named tensions (design must surface these)
- Mapping reality (de facto power) vs conferring legitimacy by listing it.
- Central coordination vs plural authority / functional equivalents.
- Transparency about authority chains vs safety for staff/complainants in coercive contexts.
- Stability of mandate boundaries vs responsiveness during emergencies/transition states.

---
## A. What the ledger is (and is not)
**Is:** a *public register* of authority boundaries and decision rights with stable **Unit IDs**.  
**Is not:** an internal org chart, a “strategy”, or a marketing page.
**Does not confer legitimacy:** record authority *as exercised* (de jure and de facto), including overlaps and contested competence. The ledger is a public map that makes disputes visible and routable.

**Minimum success condition:** a resident can determine (1) **who owns the decision**, (2) **the legal basis**, and (3) **the remedy lane**, *without insider knowledge*.

---

## B. Competence ledger — minimum schema (keep it legible)
| Field | Meaning |
|---|---|
| **Unit ID** | stable identifier for the jurisdiction/body (resolves to an entry) |
| **Coverage (if applicable)** | territory or service-area reference + boundary change log |
| **Selection / decision method** | elected / appointed / sortition / mixed + term/rotation rules |
| **Mandates (can decide)** | bounded list of decision areas (taggable) |
| **Non-mandates (cannot)** | explicit exclusions (prevents mission creep) |
| **Legal basis** | charter / statute / compact (link to PRR `RULE` IDs where feasible) |
| **Authority status (optional)** | de jure / de facto / contested; record overlaps without pretending they are resolved |
| **Overrule conditions** | who can overrule, on what grounds, with what process |
| **Backstop + escalation** | backstop Unit ID for failures/gaps; competence-dispute lane (`AL-COMP`) + timeouts |
| **Funding responsibility** | taxes/fees/transfers + who bears residual risk |
| **Appeal / remedy path** | who can stop harm, who reviews, who enforces (see `08-...`) |
| **Data systems** | core registries and accountability logs (`IOP-4/5/6/9`) |
| **Compacts** | list of active `CMP-*` IDs that materially affect mandates/operations (or explicitly “none”) (`IOP-1`) |
| **Contact + duty roles** | publish “duty officer” role for urgent coordination (not a person) |
| **Authority schedule** | pointer to the role-level signatory matrix (published as a versioned `REL-*` release) |
| **Version + effective date** | version ID, effective date, and deprecation if replaced |
| **Review/sunset trigger** | when this mandate assignment must be reconsidered |

**Version semantics (canonical):** treat this register as **append‑only** and queryable **as‑of** a date. Publish revisions with monotonic `REV`, `PUBLISHED-AT`, and (when behavior changes) `EFFECTIVE-*` timestamps—see `70-interoperability.md` §“Version semantics & ‘as‑of’ queries”.

**Coverage rule:** functional authorities / special districts MUST appear in the ledger (otherwise they become “hidden government”).  
**Change rule:** any creation/merge/split/major mandate transfer MUST publish a `DRR` tagged `DRR-TYPE: SCOPE`, update the ledger entry, and re-check backstops for affected mandates (see `IOP-10`).  
**Cross-link rule:** major decisions SHOULD cite `Unit ID`, relevant `RULE` IDs, and (where relevant) `DPR` and contract IDs; when a mandate/service is materially **delivered by contract**, the ledger SHOULD point to the major `CON-*` and `SRV-*` so accountability can’t be outsourced.

---

## B1. Unit IDs (minting rules + minimum fields)
The ledger only works if **Unit IDs are stable join-keys** across time, mergers/splits, and data systems.

**Minting rules (minimum):**
- **Namespaced + non-reused:** Unit IDs MUST be unique within the jurisdictional namespace and MUST NOT be reused.
- **Change = new ID:** merges/splits/abolition create new Unit IDs; old IDs remain resolvable with replacement pointers.
- **Crosswalk required:** every change publishes a predecessor/successor mapping (old → new) with effective dates (linked from the `DRR-TYPE: SCOPE` record).
- **Coverage references are pointers, not prose:** when a unit has a territorial/service boundary, publish a stable boundary reference (e.g., a `REL-*` release that contains the geometry) rather than a descriptive paragraph.

**Minimum Unit ID entry fields (tight):**
| Field | Meaning |
|---|---|
| `UNIT` | Unit ID (string) |
| `NAME` | official name + short label |
| `UNIT-TYPE` | general-purpose / functional authority / tribunal / oversight body / other |
| `PARENT` | parent Unit ID (if nested) |
| `COV` | coverage pointer (e.g., `REL-*` that contains boundary geometry) + effective window |
| `COV-REF` | optional external coverage codes (e.g., OCD division IDs [BIB-OCD-DIVISION-IDS]; ISO 3166‑2 subdivision codes [BIB-ISO-3166-2]) |
| `ACTIVE` | start/end (or open-ended) |
| `REPLACES` / `REPLACED-BY` | predecessor/successor Unit IDs |
| `ENDPOINTS` | URLs or handles for the unit’s PRR/PDRR/ALR feeds (if published) |

**Why the external codes are optional:** many places already use durable geographic codes (national geocodes, ISO subdivisions, or open civic identifiers). Storing these as *secondary references* lets the competence ledger interoperate without surrendering local autonomy.

## C. Mandate taxonomy (avoid bespoke category chaos)
To compare budgets, outcomes, and responsibilities across scopes, mandates SHOULD be taggable using at least one shared taxonomy.

**Baseline option (recommended):** tag fiscal-facing mandates using **COFOG** (Classification of the Functions of Government) divisions/groups as a common denominator. See [BIB-UNSD-COFOG] and fiscal compilation guidance in [BIB-IMF-GFSM-2014].  
Local additions are allowed, but MUST map back to the baseline tags.

**Why this matters:** a scope transfer without a shared tag system becomes unauditable (“we moved *something* to Authority X”).

---

## D. Lifecycle discipline (ledger hygiene)
1) **Create** — entry begins with legal basis + **scope test docket** evidence (see `54-subsidiarity-and-scope-assignment-test.md`), published via `DRR-TYPE: SCOPE`.  
2) **Operate** — decisions and budgets link to `Unit ID`; compacts and registers are referenced.  
3) **Review** — scheduled review triggers (sunset, performance failure, boundary spillovers, capture indicators).  
4) **Change** — merge/split/boundary/mandate change: new version + effective date + remedy continuity plan.  
5) **Retire** — deprecate old entry; keep it discoverable with “replaced by” pointers.

**Ledger freshness rule:** publish a “staleness report” (entries not reviewed in X months) and treat it as a governance risk.

---

## E. Interoperability: the ledger as a join-key
The competence ledger is a *join-key registry*:
- **PRR (rules):** “this unit is authorized by RULE-…”
- **DRR (decisions):** “this unit issued DRR-…”
- **Budget lines / programs:** “this unit owns program …”
- **Registers:** “this unit operates register …”
- **Remedy lanes:** “this unit is reviewed by …”

This is how polycentric governance stays legible while remaining decentralized.

---

## F. Common failure modes (and minimum mitigations)
- **Hidden government (off-book authorities):** mandate all units appear in the ledger; audit using spend/liability reconciliation.  
- **Responsibility laundering:** require explicit “non-mandates”; publish overrule conditions + duty-to-route requests (measure “wrong door” rate).
- **Orphan mandates (no one obligated to act):** require a backstop Unit ID + timeout-bound escalation in the ledger; audit “unassigned” complaints.  
- **Scope creep:** mandate versioned changes + `DRR-TYPE: SCOPE` publication + periodic review.  
- **Stale/incorrect entries:** staleness report + random verification audits + user feedback channel.

For U.S. baseline evidence that “special purpose” governments are numerous and functionally diverse, see Census of Governments special district breakdowns: [BIB-USCENSUS-SPECIALDIST-2022].
