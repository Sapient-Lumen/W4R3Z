# Interoperability (How Scopes Plug Together)

Governance fails at boundaries. This memo defines a small set of *interfaces* so polycentric systems can behave like one system when needed.

## One-screen join-key map (the MVGS “interfaces”)

These IDs are the archive’s anti-chaos mechanism: they let audits, appeals, and coordination *join up* across scopes.

- `Unit ID` — **who has authority** (competence ledger). See `34-competence-ledger-and-mandate-registry.md` (Unit ID minting rules + minimum fields in §B1).
- `EID` — **who a non-state actor is** (entity identifier bundle for vendors, grantees, lobby entities; avoids inventing a new global ID family). See §Entity identifiers below.
- `RULE-*` — **what rule is in force** (Public Rules Register, versioned). See `39-rulebook-and-instruments-registry.md` (§B PRR — minimum schema).
- `STD-*` — **which governance-grade standard applies** (Public Standards Register; pinned versions + transition discipline). See `27-standards-and-technical-governance.md` (§C PSR — minimum schema).
- `DRR-*` — **why a decision happened** (decision receipt: reasons + legal basis + appeal lane). See `31-records-foi-and-government-memory.md` (Decision Receipt / Record — minimal public schema).
- `FOI-*` — **which access-to-information request** is at issue (FOI log). See `31-records-foi-and-government-memory.md` (FOI log entry — minimal public skeleton in §3C).
- `AL-*` — **where to appeal / get urgent protection** (Redress Registry / ALR). See `36-appeal-lanes-and-redress-registry.md` (§B Minimum fields; §F lane skeleton).
- `REL-*` — **what “official fact” is being used** (Public Data Release Register / PDRR). See `26-epistemic-infrastructure-and-public-knowledge.md` (Skeleton: `REL` release record — publishable).
- `PROG-*` / `EVAL-*` / `CLM-*` — **what is being attempted and what should be true** (programs, evaluations, falsifiable claims). See `28-program-register-and-evaluation-commitments.md` (§B registers) and `37-claims-evidence-and-update-discipline.md` (§A CLM object).
- `CMP-*` — **which compact binds units** (compact record: parties, scope, metrics, enforcement ladder, dispute path). Material enforcement/dispute actions SHOULD issue a `DRR` that links the `CMP-*`. See `19-compacts-and-cooperative-governance.md` (§4 Compact Register; `CMP` record skeleton).
- `TRF-*` — **which transfer/conditionality applies** (Transfer Register). See `35-transfer-register-and-conditionality.md` (§C Minimum schema).
- `GRT-*` / `TEX-*` — **which grant/subsidy or tax expenditure applies** (Grants/Subsidies/Tax Expenditures Register). See `49-grants-subsidies-and-tax-expenditures-register.md` (§C Minimum schema).
- `SRV-*` — **which service workflow is at issue** (Service Catalog & Access Journeys). See `47-service-catalog-and-access-journeys-register.md` (§A Object; §B Minimal public schema).
- `AST-*` — **which asset/infrastructure object** is at issue (Asset & Infrastructure Register). See `48-asset-and-infrastructure-register.md` (§2 Minimal public fields).
- `ENG-*` — **what participation occurred** (Participation & Deliberation Register with duty-to-respond). See `41-public-participation-and-deliberation-register.md` (§3 Minimal schema; §7 skeleton).
- `CON-*` / `OCID` — **which contract** (open contracting). See `38-contracting-and-procurement-register.md` (§B Minimal CPR record).
- `ENF-*` — **which enforcement/custody event** (where coercive units exist). See `43-enforcement-and-custody-event-register.md` (§4 `ENF` register entry — minimum schema).
- `OFR-*` — **oversight file** (case or finding): findings + responses + closure, and (for cases) a joinable timeline spine. See `32-oversight-institutions-and-follow-through.md` (OFRR — minimum fields).
- `EMR-*` — **which emergency measure/exception** (logged + reviewed). See `45-emergency-measures-register.md` (§C minimum schema).

Mutual aid activations SHOULD be logged as a `DRR-*` tagged `DRR-TYPE: AID` (the MAAL record in `24-...`), and serious incidents SHOULD open an `OFR-*` entry within 24 hours (state `OPEN`, `OFR-KIND: CASE`) so independence and timelines are auditable.

Rule of thumb: if an action affects rights, money, or coercion, it SHOULD cite at least `DRR-*` + `RULE-*` + `AL-*` (+ the relevant register ID for the domain).

## Artifact invariants (the “minimum fields” all scopes should enforce)
Treat these as governance-grade interface contracts. If an artifact exists but violates these invariants, it does not count as compliant.

**Common invariant fields (apply everywhere):**
- **Stable ID** + issuing **Unit ID**
- **Timestamp** (issued-at) + effective date (if different)
- **Legal basis / scope** pointer (`RULE-*` / charter / compact)
- **Reasons** (plain language + `RC-*` codes where relevant)
- **Remedy lane** (`AL-*`) + deadlines (and a no-response rule)
- **Revision log** (no silent edits)

**Object-specific minimum joins:**
- `DRR-*` MUST join to: `RULE-*` (as-of), `AL-*`, and `REL-*`/`ADS-*`/`ENF-*` where material.
- `REL-*` MUST publish: method note, revision policy/log, and contestation lane.
- `ADS-*` MUST publish: purpose, role, versioning, audit hooks, and appealability notes.
- `CLM-*` MUST publish: baseline, metrics, review trigger, and versioned status.



## Entity identifiers (EID) (joinable private actors without doxxing)

Many joins depend on identifying **non-state counterparties** (vendors, grantees, regulated firms, lobby entities) in a stable way. Rather than add a new global ID family, use a small **Entity Identifier Bundle** field (`EID`) that carries *authoritative external identifiers* and supports entity resolution across scopes.

**Preferred identifiers (in order):**
- **Business registry / incorporation ID** (jurisdictional, authoritative)
- **LEI** (ISO 17442) where available for larger entities or cross-border joins ([BIB-GLEIF-ISO17442])
- **Other high-quality public identifiers** used in the jurisdiction (e.g., charity registry IDs)

### Minimal `EID` bundle (portable)
Store as a small JSON object (or structured columns) wherever an external party appears.

| Field | Meaning |
|---|---|
| `scheme` | identifier scheme / registry (e.g., `BRN`, `LEI`, `CHARITY`) |
| `value` | identifier value |
| `jurisdiction` | issuer jurisdiction (ISO 3166-1/2 where applicable) |
| `name` | legal name as-of (for disambiguation; not a join key) |

**Rules:**
- `scheme+value+jurisdiction` MUST be sufficient to re-find the entity in the source registry.
- If multiple IDs exist, store multiple `EID` entries; never overwrite IDs silently.
- For natural persons, do **not** publish government ID numbers; use protected-layer identifiers only (see `33-...`).

### Beneficial ownership join pattern (optional, high value)
When *control/ownership* matters (high-value procurement, subsidies, regulated concessions), require beneficial ownership disclosure and make it joinable: 

- Publish beneficial ownership statements as a **`REL-*` release** using BODS where feasible ([BIB-BODS]).
- On `CON-*`, `GRT-*`, and `INF-*` records, store **statement references** (e.g., BODS statement IDs) or a pointer to the relevant `REL-*` release.
- Add **verification** checks appropriate to capacity (self-declaration + cross-checks + targeted audits); see Open Ownership verification guidance ([BIB-OPENOWNERSHIP-VERIFY-2020]) and FATF expectations ([BIB-FATF-BO-2023]).

**Privacy/abuse resistance:** publish only what law permits; where beneficial owner identities are sensitive, keep person-level identifiers in protected layers with logged access and publish at least *existence/coverage* and *verification status* publicly.

## Why `DRR` is the keystone (decision receipts as capability tokens)
In this archive, a rights‑ or resource‑affecting act is **not governance‑grade** unless it emits a `DRR-*` that can be cited, audited, and appealed.

- A `DRR` functions like a **capability token for public authority**: it is the joinable reference that proves *who* acted, *under what rule*, *for what stated reasons*, and *where remedy lies*.
- **Absence is evidence:** if a class of actions must produce `DRR`/`ENF`/`CON`/`REL` artifacts, systematic gaps are treated as incidents (pattern‑detectable via complaints, audits, and gap analysis) and trigger escalation through oversight + urgent lanes.
- Scope/mandate moves MUST use `DRR-TYPE: SCOPE` so subsidiarity is contestable rather than rhetorical (`IOP-10`).

### DRR types (portable categories; keep the set small)
`DRR-TYPE` is an optional classification on decision records/receipts. When it is used, the value SHOULD map to one of these portable categories:

- `SCOPE` — mandate assignment/transfer or boundary adjustment (subsidiarity decisions)
- `COMPETENCE` — boundary/overlap/gap ruling (“who decides?” resolution)
- `AID` — mutual aid activation (the MAAL record)
- `INTEGRITY` — recusal / conflicts / integrity actions attached to decisions (useful for audits across scopes)

Local systems MAY add additional detail (e.g., `DRRX:<UNITID>:<slug>`), but SHOULD also include the nearest portable category above so audits and remedy stats join across scopes.

## 0) The competence ledger (public jurisdiction map)
Every scope maintains a public **competence ledger**: a versioned register of **Unit IDs** that makes authority boundaries legible (who can decide, who must act, who can fix harm).

**Canonical spec:** `34-competence-ledger-and-mandate-registry.md`.

**Interface rules:**
- The ledger MUST include functional authorities / special districts (prevents “hidden government”).
- Any creation/merge/split/boundary change/major mandate transfer MUST publish `DRR-TYPE: SCOPE` and update the ledger entry (see `IOP-10`).
- Major decisions SHOULD cite `Unit ID` + relevant `RULE` IDs + appeal lane.

## 0a) Competence disputes and boundary conflicts (who decides when mandates overlap)
Polycentric systems regularly face **overlap**: two units both claim authority, or a mandate boundary is unclear. If this is handled informally, the result is forum-shopping, arbitrary enforcement, and “hidden vetoes.”

**Minimum protocol**
- **Standstill for irreversible harm:** if competence is contested, the default is *no irreversible action* until a rapid competence review occurs (with an emergency override logged in the EMR when delay would cause greater harm).
- **Rapid competence review lane:** pre-designate a forum (tribunal/arbitration/joint committee) that can decide competence questions on short deadlines; publish it in the Redress Registry as a discoverable lane (e.g., `AL-COMP`).
- **Backstop obligation + timeout:** the competence ledger SHOULD name a backstop Unit ID for high-impact mandates; if the rapid lane cannot rule by deadline, the backstop MUST issue a time-bounded interim routing/allocation order (logged as `DRR-TYPE: COMPETENCE`).
- **Public resolution:** publish a reasoned competence ruling and update the competence ledger (new version + effective date + crosswalk for responsibilities).
- **Remedy continuity:** ensure affected parties keep standing and a clear appeal path even if responsibility shifts mid-process.


### `DRR-TYPE: COMPETENCE` (minimum public ruling record)
When a competence dispute is decided (overlap, gap, or contested overrule), publish a `DRR` tagged `DRR-TYPE: COMPETENCE` that records:
- contested Unit IDs + the contested mandate(s) (tags where feasible),
- interim standstill rule and any emergency override (`EMR-*` link),
- forum + lane ID (`AL-*`) + deadline (tribunal/arbitration/joint committee),
- ruling (who owns the decision / who must act / who provides remedy) + effective date,
- competence-ledger update (old → new version) + transition responsibilities,
- remedy continuity (where affected parties go during/after the change).

This deprecates ad hoc overlap-resolution prose and forces boundary rulings into the audit trail (see `31-records-foi-and-government-memory.md`).

**Interface rule:** high-impact decisions SHOULD cite the relevant competence-ledger version/entry as part of the “why we had authority” legibility story (and as a join-key for later audit and remedy).

### Example: contested mandate (permit vs. watershed authority)
- A municipality issues a landfill permit (`PAR-*`) relying on local zoning `RULE-*`; a regional watershed authority asserts the permit violates basin allocation rules in a compact (`CMP-*`).
- **Standstill:** no irreversible siting/clearing until a rapid competence review; any emergency override is logged in the EMR (`EMR-*`).
- **Competence ruling:** the rapid lane issues a public ruling: which unit is competent for which part (land-use vs. basin impacts), and the conditions for proceeding.
- **Ledger update:** publish a new competence-ledger version + crosswalk (who now decides what). Link the ruling to the affected `RULE`/`PAR` entries.
- **Remedy continuity:** affected parties keep standing; appeals reference the same join-keys (`DRR`, `RULE`, `PAR`, `CMP`).

- **Compact accountability:** when a compact changes user outcomes (service denial, penalties, receiver/replace, exit/upgrade), issue a `DRR` that links the `CMP-*`, cites the `RULE-*` basis, and points to the relevant `AL-*` dispute lane (prevents “hidden government” drift).

### Mandate transfers (scope decisions) are decision records, not folklore
Boundary changes and mandate transfers are a high-leverage failure point: if the “why” is undocumented, you get blame-shifting, unfunded mandates, and remedy collapse.

**Rule:** any non-trivial mandate assignment/transfer SHOULD be recorded as a public `DRR` tagged `DRR-TYPE: SCOPE` (see `IOP-10` in `02-design-toolkit.md`) that links:
- the scope tests (local knowledge, spillovers, scale economies, rights/capture risk, enforceability),
- the competence-ledger change (old → new entry/version + effective date) + backstop mapping for affected mandates,
- the money interface change (revenue/transfers/liabilities),
- the remedy continuity plan (where appeals go during transition).

## 0b) Rules interface (legal legibility)
Multi-level governance requires a canonical **Public Rules Register (PRR)** with stable IDs and versioning, and rights-affecting decisions that cite the **Rule IDs** they apply.

**Minimum:** each unit's competence ledger entry SHOULD link to its PRR; compacts, emergency measures, and `ADS-*` registers SHOULD reference Rule IDs as join-keys for auditability and remedy.

See: `39-rulebook-and-instruments-registry.md` and `25-legal-legibility-and-rule-inventory.md`.

## 0c) Evidence interface (public facts)
Polycentric systems need a shared way to reference **official facts** (datasets/series), otherwise coordination devolves into dueling dashboards.

**Minimum:** units SHOULD maintain a **Public Data Release Register (PDRR)** with stable Release IDs, methods, and revision logs; competence-ledger entries SHOULD link to the producing unit’s PDRR. Releases SHOULD reference metric IDs from `03-metrics-and-evidence.md` where applicable.

See: `26-epistemic-infrastructure-and-public-knowledge.md`.

**Learning interface (programs):** `PROG-*` entries SHOULD link to metric IDs and `REL-*` releases, and `EVAL-*` entries SHOULD cite tested `CLM-*` IDs (so evidence and revisions attach). See: `28-program-register-and-evaluation-commitments.md` and `37-claims-evidence-and-update-discipline.md`.

## 0d) Standards interface (technical rules)
Many binding rules are implemented as **technical standards** (protocols, data schemas, safety tests, audit formats). Treat “governance-grade” standards as first-class objects:

**Minimum:**
- Maintain a **Public Standards Register (PSR)** with stable `STD-*` IDs and pinned versions for any standard that is required for access, incorporated by reference, or required in essential procurement.
- PRR Rule IDs that incorporate standards MUST reference the PSR `STD-*` ID + version.
- Standards SHOULD be **testable** (conformance statement + validator/test suite) and transitions MUST be logged (no silent compliance changes).
- Incorporated standards MUST be **publicly accessible** (avoid “paywalled law”).

See: `27-standards-and-technical-governance.md`.

## 0e) Register pattern (stable IDs + change logs)
The archive increasingly relies on “public registers” (rules, standards, data releases, programs/evaluations, compacts, emergency measures, transfers, ADS, permits/approvals, records/FOI requests, participation/deliberation processes, **decision records/receipts**, **oversight findings/responses**). To keep these **legible** and interoperable, treat registers as a single reusable primitive.

**Minimum rules**
- **Stable IDs:** mint globally unique IDs within the issuing unit (prefix with the Unit ID); never reuse; include a status (active/retired).
- **No silent changes:** every change produces a new version with effective date + change log; keep prior versions accessible.
- **Two views:** human-readable page + machine-readable feed/API; IDs are join-keys across systems.
- **Provenance:** each entry states owning unit, legal basis (if any), coverage, and links to related IDs (`RULE`/`STD`/`REL`/`PROG`/`EVAL`/`CMP`/`EMR`/`TRF`/`ADS`/`PAR`/etc.).
- **Access + privacy:** default public; exemptions are typed and logged (and time-bounded where possible).

### Generic register entry — minimum schema
| Field | Meaning |
|---|---|
| Object ID | stable identifier (join-key) |
| Title / short description | human legibility |
| Owning unit | Unit ID from competence ledger |
| Status + version | active/retired + semantic version or revision |
| Effective dates | published / effective / superseded |
| Legal basis | Rule ID / statute / compact |
| Coverage | territory/service scope if relevant |
| Links | related IDs (rules, standards, releases, programs/evals, compacts, EMR, transfers, permits, contracts) |
| Change log | what changed and why |

### ID conventions (recommended; keep stable and namespaced)
To make cross-scope joins work without a central global ID authority:

- **Namespace by Unit ID:** every Object ID starts with the issuing unit’s **Unit ID** (from the competence ledger).
- **Type code:** include a short type segment so IDs are self-describing.
- **Do not reuse:** retired IDs stay retired; updates create a new version, not a new ID.

**Recommended shape:** `UNITID-TYPE-SEQ` (or `UNITID:TYPE:SEQ`), where `TYPE` is one of:

| TYPE | Object | Register / memo |
|---|---|---|
| `RULE` | binding rule | PRR (`39-...`) + overview (`25-...`) |
| `DRR` | decision record/receipt (rights-affecting decision) | Records system (`31-...`) + remedy (`08-...`) |
| `ENF` | enforcement/custody event (coercion log) | ENF register (`43-...`) + coercion memo (`05-...`) |
| `AL` | appeal lane (redress path) | ALR (`36-...`) + remedy (`08-...`) |
| `STD` | governance-grade standard | PSR (`27-...`) |
| `REL` | official data release / series | PDRR (`26-...`) |
| `PROG` | program / policy object | Program Register (`28-...`) |
| `SRV` | public service / access journey | Service Catalog Register (`47-...`) |
| `AST` | asset / infrastructure object | Asset & Infrastructure Register (`48-...`) |
| `CLM` | testable claim / prediction | Claims discipline (`37-...`) + Program Register (`28-...`) |
| `ENG` | public participation / deliberation process | Participation & Deliberation Register (`41-...`) |
| `INF` | influence interaction (lobbying/meetings/gifts/etc.) | Influence & Interests Register (`46-...`) + integrity memo (`22-...`) |
| `INT` | interests/COI declaration + management actions | Influence & Interests Register (`46-...`) + integrity memo (`22-...`) |
| `EVAL` | evaluation commitment / report | Evaluation Registry (`28-...`) |
| `CMP` | compact / interlocal agreement | Compact Register (`19-...`) |
| `EMR` | emergency episode / measure | EMR register spec (`45-...`) + overview (`23-...`) |
| `DPR` | personal data processing activity | DPR (`33-...`) |
| `IDN` | identity/credential system (access gate) | IDN register spec (`44-...`) + identity memo (`12-...`) |
| `ADS` | automated decision system | ADS/MOD register spec (`42-...`) (also `IOP-5`, `06-...`) |
| `MOD` | model component (high-impact/reused) | ADS/MOD register spec (`42-...`) |
| `PAR` | permit / approval | PAR (`29-...`) |
| `CON` | contract / procurement process | CPR (`38-...`) (anchor: [BIB-OCDS]) |
| `OFR` | oversight finding/response | OFRR (`32-...`) |
| `FOI` | FOI/RTI request | FOI log (`31-...`) |
| `TRF` | intergovernmental transfer | Transfer register (`35-...`) + IGF design (`18-...`) |

**Naming note:** `DEC-*` is a *toolkit module prefix* (decision & legitimacy). `DRR` is the *ID type* for Decision Records/Receipts.

Example: `NYC-RULE-01234` or `U123:EMR:0007`. The exact syntax is local; the **joinability** rule is not.

### Core join keys (minimal join graph)
These IDs are the *spine* that lets scopes interoperate without merging institutions. Keep the set small.

| If you’re publishing… | Include these join-keys when relevant | Why |
|---|---|---|
| a rights-/resource-affecting **decision** | `DRR` + `RULE` (legal basis **+ version/as-of**) + `UNIT` (issuer) + `RC-*` + `AL-*` (from ALR `36-...`) + `ENF-*` when the decision is a coercive contact (stop/search/arrest/detention/use-of-force) + `ADS-*` (and `MOD-*` when material) when automated systems are used + `CLM-*` when making predictions + `ENG-*` when participation/deliberation informed it + `INF-*` when ex parte influence disclosures exist + `INT-*` when conflicts/recusals are material + `IDN-*` when identity/credential proofing/verification is a precondition or cause of denial + `SRV-*` when the decision occurs within a defined service workflow + `AST-*` when the decision creates/changes a material asset, approves major works, or defers maintenance | contestability + auditability |
| an **enforcement/custody event** | `ENF` + linked `DRR` receipt (when provided) + `RULE` (as-of) + `AL-*` + evidence pointers + `OFR-*` when serious incident review occurs | prevents dark enforcement; supports independent review & learning |
| a **rule** or policy | `RULE` + `STD` (if incorporated) + `REL`/metric IDs (if evidence-based) | legibility + reproducibility |
| a **dataset / release** | `REL` + method + revision log + producing `UNIT` | shared facts + comparability |
| an **ADS** | `ADS` + linked `RULE` + linked `DPR` + (often) `PROG` | constrain automation + enable redress |
| a **program** | `PROG` + `CLM-*` claims + (where feasible) joinable budget/execution line references via `REL-*` releases (plus functional/program classification codes) + `REL`/metric IDs + `EVAL` commitments | learning loops |
| a **contract / concession** | `CON` (+ OCID if using OCDS) + supplier `EID` bundle + (optional) BO statement references (prefer BODS; typically via a `REL-*` BO release) + `SRV-*` (services materially delivered/operated) + `ADS-*`/`MOD-*` (if automated decisions are in scope) + (when published) execution/payment ledger release (`REL-*`) | integrity + traceability |
| an intergovernmental **transfer** | `TRF` + payer/recipient `UNIT` + (if compact-backed) `CMP` + legal basis `RULE` | money-map legibility + anti-blame shifting |
| a **permit / approval** | `PAR` + `AUTH-DRR` (decision receipt) + criteria `RULE` + (if applicable) `REL` evidence + appeal path | prevent arbitrary permissioning |
| a public **engagement / deliberation** process | `ENG` + decision hook `DRR` + `AL-*` (process complaints) + info pack (`RULE`/`REL`/`CLM`) + vendor/funding links (`CON`/`TRF`) | prevent participation theatre; make influence auditable |
| an **oversight finding** | `OFR` + linked object IDs (`CON`/`ADS`/`PROG`/etc.) + response deadline | follow-through |
| an **information request / disclosure** | `FOI` + record class + (where safe) linked object IDs | transparency that can be used |


### Authorization links (avoid “orphan” objects)
Many failures happen when artifacts exist but the **authorizing decision** is not traceable (e.g., a contract award with no attributable decision, or a permit that can’t be appealed because the decision record is missing).

**Rule (two-way link):**
- the *object entry* (`CON`, `PAR`, `TRF`, `EMR`, etc.) SHOULD reference the authorizing **Decision ID** (`DRR`), and
- the **Decision Record/Receipt** (`DRR`) SHOULD reference the resulting object ID(s).

**Naming suggestion (interoperability):** on object register entries, store the authorizing decision receipt under a consistent field name such as `AUTH-DRR` (or `AUTH.DRR`) so audits and tooling can join across systems without bespoke mapping.

| Object created | Object ID type | Link to authorizing decision |
|---|---|---|
| contract award / concession | `CON` | `CON` ↔ `DRR` (award decision) |
| permit / licence / variance | `PAR` | `PAR` ↔ `DRR` (approval/denial) |
| discretionary grant / transfer | `TRF` | `TRF` ↔ `DRR` (award formula/exception) |
| emergency measure | `EMR` | `EMR` ↔ `DRR` (declaration/renewal) |
| asset creation/major works/maintenance deferral | `AST` | `AST` ↔ `DRR` (approval/deferral/transfer) |
| enforcement action / sanction | local type + `DRR` | action ↔ `DRR` (reasons + appeal lane) |

This keeps **remedy**, **audit**, and **learning** attached even when responsibility shifts across scopes.

### Reason codes (portable taxonomy; keeps decisions appealable across scopes)
Many systems fail because denials/sanctions are written as prose (“because policy”) or as siloed local categories that do not travel across institutions.

**Rule:** every rights-/resource-affecting **Decision Record/Receipt** (`DRR`) SHOULD include ≥1 **Reason Code** from this portable set (plus Rule IDs for the cited criteria).
Local systems MAY add detail, but MUST map to a portable code.

| Code | Meaning (portable) | Typical use |
|---|---|---|
| `RC-AUTH` | wrong authority / competence mismatch | “This unit cannot decide this.” |
| `RC-ELIG` | not eligible / no standing | “You don’t qualify under the rule.” |
| `RC-PROC` | procedural failure (missing info, late, wrong channel) | “Application incomplete/late.” |
| `RC-NOREC` | no record exists / not held | FOI: “No responsive records.” |
| `RC-DUP` | already public / previously released | FOI: “Already published; see link.” |
| `RC-CRIT` | substantive criteria not met | “Requirements under RULE-* not satisfied.” |
| `RC-EVID` | evidence insufficient / burden not met | “Insufficient proof to grant/deny.” |
| `RC-HARM` | unacceptable risk/harm (safety, environment, public health) | “Granting would create unacceptable risk.” |
| `RC-RGHT` | rights/equality constraint (cannot do this lawfully) | “Would violate protected rights.” |
| `RC-INTE` | integrity/fraud/conflict constraint | “Blocked due to integrity safeguards.” |
| `RC-PRIV` | privacy/confidentiality limit | FOI redaction/withholding; data minimization |
| `RC-SECU` | security/classified limit | FOI withholding; secure facility controls |
| `RC-COMM` | commercial secrecy / trade secret limit | FOI withholding; procurement confidentiality |
| `RC-INV` | investigation/enforcement integrity | FOI withholding; active investigation |
| `RC-CAPA` | capacity/feasibility/legal impossibility | “Cannot be done within constraints.” |
| `RC-EXCP` | exception/emergency invoked | MUST cite `EMR-*` + sunset/review |

**Local extensions:** add an optional local code (e.g., `RCX:<UNITID>:<slug>`) but ALWAYS include the nearest portable code above.

**FOI mapping:** local FOI/RTI exemption codes MAY vary, but refusals MUST include portable `RC-*` codes. Use `RC-PRIV`/`RC-SECU`/`RC-COMM`/`RC-INV` for withholdings, `RC-NOREC` when no responsive record exists, and `RC-DUP` when the record is already publicly available.

**Audit hook:** publish aggregate counts of Reason Codes for major decision classes (with privacy safeguards) to detect targeting, drift, or procedural denial-as-policy.


### Appeal lanes (portable taxonomy; makes remedies comparable)
People need to know *where to go next*, and systems need a small way to report and compare contestation outcomes across scopes.

**Rule:** every `DRR` SHOULD include ≥1 **Appeal Lane** code (`AL-*`) in escalation order (plus the specific institution/channel and time limits).
Local systems MAY add detail, but MUST map to a portable lane below.

| Code | Lane (portable) | Typical forum |
|---|---|---|
| `AL-FRONT` | informal fix / reconsideration | caseworker/front desk/hotline |
| `AL-LEG` | legibility complaint (missing required receipt/log) | ombuds / inspectorate / internal compliance desk |
| `AL-ADM` | administrative review | supervisor / internal appeals unit |
| `AL-OMB` | independent oversight review | ombuds / inspector general / audit office |
| `AL-TRI` | administrative tribunal | specialist tribunal / board |
| `AL-CRT` | courts | judicial review / constitutional court |
| `AL-ADR` | alternative dispute resolution | mediation/arbitration (voluntary; rights-safe) |
| `AL-INT` | supranational / international remedy | treaty body / regional court / complaints mechanism |

**Audit hook:** publish appeals volume/outcomes by `AL-*` lane and `RC-*` reason codes (with privacy safeguards) to detect denial-as-policy, bias, and bottlenecks.

### Appeal outcomes (portable taxonomy; makes contestation measurable)
Once a challenge is filed, systems still fail if outcomes are not classifiable (everything becomes prose) or if “wins” are hidden.

**Rule:** when a `DRR` represents the outcome of a challenge/review, it SHOULD include ≥1 **Appeal Outcome** code (`AO-*`), plus the lane used (`AL-*`) and a pointer to the original `DRR` being challenged.

| Code | Outcome (portable) | Meaning |
|---|---|---|
| `AO-UPHOLD` | upheld | original decision stands |
| `AO-REVERSE` | reversed | original decision overturned |
| `AO-REMAND` | remanded | sent back for reconsideration / further fact-finding |
| `AO-MOD` | modified | partially changed (benefit/condition/penalty adjusted) |
| `AO-SETTLE` | resolved by agreement | settlement/consent resolution (rights-safe) |
| `AO-WITHDRAW` | withdrawn | appellant withdraws (record why if feasible) |
| `AO-DISMISS` | dismissed (procedural) | out of time / no standing / wrong forum (`RC-*` SHOULD include the procedural reason) |
| `AO-NORESP` | no response / default | the forum fails to act in time (a system defect; triggers escalation) |

Local systems MAY add detail, but MUST map to one of the outcomes above.

### Register inventory (canonical names; keep the list short)
| Register | What it makes legible | Where specified |
|---|---|---|
| Competence ledger | who can decide what (and who can overrule) | `34-...` + `70-...` |
| PRR | the binding rules (with Rule IDs + versions) | `39-...` + overview (`25-...`) |
| PSR | governance-grade standards (pinned versions + tests) | `27-...` |
| PDRR | official datasets/series (Release IDs + methods + revisions) | `26-...` |
| Program Register + Evaluation Registry | what we’re doing and how we’ll learn | `28-...` |
| Compact Register | cross-scope agreements (compact discipline) | `19-...` |
| EMR | emergency declarations/measures/renewals | `45-emergency-measures-register.md` + overview (`23-...`) |
| DPR | personal-data processing inventory | `33-...` |
| ADS/MOD register | rights-affecting automation inventory | `42-...` + overview (`06-...`) |
| PAR | permits/licences/approvals + appealability | `29-...` |
| OFRR | oversight findings → responses → closure | `32-...` |
| FOI log | access-to-information requests + outcomes | `31-...` |
| Contract register | contracts/procurement awards (prefer OCDS/OCID when used) | `38-...` + integrity memo (`22-...`) |
| Transfer register | intergovernmental transfers (formulas + discretionary grants) | `35-...` + IGF design (`18-...`) |
| Influence & interests register | lobbying/meetings/gifts + interest declarations + recusals | `46-influence-and-interests-register.md` + integrity memo (`22-...`) |

**Anchors:** see [BIB-W3C-DWBP]; [BIB-UKGDS-REG]; [BIB-ODI-ID].

For oversight-specific tracking (findings → responses → closure), see `32-oversight-institutions-and-follow-through.md` (OFRR).

### Register conformance (linting + completeness tests)
This architecture fails silently if registers drift, joins break, or deadlines slip. Treat **conformance** as a first-class output.

**SHOULD (each major register):**
- publish a schema version and a basic validator (even if only as documentation + a reference JSON schema),
- run automated checks for: required fields present, ID uniqueness, crosswalk completeness, broken joins (`DRR`→`RULE`/`AL`/`REL`), and deadline misses (`AO-NORESP` share),
- publish a periodic conformance report as a small `REL-*` release, and open `OFR-*` cases for persistent noncompliance.

## 0f) Personal data interface (privacy + data sharing)
Personal data is a cross-scope risk surface: it enables targeting, exclusion, and surveillance if it becomes invisible. Treat personal-data processing as a joinable governance object.

**Minimum:**
- Maintain a **Public Data Processing Register (DPR)** with stable `DPR-*` IDs and change logs (conforms to `IOP-9`).
- DPR entries SHOULD link to **`RULE-*` IDs** (legal basis), retention class (`OPEN-9`), and (where relevant) `PROG-*` IDs and `ADS-*` IDs.
- Cross-scope/cross-border sharing MUST be filed as a compact/agreement with purpose, safeguards, auditability, and remedy (see `19-compacts-and-cooperative-governance.md`).
- `ADS-*` registers SHOULD reference `DPR-*` IDs for major inputs/outputs; undeclared expansion of processing counts as an incident (`DAG-4`).

**Privacy note:** DPR publication SHOULD avoid leaking sensitive details; exemptions are typed and logged (no ‘secret processing’—only redacted descriptions).

**Joinability vs reidentification:** where artifacts are public, avoid publishing globally joinable person identifiers. Prefer event/decision IDs (`DRR-*`, `ENF-*`) in public logs and keep person-linkage in protected layers with audited access (see `33-data-protection-and-personal-data-governance.md`).

See: `33-data-protection-and-personal-data-governance.md`.

**Anchors:** see [BIB-W3C-DWBP]; [BIB-UKGDS-REG]; [BIB-ODI-ID].

## 1) Escalation ladder (subsidiarity protocol)
A standard escalation template:
1. local attempt + documented rationale  
2. municipal coordination attempt  
3. regional compact / arbitration  
4. national review (rights, externalities, funding)  
5. supranational/global only when scale/effects demand it  

Higher levels MUST publish:
- scale/effects or rights justification,
- proportionality argument,
- sunset/review plan.

Subsidiarity/proportionality anchor: see [BIB-TEU-A5].


## 1b) Emergency interface (exception logging across scopes)
Emergencies are when multi-level systems fragment. Use one shared pattern:
- emergency declarations and renewals are **public records** with stable IDs
- exceptional measures are **typed and logged** (procurement, data, fiscal, coercion)
- emergency events MUST be legible in the competence ledger (who declared what, for where, with what powers)

**Rule:** a declaration is a **ledger event**—publish the Emergency Measures Register entry and link it from affected units.

### Emergency Measures Register (EMR)
**Canonical spec:** `45-emergency-measures-register.md`.

Minimal join rule: if an action relies on emergency authority, it MUST cite `EMR-*` (and still log the underlying object: `CON-*`, `DPR-*`, `ENF-*`, `TRF-*`, etc.).

## 2) Money interface (mandates ↔ revenue ↔ transfers)
- publish a cross-scope balance sheet: mandates, revenues, transfers, liabilities
- publish a **transfer register** and link it to the competence ledger (prevents “hidden government” and blame-shifting)
- transfers SHOULD be formula-based and predictable (`CAP-5`; see `18-intergovernmental-finance.md`)
- crisis funding SHOULD be trigger-based (disaster, unemployment, outbreak)
- off-book entities MUST be consolidated or disclosed (`CAP-2/3` discipline)


## 3) Ecological commons interface (OPEN-6)
Across boundaries (watersheds/airsheds/migration of harms), require:
- an explicit **ecological budget** object (metric, ceiling/floor, baseline, allocation rule, revision rule)
- shared registries (permits/emissions/discharges/protected areas) with stable IDs where feasible
- joint monitoring + shared enforcement clauses inside compacts (avoid “paper cooperation”)
- leakage controls (comparable measurement; no mutual recognition without auditability)
- dispute clause + emergency coordination protocol for acute ecological events (fires, floods, contamination)

Anchor set: see [BIB-SEEA-CF]; [BIB-UNECE-WATER]; [BIB-PARIS]; [BIB-CBD-GBF]; [BIB-UNGA-76300]; [BIB-AARHUS].
See also: `11-commons-and-ecological-governance.md`.

## 4) Data interface (schemas + privacy + audit logs)
- common schemas for budgets, procurement, and service performance
- integrity registers (interests/assets, lobbying/meetings, contract register) SHOULD use stable IDs and link to the competence ledger (see `22-public-integrity-and-procurement.md`)
- privacy-by-design: minimization, role-based access, audit logs
- procurement schema anchor: see [BIB-OCDS].

## 5) Identity & recognition interface (IOP-6)
- define the **minimum identity objects** used across scopes: person ID (where lawful), household/entity IDs, and document IDs
- publish rules for **status decisions** (citizenship/residency/eligibility) and their appeal paths (`LAW-5`)
- portability SHOULD include: benefits eligibility proofs, education/professional credentials, and civil-status extracts
- cross-border document authentication SHOULD prefer standard mechanisms (e.g., Apostille) over bespoke legalization
- digital credentials (if used) SHOULD be standards-based and auditable; avoid vendor-locked wallets
See: `12-identity-and-recognition.md`.

## 6) Coercion interface (force, detention, investigation)
- define who can detain/use force at each scope, under what standards (`SAFE-*`)
- mutual aid and cross-scope safety operations MUST follow MASIP (`24-mutual-aid-and-serious-incident-protocol.md`) (activation logs, command/authority, independent serious-incident pipeline).
- cross-border cooperation MUST include rights baselines and remedy paths (`LAW-5`, `LAW-2/3`; see `08-remedy-and-grievance.md`)

## 7) Mutual recognition interface (portability with minimum standards)
- default: recognize other jurisdictions’ licenses/credentials/judgments
- exceptions: minimum rights/safety/integrity standards not met (documented)
- build portability for benefits and educational/professional records
- **regulated markets/utilities:** recognition SHOULD require baseline rulemaking transparency + appeal rights (`CAP-7`, `LAW-5`) to avoid “race to the bottom” (see `13-regulation-utilities-and-soes.md`)
- regulators SHOULD use compacts for cooperation (shared standards, joint investigations, confidentiality rules, and dispute channels) (`IOP-1`)
### Compact record — minimum schema
| Field | Meaning |
|---|---|
| Compact ID | stable identifier from the compact register |
| Parties | who is bound (jurisdictions/authorities) |
| Scope | what decisions/resources are covered (and exclusions) |
| Legal basis | statute/charter authority + link to full text |
| Decision rule | voting/override rules; delegated roles |
| Contributions | funding / in-kind / data duties; residual risk |
| Transparency | meeting/votes/minutes + disclosure obligations |
| Accounts & audit | consolidation logic + audit cadence (`07-...`, `18-...`) |
| Performance | 3–10 measures + reporting cadence |
| Enforcement | graduated responses for non-compliance |
| Dispute + remedy | arbitration/tribunal + user remedy path (`08-...`) |
| Sunset / exit | review schedule + transition/continuity rules |

## 8) Compact interface (IOP-1)
Compacts MUST follow the Minimum Viable Compact (MVC) spec in `19-compacts-and-cooperative-governance.md`.

At minimum, a compact MUST include:
- scope + competence boundaries (and explicit exclusions)
- contributions + residual risk rules; no off-book money
- transparency + auditability obligations
- 3–10 measures + reporting cadence
- enforcement ladder + dispute path + user remedy path
- sunset/review + exit clause + continuity/transition plan
- filing in the **compact register** with a stable ID (so it can be linked in the competence ledger)

## 9) Intergovernmental dispute resolution
- standing arbitration / administrative court system for compact disputes, funding disputes, and competence conflicts
- clear escalation to constitutional courts at national/supranational levels (`LAW-2/3`)

## 10) Digital infrastructure interface (IOP-4)
Where shared digital systems exist (identity, registries, benefits):
- publish governance rules and auditability requirements
- avoid vendor lock-in via open standards and exit clauses
- treat core systems as public infrastructure, not merely IT

### Automated decision system register — minimum schema
When automated or semi-automated systems shape eligibility, enforcement, triage, or sanctions, publish:
| Field | Meaning |
|---|---|
| System name + owner | who operates it |
| Purpose + decision effect | what it is for and what it can change |
| Legal basis | statute/regulation/policy authority |
| Inputs | main data sources (with provenance) |
| Model / rule versioning | change logs and evaluation notes |
| Human review | how to get a human decision; deadlines |
| Reason codes | portable categories for explanations |
| Appeal path | where the remedy lives (`LAW-5`, `08-...`) |
| Auditability | access for authorized auditors; logs |

## 11) Automated decision interface (IOP-5)
When decisions cross boundaries (benefits portability, sanctions lists, eligibility determinations):
- require a shared **system register** field set (purpose, legal basis, versioning, appeal path)
- require portable **reason codes** and an explicit human-review escalation ladder
- prohibit “black box” mutual recognition in high-stakes contexts without auditability

## 12) Remedy interface (portable appeals)
When a decision touches multiple scopes (benefits portability, policing cooperation, mutual recognition, global listings):
- MUST: publish which body can **stop** the harm, which can **review**, and which can **enforce**
- MUST: a clear escalation ladder with deadlines and evidence-preservation rules
- SHOULD: shared reason-code taxonomy so appeals can travel across systems (`IOP-5`)
