# Transfer Register & Conditionality (Money is governance)

**Purpose:** make transfers and conditionality (grants, aid, mandates) joinable so obligations, discretion, and enforcement don’t disappear across layers.
**Person served:** a resident or recipient community affected by transfers who needs to see what money funds, what conditions apply, and how conditionality can be contested.

**From-below:** This shows what benefits and conditions really are so you aren’t surprised, coerced, or punished by hidden strings.
**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-07` (Indifference) by making transfers/conditionality auditable and contestable (`98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)
**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations (receipting, time bounds, continuity of records) for transfers/holds/clawbacks so silence can’t cut off essentials. (See `80-implementation-roadmap.md`, `82-service-standards-and-minimum-service-guarantees.md`, `31-records-foi-and-government-memory.md`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Notices & receipts:** holds/withholds/clawbacks and service-impacting conditionality MUST emit `DRR-*` Decision Receipts with the `31` minimum fields (as‑of basis, deadlines/no‑response semantics, continuity backstop, and `AL-*` lane pointers). (`101` NR-02, NR-05, NR-15)
**Proof burdens:** publish what counts as compliance/noncompliance evidence and the least‑burdensome alternatives; “silent holds” are invalid and state‑held facts are retrieved once‑only where feasible. (`101` NR-06)
**Assistance & representation:** where residents are harmed by conditionality enforcement, provide assisted/oral filing + representation/advocacy options and a safe channel for fear/retaliation contexts. (`101` NR-12, NR-17)


Intergovernmental finance becomes **hidden governance** when transfers are opaque, conditions are unclear, or money moves without a corresponding competence/mandate map.

A **Transfer Register** is the smallest public artifact that keeps the *money map* aligned with the *competence map*:
- every transfer is legible (who pays whom, for what, on what terms),
- conditions are typed and auditable (not “policy by spreadsheet”),
- disputes and remedies are explicit (no discretionary punishment).

**Minimum success condition:** a resident (and a recipient unit) can identify every material transfer affecting them and answer: **what it funds, what it requires, how it is measured, and how it is contested** — without insider knowledge.

Anchors: see [BIB-OECD-IGFT-2025]; [BIB-IMF-IGF-2018]; fiscal transparency baselines in [BIB-IMF-FTC-2019] and [BIB-PEFA-2016].

---

## Kernel anchors (do not repeat)
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Material floor / burden realism:** `98-persons-path-and-accessibility-invariants.md`, `82-...`.
- **Intergovernmental conditionality:** `18-intergovernmental-finance.md`.

## Named tensions (design must surface these)
- **Accountability vs cruelty:** ensuring funds are used well vs punishing the vulnerable.
- **Conditionality vs autonomy:** compliance leverage vs self-determination.
- **Standard metrics vs local reality:** comparability vs context.
- **Fraud control vs timely relief:** verification vs hunger/eviction risk.

## A. What belongs in the register
The register covers **any** flow where one public unit finances another (or a pooled fund) in a way that affects service delivery or accountability:

- formula-based equalisation,
- conditional/matching grants (including capital and spillover grants),
- stabilization/emergency transfers,
- pooled funds created via compacts (`CMP`),
- pass-through and earmarked revenues (where material),
- revenue-sharing formulas (shares of nationally collected taxes; the base and calculation should be reproducible from published `REL-*` releases, often joined to `93-...`).
  - For revenue-share transfers, the register MUST also link to the **revenue base publications** (`REL-*`) and any material revenue-admin changes that affect the formula, so “transfer governance” can’t drift away from “collection governance.” (See `101-claude-rev142-normative-requirements.md` (NR-15).)

**Coverage rule:** include transfers that route through SPVs/authorities where the economic substance is intergovernmental (prevents laundering via intermediaries).

---
**Note:** this register is for **intergovernmental** money flows. Grants/subsidies to non-public recipients and tax expenditures are covered in `49-grants-subsidies-and-tax-expenditures-register.md`.

---

## B. Register discipline (non-negotiables)
- **Stable IDs:** every transfer has a stable `TRF` ID (see `70-interoperability.md`).
- **No silent changes:** formula/conditions/eligibility changes create a new version with effective date + change log.
- **Typed conditions:** any conditionality is classified using a small portable condition class (below) and linked to the legal basis (`RULE` / compact clause).
- **Auditability:** publish appropriated vs. disbursed vs. withheld vs. clawed-back (with reasons) on a known cadence.
- **Joinability:** `TRF` entries link to `UNIT` (payer/payee), `CMP` (if compact-backed), `RULE` (legal basis), and (where relevant) `DRR-TYPE: SCOPE` when transfers finance mandate moves; store authorizing decision receipts under `AUTH-DRR` (see `70-...`).
- **Beneficiary continuity (anti-hostage conditionality):** enforcement MUST be designed so that *final recipients* and **essential services** are not punished for higher-level disputes or compliance conflicts; publish the continuity mechanism in the `TRF` entry (see Section H). Anchors: [BIB-EC-ROL-COND-REG-2021]; [BIB-OECD-SNG-INSOLVENCY-2018]; [BIB-IMF-SNG-FISCALRISKS-2022].

### Legibility conditionality ("no money without receipts")
Conditionality should strengthen governance **without** rewarding illegibility.
- **Enforcement actions require receipts:** holds/clawbacks MUST cite `AUTH-DRR` and link to the specific breached condition clause; “silent holds” are invalid.
- **Artifact hygiene as eligibility:** material programs MAY require baseline register compliance (budget/contract/decision receipts) as a condition class (`COND-INT`), but MUST include a support phase and continuity backstops.
- **Resident-facing protection:** where a transfer’s compliance logic causes service denial, residents must have an `AL-*` lane and missing receipts can be raised via `AL-LEG`.
- **Positive incentives:** publish a “fast lane” for units with high artifact-conformance (lighter reporting; quicker disbursement), so compliance becomes strategically attractive.

---

## C. Minimum schema (publish as data + a human view)
| Field | Meaning |
|---|---|
| **Transfer ID (`TRF`)** | stable ID (recommended: `UNITID-TRF-SEQ`) |
| **Payer Unit ID** | from competence ledger (`34-...`) |
| **Recipient Unit IDs** | explicit list (or rule that resolves to units) |
| **Purpose type** | equalisation / conditional / capital / spillover / stabilisation |
| **Mandate link** | which mandate(s) this supports (tags; COFOG when fiscal-facing) |
| **Service links (if applicable)** | `SRV-*` list funded/affected; if enforcement actions impact delivery, the `DRR` receipts SHOULD cite the impacted `SRV-*` (and whether any are `ESS-1`) |
| **Legal basis** | statute / appropriation rule (`RULE-*`) / compact clause (`CMP-*`) |
| **`AUTH-DRR`** | authorizing `DRR-*` for discretionary awards/holds/clawbacks, and for material formula/conditions changes (joins object ↔ decision per `70-...`) |
| **Formula + parameters** | plain-language summary + machine-readable versioned spec |
| **Revenue base (if revenue-share)** | which tax base/collection releases feed the formula (link to `REL-*` and `93-...` publication) |
| **Eligibility rule** | inputs and thresholds; data sources + update cadence |
| **Amount + timing** | appropriated, scheduled, disbursed; variances |
| **Conditions (if any)** | list of condition clauses (typed; verification method; deadlines) |
| **Enforcement ladder** | warn → support → partial holdback → full holdback → clawback (and when each applies) |
| **Dispute/appeal path** | forum + time limits + `AL-*` lane IDs (from ALR `36-...`) for: recipient units *and* affected residents (where services are impacted) |
| **Beneficiary continuity backstop** | if funds are withheld/clawed back, how **`ESS-1` services** / final recipients are protected (route/direct pay/escrow; backstop Unit ID; time bounds; reference relevant `SRV-*` and their continuity floors) |
| **Sunset/review trigger** | mandatory periodic review (and what evidence must be considered) |
| **Version + effective date** | version ID; effective date; superseded link |
| **Change log** | what changed and why |

**Version semantics (canonical):** treat this register as **append‑only** and queryable **as‑of** a date. Publish revisions with monotonic `REV`, `PUBLISHED-AT`, and (when behavior changes) `EFFECTIVE-*` timestamps—see `70-interoperability.md` §“Version semantics & ‘as‑of’ queries”.

**Optional (high leverage):** publish the formula as a small machine-readable artifact (e.g., JSON) pinned by version, so anyone can reproduce allocations.

---

## D. Condition classes (portable; keep small)
Conditionality should be typed so burdens and coercion are visible and comparable.

| Class | Meaning | Default rule |
|---|---|---|
| `COND-OUT` | outcomes/outputs required | prefer this over process controls |
| `COND-COF` | co-financing / matching required | must disclose equity effects |
| `COND-INT` | integrity/compliance safeguards | minimize paperwork; prefer audits |
| `COND-DAT` | data/reporting requirements | publish burden estimate; reuse existing registers/releases |
| `COND-STD` | standards/interoperability requirements | must reference PSR `STD` IDs and pinned versions |
| `COND-REF` | policy/reform commitments | must cite the specific `RULE-*` change required (no vague “reform”) |
| `COND-TMP` | time-bounded emergency conditions | must include sunset + review |

**Anti-overload rule:** conditionality MUST not create a compliance burden that exceeds the expected benefit. Publish a *burden note* (estimated staff hours / reporting objects required) for material programs.

---

## E. Transfers that move power (avoid “backdoor centralisation”)
Transfers often reassign power without saying so:
- conditional grants can effectively dictate local policy,
- capital grants can reshape land use and service priorities,
- emergency funds can become permanent control channels.

**Rule:** when a transfer *functionally* changes mandate assignment or enforcement discretion, it SHOULD be paired with a `DRR-TYPE: SCOPE` (see `IOP-10`) and a competence-ledger update (who can decide what, and who can fix harm).

---

## F. Disputes and remedy (make money contestable)
- **Recipient units** must have a defined dispute path for withheld funds (rapid review lane; reason-giving required).
- **Residents** must have a route to contest service denial when it is caused by transfer compliance logic (otherwise conditionality becomes punishment-by-admin).
- Publish aggregate dispute outcomes (mapped to portable `RC-*` and `AL-*` codes where relevant; see `52-reason-codes-registry.md`).

---

## H. Beneficiary continuity (anti-hostage conditionality)
Conditionality regimes often fail by turning residents into **hostages**: funds are suspended for governance failures, and the people who lose services are not the people who caused the breach. This destroys legitimacy and can create perverse incentives (units hide problems to avoid sanctions).

**Rule:** conditionality enforcement MUST be **targetable** to responsible actors and MUST preserve **essential public services**.

**Operationalization:** treat “essential” as a property of services, not rhetoric: flag services as `ESS-1` in the `SRV-*` catalog (with published continuity floors) and have `TRF` entries and enforcement receipts (`DRR`) cite the impacted `SRV-*` so continuity promises are auditable.

**Default ladder (resident-protecting):**
- **Support before punishment:** technical assistance, phased compliance plans, and time-bounded corrective action orders before holdbacks.
- **Prefer routing over suspension:** where feasible, route funds **directly to providers/final recipients** (or via escrow) instead of cutting off service funding.
- **Time-bounded holdbacks:** if holdbacks are unavoidable, they MUST be proportionate, time-bounded, and paired with a published continuity plan (backstop Unit ID + service minimums + reversion path).
- **Contestability:** both recipient units and affected residents MUST have a clear dispute/appeal lane (`AL-*`) and reason-giving in `DRR` form for material enforcement actions (link the `TRF-*`).

**Why this is not optional:** credible no-bailout / hard-budget regimes still assume essential services continue during distress/workouts; insolvency and fiscal-risk frameworks explicitly treat service continuity as a design constraint, not an afterthought. Anchors: [BIB-OECD-SNG-INSOLVENCY-2018]; [BIB-IMF-SNG-FISCALRISKS-2022]; [BIB-WB-UNTILDEBT-2013]. A worked example of “protect beneficiaries while applying conditionality” exists in EU budget conditionality framing. See [BIB-EC-ROL-COND-REG-2021].

**Interface rule:** the continuity mechanism MUST be recorded in the `TRF` entry (schema field above) so it is auditable and discoverable.

## G. Minimal “done” checklist
- [ ] A public `TRF` register exists with stable IDs, versions, and change logs.  
- [ ] Every `TRF` links to payer/recipient Unit IDs and legal basis (`RULE`/`CMP`).  
- [ ] Conditionality is typed, verifiable, and has a dispute path (for recipient units **and** affected residents).  
- [ ] Appropriated vs. disbursed vs. withheld/clawed-back is published.  
- [ ] Mandate moves financed by transfers are logged as `DRR-TYPE: SCOPE` and reflected in the competence ledger.