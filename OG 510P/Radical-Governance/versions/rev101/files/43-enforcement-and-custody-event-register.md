# Enforcement & Custody Event Register (Joinable Coercion)

Coercive power becomes illegitimate when it is **unlogged**. This memo defines a minimal **Enforcement & Custody Event Register** so remedies, oversight, and learning can work across scopes without merging institutions.

**See also:** `05-public-safety-and-coercion.md` (constraints), `24-mutual-aid-and-serious-incident-protocol.md` (serious incidents), `36-appeal-lanes-and-redress-registry.md` (ALR), `31-records-foi-and-government-memory.md` (records), `70-interoperability.md` (IDs).

**Design goal:** every coercive contact produces (1) a person-facing **Decision Receipt** and (2) an auditable **event log**, with privacy discipline.

Anchors: [BIB-UN-UOF]; [BIB-UN-LEO-CODE]; [BIB-MANDELA-RULES]; [BIB-ISTANBUL-PROTOCOL].

---

## 1) Non-negotiables (always-on)
- **No dark enforcement:** any action that affects liberty/property/bodily integrity MUST generate an `ENF-*` event record.
- **Receipt:** the subject MUST get a one-screen **Decision Receipt** (a `DRR`-linked receipt) with `ENF-*`, legal basis, and appeal lane—unless a documented safety exception applies.
- **Verifiable receipt code (anti‑dark enforcement):** the receipt SHOULD include a **non‑guessable verification code** (QR/short code) that lets the holder confirm the record exists (and retrieve the redacted receipt + `AL-*` lane) via a rate‑limited “receipt verification” endpoint. The endpoint MUST not allow enumeration (possession‑based check only). See `31-records-foi-and-government-memory.md` (publication integrity).
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
| Reason codes | `RC-*` (portable where possible) + short narrative |
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
- **[LRR-4] Time-to-remedy:** include enforcement/custody complaints.
- **[SAFE-2] Serious-incident follow-through:** link incidents → findings → corrective action.
- **[IPM-17] Logged coercion coverage (dark enforcement test):** see `03-metrics-and-evidence.md`.
