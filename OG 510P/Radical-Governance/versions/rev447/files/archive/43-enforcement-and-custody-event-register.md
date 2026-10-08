# Enforcement & Custody Event Register (Joinable Coercion)

**Purpose:** make coercive events receiptable and reviewable (use‑of‑force, detention, custody) so harm can be traced and retaliation/chilling can be monitored (see [TM-29]).
**Person served:** a person subjected to enforcement contact or custody (and their family) who needs a receipt, traceable event log, and safe review paths.

**From-below:** This forces coercive encounters to leave joinable records so abuse can’t disappear into missing paperwork or vanished logs.
**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-05` (Fear) by requiring receipted enforcement events that remain contestable (`98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Join constraints:** coercion logs are high‑risk join surfaces: joins MUST be purpose‑limited to accountability/defense, avoid public person‑level join keys, and default to person‑held event receipts/reference numbers with protected disclosures for victims/witnesses (see `70`, `77`, `33`). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

**Authority:** enforcement actors must create `ENF-*` records; independent oversight + remedy lanes (`55`/`36`/`08`) must be able to compel correction where coercion harms. (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect complainants/witnesses via confidential channels + redaction discipline (`83`, `77`) and publish aggregate retaliation/chilling signals where needed; include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** for custody/enforcement events, the state bears the burden to maintain a complete evidentiary trail (time-stamps, authorizations, continuity); people can contest via `RC-*` + `AL-*` lanes using the register as-of (`31`, `36`, `52`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)


Coercive power becomes illegitimate when it is **unlogged**. This memo defines a minimal **Enforcement & Custody Event Register** so remedies, oversight, and learning can work across scopes without merging institutions.

**See also:** `05-public-safety-and-coercion.md` (constraints), `24-mutual-aid-and-serious-incident-protocol.md` (serious incidents), `36-appeal-lanes-and-redress-registry.md` (ALR), `31-records-foi-and-government-memory.md` (records), `70-interoperability.md` (IDs).

**Design goal:** every coercive contact produces (1) a person-facing **Decision Receipt** and (2) an auditable **event log**, with privacy discipline.

Anchors: [BIB-UN-UOF]; [BIB-UN-LEO-CODE]; [BIB-MANDELA-RULES]; [BIB-ISTANBUL-PROTOCOL].

---

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- **Coercion constraints:** `05-public-safety-and-coercion.md` (receipts; limits; audits).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (fear/retaliation; language; no wrong door).
- **Remedy lanes:** `08-remedy-and-grievance.md`, ALR `36-...` (effective relief for coercive events).
- **Records + publication integrity:** `31-...`, `53-...` (tamper-evident logging where stakes are highest).
- **Secrecy discipline:** `77-...` (withholding receipts; safety exceptions, not dark zones).

## Named tensions (design must surface these)
- **Officer safety vs accountability:** safety matters; “security” cannot erase the audit spine.
- **Deterrence vs rights:** enforcement goals do not justify unlogged coercion or indefinite delay.
- **Legibility vs retaliation:** witnesses/complainants need protection; publish aggregates + protected channels where needed (see [TM-29]).
- **Data detail vs privacy:** log enough to contest; minimize exposure and secondary uses (`99`).

## 1) Non-negotiables (always-on)
- **No dark enforcement:** any action that affects liberty/property/bodily integrity MUST generate an `ENF-*` event record.
- **Receipt:** the subject MUST get a one-screen **Decision Receipt** (a `DRR`-linked receipt) with `ENF-*`, legal basis, and appeal lane—unless a documented safety exception applies.
- **Representation duty under coercion:** when the subject cannot effectively contest (minors, people under custody/control, severe disability), the receipt MUST specify the representative/advocate/attorney channel and the fastest protective lane (`AL-*`), and the system SHOULD provide an independent advocate intake path.
- **Verifiable receipt code (anti‑dark enforcement):** the receipt SHOULD include a **non‑guessable verification code** (QR/short code) that lets the holder confirm the record exists (and retrieve the redacted receipt + `AL-*` lane) via a rate‑limited “receipt verification” endpoint. The endpoint MUST not allow enumeration (possession‑based check only). See `31-records-foi-and-government-memory.md` (publication integrity).
- **Sampling audits (anti-bias / anti-evasion):** for high-volume enforcement logs (e.g., bodycam review, stop/search documentation, custody welfare checks), the oversight/QA program SHOULD publish a **sampling policy** (risk + random component) and log selections as part of the verification regime (see `81-verification-inspection-and-compliance-ladders.md`; metric hook `[IPM-25]`).
- **Rule basis:** `ENF` records MUST cite `RULE-*` **version/as-of** (and `DRR-*` when a warrant/order/authorization exists).
- **Custody safety:** any custody episode MUST be logged **start→end** with welfare/medical checkpoints.
- **Serious incidents:** must trigger independent pipeline (see `24-...`) and link to the resulting `OFR-*` finding(s) / response(s).

---

## 2) What gets an `ENF-*` ID (minimum set)
If a person would reasonably say “the state used power on me,” it’s in-scope.

**Minimum event types**
- Stop / questioning / identity check (including traffic stops)
- Search (person/vehicle/home) and warrant execution
- Seizure / confiscation / property taking
- Citation / fine / administrative sanction issuance (when delivered by an enforcement actor)
- Arrest / detention start; detention end / release
- Transfer between custody facilities or agencies
- Use-of-force event (including restraint, weapons display/use, chemical agents, taser, firearms discharge)
- Medical emergency in custody; in-custody death
- Forced entry / forced removal (including high-stakes “civil” enforcement: immigration, child welfare removal, mental health holds)

**Scope note:** this covers *all* coercive units, not only police (e.g., border, corrections, bailiffs, inspectors with seizure powers).

---

## 3) Public vs protected layers (privacy without impunity)
The register is **two-layer**:

1) **Protected operational log** (full fidelity)
- contains PII, full evidence pointers, and staff identifiers.
- access-controlled with audit logs; purpose limitation; retention rules.

2) **Public release** (de-identified, joinable)
- publishes a de-identified `ENF` ledger + aggregates, with revision logs (`REL-*`).
- precision tiers for location/time to reduce re-identification.
- publishes disclosure/refusal counts (FOI) with typed exemptions (see `31-...`).

---

## 4) `ENF` register entry — minimum schema
| Field | Meaning |
|---|---|
| ENF ID | stable join-key (`UNITID-ENF-####`) |
| Owning unit + agency | competence-ledger Unit ID + org |
| Event type | from a small local taxonomy; publish the taxonomy |
| Start/end time | with time precision tier if needed |
| Location | with precision tier (point/segment/area) |
| Subjects | count; optional pseudonymous subject token for longitudinal disparity analysis |
| Staff | protected identifiers; public may use pseudonymous staff tokens for accountability analysis (risk-tiered) |
| Legal basis | cited `RULE-*` (version/as-of); include `DRR-*` if warrant/order exists |
| Reason codes | `RC-*` (see `52-reason-codes-registry.md`) + short narrative |
| Receipt link | the `DRR-*` / receipt ID provided to the subject |
| Receipt verification | non‑guessable verification code (QR/short code) for possession‑based existence check + redacted receipt retrieval |
| Appeal lane | `AL-*` from ALR (`36-...`) for complaints/review |
| Force / restraint | coded level + tools used + resistance indicator |
| Injury / medical | injury flag + medical referral/hospitalization + in-custody death flag |
| Evidence pointers | bodycam/dashcam/CCTV IDs + chain-of-custody pointers (protected); public release may publish existence/retention windows |
| Custody link | if relevant, link to custody episode `ENF-*` (see §5) |
| Related links | `EMR-*` (if emergency), `CMP-*` (mutual aid compact), MAAL `DRR-*` (aid activation, when applicable), `CON-*` (if vendor equipment), `ADS-*`/`MOD-*` (if automation materially shaped enforcement) |
| Privacy tier | what is public vs protected and why |
| Change log | corrections + reason + authority |

---

## 5) Custody episode (minimum fields)
A custody episode SHOULD be represented as an `ENF-*` record of type `CUSTODY_EPISODE`, with linked sub-events (booking, transfer, welfare check, release).

**Minimum additional fields**
- **Basis + authority:** `RULE-*`/`DRR-*` for detention authority; time limits.
- **Facility:** facility identifier; transfers with timestamps.
- **Welfare checks:** intervals + flags for missed checks.
- **Medical screening:** completed Y/N; urgent care Y/N; medications continuity flag.
- **Restrictions:** isolation/segregation flags; restraints duration flags.
- **Notifications:** next-of-kin/attorney notification timestamps where applicable.

---

## 6) Interfaces (how this plugs into the archive)
- **DRR receipts:** any coercive contact that issues a receipt MUST include `ENF-*` (and the `ENF` MUST link back to `DRR-*`). See `31-...`, `08-...`.
- **Appeal lanes:** ALR publishes the lane(s) for each enforcement class; `ENF` records include the `AL-*` used for complaint/review. See `36-...`.
- **Serious incident protocol:** serious incidents link `ENF-*` → independent case pipeline (`OFR-*` opened within 24h; `OFR-KIND: CASE`) → findings and resulting `DRR` responses; if the event occurred under mutual aid, link the MAAL `DRR-*` as well. See `24-...`, `32-...`.
- **Records/FOI:** `ENF` is an official record class; exemptions are typed and logged; public releases use `REL-*`. See `31-...`, `26-...`.

---

## 7) Minimal metric hooks

**Omission / selective-enforcement visibility:** publish periodic `REL-*` coverage snapshots keyed by `RULE-*` and geography (counts/rates; include *zero-event* flags) so patterns of non‑enforcement or “enforcement only against convenient targets” are legible (see [TM-30]). (See `101-claude-rev142-normative-requirements.md` (NR-02).)
- **[LRR-4] Time-to-remedy:** include enforcement/custody complaints.
- **[SAFE-2] Serious-incident follow-through:** link incidents → findings → corrective action.
- **[IPM-17] Logged coercion coverage (dark enforcement test):** see `03-metrics-and-evidence.md`.
- **[IPM-25] Verification sampling coverage:** share of enforcement events subject to independent QA/oversight sampling (risk + random) and disparity checks; see `81-...` and `03-...`.
