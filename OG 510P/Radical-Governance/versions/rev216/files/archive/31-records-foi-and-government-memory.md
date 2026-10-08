# Records, FOI, and Government Memory

**Purpose:** ensure the governed can obtain the records needed to contest decisions, and that public memory remains durable under capture, crisis, or collapse.

Governance becomes “dark matter” when decisions and evidence exist only inside inboxes, chats, or discretionary files. This memo defines a **Minimum Viable Records & Access System (MVRAS)**: the smallest set of rules and institutions that make *transparency, remedy, and learning* feasible at any scope.

**Why records matter:** records are an obligation to the living and the dead—without durable, queryable decision memory, abuse becomes deniable, reparations become impossible, and future governance cannot learn.

**Posthumous access/correction note:** record systems SHOULD define lawful access and correction paths for estates/representatives where needed for reparations, truth‑finding, or ongoing rights (balanced against privacy/safety and documented as a reviewable rule).

**Core idea:** *FOI is not a front desk; it is a byproduct of recordkeeping.*

## Kernel anchors (do not repeat)
- Person-facing comprehension + non-reading access: `98-persons-path-and-accessibility-invariants.md`.
- Remedy/appeal joins for FOI denials and decision challenges: `08-...`, `36-...`.
- Release registry (proactive disclosure) and publication integrity: `51-...`, `53-...`.
- Join-key/version semantics (“as-of” access; correction propagation): `70-...`.
- Protective legibility + adoption dynamics (records are politically resisted; design for uneven compliance): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Transparency/learning vs retaliation, doxxing, and operational/security risk.
- Joinability/auditability vs comprehension and low-literacy/non-reading reality.
- Retention for accountability vs minimization/privacy (harmful permanence).
- Centralized record power vs plural custody/resilience (capture vs fragmentation).

---


## 1) What this primitive covers
- **Official record** definition + capture rules (what must be recorded; where it lives).
- **Retention & disposition** discipline (keep what matters; delete what can safely go).
- **Access pipeline** (FOI / RTI requests + proactive disclosure + appeals).
- **Archives** (long-term memory with access rules and declassification discipline).

## 2) Failure modes (what to design against)
- **Ephemeral governance:** decisions in private messaging; no minutes; no reasons; no trace.
- **Selective recording:** “shadow files” and discretionary note-taking; inconsistent retention.
- **Slow denial:** backlog as censorship (requests technically allowed, practically impossible).
- **Over-classification / over-redaction:** secrecy becomes the default; exemptions aren’t reviewable (see `77-sensitive-information-and-secrecy-governance.md`).
- **Disposal risk:** premature deletion, “clean desk” purges, or unmanaged cloud retention.
- **Disclosure without legibility:** dumps without IDs/methods/versioning (can’t be used to contest or learn).

## 3) Minimum Viable Records & Access System (MVRAS)

### A) Define “official record” (and enforce capture)
**MUST**
- define official records to include: **decisions + reasons**, mandates used (Rule IDs where possible), minutes, procurement artifacts, enforcement actions (`ENF-*` event logs + custody episodes), emergency measures, participation/deliberation processes (register entries + outputs), program/evaluation artifacts, and the core registers defined in this archive.
- treat records created/held by **contractors performing public functions** as in-scope for capture/retention and (where lawful) access — procurement MUST not be used to launder power into non-disclosable systems (see also [BIB-HUP-GOVBYCONTRACT-2009] and the CLC pack in `38-...`).
- require a **Decision Record** (`DRR`) for rights-affecting or resource-allocating actions (and a one-screen **Decision Receipt** when the decision affects a person/entity; see the receipt table below and `08-remedy-and-grievance.md` for remedy-stack design).

#### Decision Record (`DRR`) — minimum schema
| Field | Meaning |
|---|---|
| DRR ID | stable Decision ID (join-key) |
| Kind | `DEC` (initial decision), `REVIEW` (review outcome), or `NOTICE`/`REFUSAL` (procedural & access decisions) |
| DRR Type (optional) | use when useful to classify: `SCOPE` (mandate assignment/transfer), `COMPETENCE` (boundary/overlap ruling), `AID` (mutual aid activation), `DELEGATION` (acting/delegated authority receipts); keep the set small |
| Issuing unit | Unit ID / body |
| Decision date + effective date | when decided; when it takes effect |
| Decision class + outcome | permit/benefit/sanction/FOI appeal/etc + result; for reviews include `AO-*` |
| Legal basis | cited `RULE-*` IDs **+ version/as-of pointer** (and competence-ledger entry where relevant) |
| Reasons | short narrative + portable `RC-*` code(s) (see `52-reason-codes-registry.md`) |
| Evidence links | record references and/or `REL-*` Release IDs (see `51-release-registry.md`) (if applicable) |
| Remedy path | `AL-*` lane(s) (see ALR `36-...`) in order + forum + time limits + interim protection rules (and any filing cost/assistance where published) |
| Links | related object IDs (`PAR`/`CON`/`TRF`/`EMR`/`ADS`/`ENG`/`IDN`/`SRV`/`INF`/`INT`/etc); for `REVIEW`, link the challenged `DRR` |

#### Decision Receipt (person-facing) — minimum fields (one screen)

A Decision Receipt is the **human-readable view** of a `DRR` for the affected person/entity. It exists so someone can answer: *what happened, under what rule, why, and how to contest it.*

**Comprehensibility is load-bearing:** the receipt MUST be understandable to the affected person in the language and format they can actually use (plain speech, translation/interpretation where needed, disability-accessible presentation). A technically complete but incomprehensible receipt is an audit artifact, not a contestation artifact.

When literacy is a barrier, the one‑screen block MUST have a non‑reading equivalent (oral explanation at issuance, plus an audio/pictogram summary the person can replay later), and MUST NOT require portal reading to learn deadlines or next steps (see `98-persons-path-and-accessibility-invariants.md`).

#### DRR taxonomy maintenance rule (keep `DRR-*` from becoming a god object)

`DRR-KIND`/`DRR-TYPE` enumerations MUST remain **small and stable**. When `DRR-TYPE` exceeds ~15 values **or** different types require materially different minimum fields, graduate the divergent type into its **own ID family** (while keeping a `DRR-*` cross‑reference for backward compatibility and keeping person‑facing receipts unchanged). Treat this as a deprecation/refactor decision under `96-archive-governance.md`.



| Field | Meaning |
|---|---|
| Decision ID | stable `DRR` identifier (join-key) |
| Issuing unit | Unit ID/agency + contact channel |
| What happened | decision/outcome summary (plain language) |
| Why | short reasons summary + cited `RULE-*` IDs (legal basis, as-of) |
| Reason code(s) | ≥1 portable `RC-*` code(s) (see `52-reason-codes-registry.md`) |
| Evidence used (if applicable) | linked `REL-*` (see `51-release-registry.md`) or record references |
| Service context (if applicable) | cite `SRV-*` if the decision occurred within a defined service/benefit workflow |
| Identity gate (if applicable) | cite `IDN-*` if identity/credential proofing materially shaped the outcome |
| Effective date | when it applies; any deadlines triggered |
| How to challenge | appeal lane(s) `AL-*` + time limit + how to file (**what to submit / what to say**, any fee/cost, and whether assistance is available) |
| Interim protection | if available: stay/urgent review trigger |
| Review results (when applicable) | include `AO-*` outcome code(s) + link to challenged `DRR` |
| Receipt verification (recommended) | non-guessable code (QR/short code) for possession-based existence check + redacted receipt retrieval (no enumeration) |

**Design rule:** the receipt MAY redact personal/sensitive details, but MUST still publish: issuing `Unit ID`, dates, decision type, relevant `RULE-*`/`REL-*` joins, ≥1 `RC-*`, and ≥1 `AL-*`.

**Missing-doc denial rule:** if the decision is adverse due to missing documentation, the receipt MUST list what is missing, the resubmission deadline, where/how to obtain acceptable alternatives, and whether the state could have obtained the item itself (with consent).

**Comprehension test (minimum):** a receipt is compliant only if a person with primary‑school literacy, reading it in their own language (or via a non‑reading modality), can answer: (1) What was decided? (2) Why? (3) What can I do next, and by when? If it fails, the format MUST be revised (not merely appended).

**Correction propagation note:** when a receipt records a correction of a joinable record used by other systems (identity/eligibility/status), it SHOULD list downstream systems notified and their acknowledgment status (or a pointer to where that status can be checked) so people aren’t told “fixed” while harms persist (see `70-interoperability.md`). For high‑stakes corrections, the receipt SHOULD also state the **interim protection** status while downstream systems update (so “fixed” does not mean “still harmed”).

**Taxonomy maintenance:** if you add a new `DRR-Type`, `RC-*`, `AO-*`, or other portable code, you MUST:
- add it to its registry “home” memo (e.g., `52-reason-codes-registry.md`),
- avoid ambiguous residual categories (“Other”) unless paired with a review trigger,
- and include a deprecation/mapping note rather than renaming in place.

**Version semantics invariant:** joinable artifacts that cite rules or obligations MUST support point‑in‑time retrieval (“as‑of date X, show the version in force”). See `39-rulebook-and-instruments-registry.md`, `70-interoperability.md`, and `99-protective-legibility-and-adoption-dynamics.md`.

**Note:** scope assignment / mandate transfer decisions SHOULD be issued as a `DRR` with `DRR-TYPE: SCOPE`, linking the competence-ledger change (old → new) and the remedy continuity plan (see `IOP-10` in `02-design-toolkit.md` and `70-interoperability.md`).

**Note:** delegations/acting appointments/revocations SHOULD be issued as `DRR-TYPE: DELEGATION` and linked from the affected Unit ID’s authority schedule pointer (see `78-delegation-and-acting-authority-discipline.md`).

#### `DRR-TYPE: SCOPE` skeleton (one screen; mandate assignment / transfer)
```yaml
DRR-ID: DRR-____
DRR-KIND: DEC
DRR-TYPE: SCOPE
ISSUING-UNIT: UNIT-____
DECISION-DATE: YYYY-MM-DD
EFFECTIVE-DATE: YYYY-MM-DD
CHANGE: (new authority | mandate transfer | boundary adjustment | delegated compact power)
FROM: (old unit + competence-ledger version)
TO: (new unit + competence-ledger version)
SCOPE-TESTS: {local_knowledge: Y/N, spillovers: Y/N, scale: Y/N, rights_risk: Y/N, enforceability: Y/N}
# (preferred) attach the one-screen scope-test docket from `54-subsidiarity-and-scope-assignment-test.md`.
FUNDING-ALIGNMENT: (who pays; transfers; residual risk; liabilities)
REMEDY-CONTINUITY: (appeal forums during/after transition; standing rules)
REVIEW: (date/trigger; sunset rule if applicable)
LINKS: [RULE-… , CMP-… , TRF-… , EMR-…]  # only what applies
```

#### `DRR-TYPE: COMPETENCE` skeleton (one screen; overlap/gap ruling)
```yaml
DRR-ID: DRR-____
DRR-KIND: DEC
DRR-TYPE: COMPETENCE
ISSUING-UNIT: UNIT-____   # the forum issuing the ruling
DECISION-DATE: YYYY-MM-DD
EFFECTIVE-DATE: YYYY-MM-DD
CONTESTED: {units: [UNIT-____, UNIT-____], mandates: [COFOG/other tags or short list]}
INTERIM: {standstill: Y/N, emergency_override: EMR-____}
RULING: {owns_decision: UNIT-____, must_act: UNIT-____, provides_remedy: UNIT-____}
LEDGER-UPDATE: (old competence-ledger version → new version; transition plan)
REMEDY-CONTINUITY: (appeal forums/time limits; standing during transition)
LINKS: [RULE-… , CMP-… , TRF-… , EMR-…]  # only what applies
```


#### Decision Receipt / Record (`DRR-*`) — minimal public schema (portable)

A `DRR` is the **joinable receipt** for any rights-affecting or resource-allocating decision (and for any review of such a decision).
It exists so people can answer: **what happened, under what rule, why, and how to contest it**.

**Rule:** the public `DRR` MAY redact personal/sensitive details, but MUST still publish: issuing `Unit ID`, dates, decision type,
the relevant `RULE-*` / `REL-*` / register joins, a short reasons summary + ≥1 `RC-*`, and ≥1 `AL-*`.

```yaml
DRR-ID: DRR-____
DRR-KIND: DEC | REVIEW | REFUSAL | NOTICE
DRR-TYPE: (small local type; map to portable categories in `70-...`)
ISSUING-UNIT: UNIT-____
DECISION-DATE: YYYY-MM-DD
EFFECTIVE-DATE: YYYY-MM-DD

SUBJECT: "one-line description"
AFFECTS:
  SRV: [SRV-____]        # if a service workflow is involved
  RULE: [RULE-____]      # cited rule(s) / instrument(s)
  REL: [REL-____]        # cited releases / official facts (if any)
  TRF: [TRF-____]        # if transfer/conditionality applies
  CMP: [CMP-____]        # if a compact binds the decision
  CON: [CON-____]        # if procurement/contract is involved (or OCID)
  ENF: [ENF-____]        # if enforcement/custody event(s) apply
  EMR: [EMR-____]        # if emergency exception/measures apply
  OFR: [OFR-____]        # if tied to an oversight file (case/finding)

LEGAL-BASIS: ["short citation(s) to statute/regulation/instrument or RULE-*"]

REASONS:
  SUMMARY: "plain-language why (≤5 bullets)"
  RC: [RC-____]          # portable reason code(s), see `70-...`

REMEDY:
  AL: [AL-____]          # where to contest / seek urgent protection
  TIME-LIMIT: "e.g., 30 days from notice"

REVIEW:                  # only when DRR-KIND: REVIEW
  TARGET-DRR: DRR-____
  AO: [AO-____]          # portable appeal outcome code(s), see `70-...`

PUBLICATION:
  DISCLOSED: Y/N
  REDACTIONS: "typed grounds (privacy/safety/etc), counts only"
  CONFIDENTIALITY-BASIS: ["typed grounds or legal code"]
```

Notes:
- Local systems MAY add fields, but SHOULD keep the portable joins intact.
- For FOI/RTI requests, use `FOI-*` as the request ID and log the decision as a `DRR-KIND: REFUSAL|NOTICE` when denying or heavily redacting.

- require **official channels** for official business (email/chat/workflow) with automatic retention/capture; prohibit “official-only in private channels” (or require automated journaling into the record system).

**SHOULD**
- publish a short “what we record” statement for residents/users (reduces conflict and gaming).

### B) Retention, disposition, and legal holds
**MUST**
- adopt a **retention schedule** by record class (e.g., budget, procurement, licensing, safety, environmental, land-use, HR, casework).
- maintain **legal holds** (litigation/inquiry hold blocks disposal).
- log destruction/disposition events (what, when, authority) and audit them annually.

**SHOULD**
- transfer historically significant material to an archive on a set cadence (e.g., annually/biannually), with a published accession log.

### C) Access pipeline: FOI / RTI that can’t be stalled indefinitely
**MUST**
- publish request intake channels and time bounds; provide a **Request ID** and status tracking; include at least one **non‑digital** channel and allow **assisted/oral** filing with interpretation/translation where needed (see `98-persons-path-and-accessibility-invariants.md`).
- use typed exemptions with reasons; keep an internal **redaction log**.
- provide **internal review** + independent appeal path (court/commission/ombuds) with time bounds.
- maintain a public **disclosure log**: released records indexed by Request ID and (where safe) record class + date.
- when denying or heavily redacting, publish a **refusal record** in the disclosure log: Request ID, exemption code(s) (if used), **Reason Code(s)** (`RC-*`), record class/date range, items/pages withheld (counts only), and appeal lane (`AL-*`) + time limit (without leaking sensitive content). Use `RC-NOREC` when no responsive record exists, and `RC-DUP` when the record is already publicly available.
- when an FOI appeal/review is decided, log the outcome as a `DRR` (review result) and include `AO-*` + `AL-*` + the original Request ID (`FOI-*`) so denial patterns are measurable.
- for records held in vendor systems, require contracts to support timely search/production under the same tracking and deadline discipline (or explicitly publish the lawful limit where such access is not available).
- Where a request concerns **personal data about the requester**, route it through the subject access/correction channel with time bounds and appeal; log the outcome and (where feasible) reference relevant `DPR-*` IDs (see `33-data-protection-and-personal-data-governance.md`).

#### Minimal public FOI log entry (publishable)

This is the minimum joinable surface for an FOI/RTI request (`FOI-*`). The *decision* is logged as a `DRR` (often `DRR-KIND: REFUSAL|NOTICE`), but the request itself also needs a stable record so backlog, delays, and outcomes can be measured.

```yaml
FOI-ID: FOI-____
SUBMITTED: YYYY-MM-DD
REQUESTER: (resident | journalist | org | anonymous | other)   # coarse category only
SCOPE:
  RECORD-CLASS: (budget | procurement | permitting | enforcement | environment | other)
  DATE-RANGE: (start..end)
  DESCRIPTION: ...          # brief; do not leak sensitive info
STATUS: (OPEN | IN-REVIEW | PARTIAL | CLOSED)
DUE-DATE: YYYY-MM-DD
EXTENSION: (none | reason + new_due_date)
DECISIONS:
  - DRR: DRR-____      # the refusal/notice/release decision receipt
    RC: [RC-____, ...]      # portable reason codes (when refusing/withholding)
    AL: [AL-____, ...]      # appeal lanes for this request
DISCLOSURE:
  RELEASED: (Y/N)
  REL: [REL-____, ...]      # if the response creates/updates a public release
  LINK: (catalog pointer)   # disclosure log pointer
```

**SHOULD**
- adopt a “proactive disclosure trigger”: repeat requests → publish by default (reduces load).
- publish common datasets as **Release IDs** with methods + revision logs (`26-...`), rather than ad hoc attachments.

### D) Classification / confidentiality discipline

**MUST**
- treat withholding/classification as a **decision**: issue a `DRR-KIND: REFUSAL` (or FOI refusal `DRR`) that cites the legal basis/exemption, provides a non-sensitive reasons summary + `RC-*`, and names the appeal lane(s) `AL-*`.
- publish **existence metadata** even when content is withheld: record class, date range, holding unit, and counts/pages/items withheld (no content), so denial patterns are measurable.
- apply a **least-restrictive** rule: partial release / delayed release / summarized release preferred over full denial; distinguish privacy vs national security vs commercial confidentiality; and prohibit “confidentiality by contract” that blocks lawful audit/oversight (see the CLC pack in `38-...`).
- time-bound secrecy: each withholding decision records a **review-by date** and (where possible) a declassification/sunset rule; missed review deadlines are logged as `AO-NORESP` via the relevant lane’s review-result `DRR` (see `36-...`, [TM-23]).
- independent contestation: denial/withholding is reviewable by an independent body that can inspect withheld material (in camera) and order disclosure/redaction revisions where lawful; publish de-identified summaries of review outcomes.

**SHOULD**
- publish a periodic **withholding report** (counts by exemption + unit + age; reversal rate) as a `REL-*` release with methods and revision logs (see `26-...`).
- reserve the most restrictive secrecy for narrow categories; require senior sign-off and post-hoc disclosure when the risk expires.

**Anchors:** see [BIB-COE-TROMSO] and the “Tshwane Principles” / Johannesburg Principles on national security exceptions and public-interest disclosures ([BIB-TSHWANE-2013], [BIB-JOHANNESBURG-1995]).

### E) Archives and “government memory”
**MUST**
- ensure archival custody for high-stakes categories (rights, safety, land, environment, public money) with continuity across reorganizations/boundary changes (`17-...`).
- publish access rules; track restrictions and their expiry.

**SHOULD**
- provide a process for individuals to know whether they appear in archives and to append a statement contesting accuracy (where relevant).



### F) Publication integrity (tamper‑evidence + persistence)
Transparency fails if public artifacts can be **silently altered, backdated, or “lost”**. For high-stakes records (registers, `DRR`, `REL`), add a small integrity layer:

**MUST**
- publish registers and releases with **stable IDs + “as‑of” access** (older versions remain retrievable; use tombstones rather than deletion).
- publish a **change log** for each public feed (what changed, when, and why).
- treat “missing public artifacts” as a compliance issue: absence must be contestable (see `32-...` legibility-gap audits).
- for person‑facing receipts (`DRR` / coercion receipts that cite `ENF-*`), provide a **possession‑based receipt verification** endpoint (enter/scan the receipt code → confirm existence + issuing unit + date + `AL-*` lane; no enumeration). Failed verification is a legibility incident (`AL-LEG`).

**SHOULD (strongly)**
- ship each update with a **hash/checksum manifest** (file list + cryptographic hashes) and a **signature** by the publishing unit (or equivalent attestation) (pattern: `53-publication-integrity-and-tamper-evident-logs.md`).
- maintain ≥2 independent **mirrors** (e.g., national archive + civil-society mirror) and publish mirror pointers.
- for “constitutional” registers (competence ledger, PRR, EMR, OFRR (`55-...`), core enforcement logs), use an **append‑only transparency log** pattern so third parties can audit “nothing was changed or deleted since time T” (see `53-publication-integrity-and-tamper-evident-logs.md`; anchors: [BIB-RFC6962], [BIB-TRILLIAN]).

**Note:** cryptography does not prevent a lawful authority from changing a rule or record; it prevents **silent** change and enables audit and contestation.


## 4) Interfaces (how this plugs into the rest of the archive)
- **Register discipline:** core registers follow `IOP-9` (stable IDs + change logs) (`70-...`).
- **Rule legibility:** decisions cite Rule IDs (`25-...`).
- **Evidence legibility:** published data uses `REL-*` releases with revision logs (`51-release-registry.md`) and epistemic integrity rules (`26-epistemic-infrastructure-and-public-knowledge.md`).
- **Program legibility:** major programs have `PROG-*`/`EVAL-*` IDs (`28-...`).
- **Emergency + exceptions:** declarations and derogations are logged in the EMR (`23-...`).
- **Enforcement/custody logs:** coercive actions produce receipts + joinable `ENF-*` event logs (and custody episodes) (`43-...`, `05-...`, `24-...`).
- **Permits/approvals:** Permit/Approval Register (PAR) entries are retrievable and appealable (`29-...`).

## 5) Minimal metrics (use existing pack IDs)
- **[LRR-3] Petition/complaint throughput:** include FOI request intake + resolution time.
- **[LRR-4] Time-to-remedy:** include FOI appeals and denials-to-reversal timelines.
- **[LRR-8] Decision transparency coverage:** share of rights-affecting decisions with published reasons + `RC-*` + `AL-*` (and FOI refusal records typed and logged).
- **[IPM-1] Open publication coverage:** spend/awards + key disclosures published with stable IDs (timeliness/completeness).

## 6) Anchors (high-trust starting points)
- OECD Recommendation on Open Government (2017): see [BIB-OECD-OG].
- Council of Europe Convention on Access to Official Documents (Tromsø Convention): see [BIB-COE-TROMSO].
- Records management baseline: see [BIB-ISO-15489-1] (note: ISO text may be paywalled).
- Archives access baseline: see [BIB-ICA-ACCESS-2012].