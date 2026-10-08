# Epistemic Infrastructure & Public Knowledge (Seeing Reality, Updating Honestly)

**Purpose:** build public knowledge infrastructure so claims about reality are auditable without requiring insider access.

When institutions can’t produce **shared facts** (or can’t correct them), governance collapses into narrative conflict, capture, and exception regimes.

This memo turns `OPEN-4/5` into a compact **Minimum Viable Epistemic Infrastructure (MVEI)** that can plug into the ledger/register stack.

**Anchor set (high-trust):**
- UN Fundamental Principles of Official Statistics (UNFPOS): see [BIB-UNFPOS].
- OECD Recommendation on Good Statistical Practice (OECD/LEGAL/0417): see [BIB-OECD-GSP].
- OECD Open Government Recommendation (OECD/LEGAL/0438): see [BIB-OECD-OG].
- Content provenance / Content Credentials (C2PA): see [BIB-C2PA-2-3].

## Kernel anchors (do not repeat)
- Records + revision discipline (no silent overwrites): `31-records-foi-and-government-memory.md`, `53-publication-integrity-and-tamper-evident-logs.md`.
- Evidence releases should be joinable to decisions without doxxing: `51-release-registry.md`, `99-protective-legibility-and-adoption-dynamics.md`.
- Person-facing usability (plain-language, non-reading modalities where needed): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- **Truth-seeking vs pluralism:** epistemic institutions must be contestable without collapsing into “anything goes.”
- **Openness vs safety:** public knowledge can endanger people; publish methods/aggregates when raw data is dangerous.
- **Rigor vs speed:** crisis requires fast signals; legitimacy requires revision logs and error admission.


---

## A. What this system must do (minimal promise)
1) **Publish baseline reality** (with methods + uncertainty) on the main domains: people, money, services, safety, ecology.
2) **Separate facts from arguments**: factual releases are labeled as such; policy positions live elsewhere.
2a) **Make predictions joinable:** major policies/programs should publish testable claim IDs (`CLM-*`) that link to releases (`REL`) and evaluations (`EVAL`) (see `37-...` and `28-...`).
2b) **Treat methods as first-class:** many “official facts” embed definitional choices. Releases MUST publish method notes + revision rules, and SHOULD name where method disputes can be raised (ombuds/statistics board/court lane registered in ALR). See `51-release-registry.md` for the minimal `REL-*` schema and PDRR discipline.
3) **Correct quickly**: errors are inevitable; *denial and hidden revisions are fatal*.
4) **Make updates legible**: changes have stable IDs, versioning, and revision logs (like rules and compacts).
5) **Resist interference**: political pressure is expected; the system must log and survive it.


**Protective legibility note:** epistemic releases constrain power only if independent users can *use* them. Publish machine-readable releases **and** person-readable summaries, plus low-bandwidth/offline access; fund and protect contestation capacity (independent media, civil society, legal aid). Otherwise MVEI becomes dashboard theater. See `99-protective-legibility-and-adoption-dynamics.md`, [TM-33], and [TM-16].


---

## B. Minimum Viable Epistemic Infrastructure (MVEI)

### 1) Official statistics function (professional independence)
- MUST: a legal mandate, professional standards, and **equal access** (no privileged pre-release).
- MUST: a pre-announced **release calendar** for core series.
- MUST: publish **methods** (sampling/definitions/coverage), known biases, and uncertainty.
- MUST: publish a **revision policy** (what can change, how it is tagged, how far back revisions can reach).
- SHOULD: protected tenure for chief statistician / governing board + firewall from line ministries.

### 2) Administrative data quality (the “pipes” behind the numbers)
- MUST: stable identifiers for core objects (units, programs, contracts, rules, emergencies, systems).
- MUST: data quality checks and an audit trail for changes.
- SHOULD: publish a small **data quality statement** for major administrative series (coverage, missingness, definitional drift).

### 3) Evaluation & learning function (policy updates based on evidence)
- MUST: for high-spend or rights-sensitive programs, publish an **evaluation commitment**: what outcomes, when reviewed, and what decision will follow.
- SHOULD: publish evaluation protocols (pre-analysis plans where feasible), and publish results even when negative.
- SHOULD: maintain a Program Register + Evaluation Registry (stable IDs) linking: (program → predicted effects → evaluation → decision revision). See `28-program-register-and-evaluation-commitments.md`.

### 4) Public information integrity (without turning into censorship)
- MUST: publish official information with **provenance** (source, method, uncertainty, last updated, revision history).
- SHOULD: publish releases with **as‑of access** and a signed **checksum manifest** so third parties can mirror and detect silent tampering (see `53-publication-integrity-and-tamper-evident-logs.md` (and `31-...`; anchors: [BIB-RFC6962], [BIB-TRILLIAN]).
- SHOULD: for media outputs (images/video) where feasible, add verifiable content provenance metadata (e.g., C2PA Content Credentials) and publish simple verification instructions.
- MUST: publish corrections/errata with stable IDs; never silently edit releases.
- SHOULD: publish a compact “rumor response” workflow for emergencies (what the institution can confirm/deny, and how it updates). See `61-public-communication-and-information-integrity.md`.
- SHOULD: prefer *transparency + literacy + provenance* over speech policing.

---

## C. Registers (small, join-key friendly)

### 1) Public Data Release Register (PDRR)
A public index of official releases (series or datasets) with stable IDs.

**PDRR — minimum schema**
| Field | Meaning |
|---|---|
| Release ID (`REL-ID`) | stable ID for the dataset/series |
| Owner unit | the producing body (must be in competence ledger) |
| Coverage | territory/service-area/time span |
| Indicators | linked metric IDs (e.g., `[IPM-2]`, `[ECO-1]`) where relevant |
| Method note | definitions + method link |
| Source systems | admin systems / surveys / external sources |
| Update cadence | calendar + publication lag |
| Revision policy | what changes are allowed + tagging |
| Revision log | dated record of corrections/updates |
| Contestation lane | where to challenge methods/revisions (cite `AL-*` where applicable) |
| Access mode | open / safeguarded microdata / restricted |

**Canonical join-key:** `REL-*` (Release object). The PDRR is the index of `REL` objects. The **home spec** for `REL-*` is `51-release-registry.md` (minimum public schema + revision discipline).

**Metadata interoperability (optional but recommended):** publish catalogs using DCAT 3 [BIB-W3C-DCAT-3], statistical series using SDMX 3.0 [BIB-SDMX-3-0], and provenance using PROV-O [BIB-W3C-PROV-O].

**For stats-grade releases (recommended fields beyond the one-screen minimum):**
- update cadence + publication lag (so “late data” is measurable),
- explicit `REVISION-OF` linkage + a short changelog entry per revision,
- uncertainty / quality note (even if qualitative),
- status flags (provisional/final/superseded).

See also `53-publication-integrity-and-tamper-evident-logs.md` for signed bundle / transparency log patterns that prevent silent rewrites.


### 2) Methods & definitions register
- SHOULD: stable IDs for major definitions (e.g., “unemployment”, “serious incident”, “contract award”).
- SHOULD: change logs and crosswalks when definitions change.

### 3) Interference & integrity log (for trust)
- SHOULD: publish a quarterly log of attempted interference (redacted where needed) and how it was handled.

---

## D. Failure modes (and hard rules)
- **Suppressed series / missing baselines:** treat as a governance incident.
- **Silent revisions:** prohibited; all revisions must be logged.
- **Dashboard theatre:** metrics without decision loops (`03-metrics-and-evidence.md`) are noise.
- **Consultant epistemic monopoly:** require open methods and replicability for public claims.
- **Narrative capture:** separate “facts release” from “policy argument”; publish uncertainty.

---

## E. Interfaces (how this plugs into the archive)
- The competence ledger SHOULD link to the producing unit’s PDRR (legibility of facts) (`70-interoperability.md`).
- Metric packs SHOULD reference releases by Release ID where feasible (`03-metrics-and-evidence.md`).
- Emergency Measures Register entries SHOULD link to relevant releases and corrections (outbreak curves, damage assessments) (`23-...`).
- Rule IDs and Release IDs SHOULD be join-keys in notices/reasons (why a decision happened) (`25-...`, `08-...`).

---

## F. Minimal metrics (choose ≤6)
Prefer metric IDs from `03-metrics-and-evidence.md`.
- release calendar compliance (% on-time) [DAG-5]
- share of releases with method + revision log [DAG-5]
- correction latency (median + 90p) [DAG-5]
- interference incidents logged (count + type) (assumption: publishable without undue harm)
- share of major programs with evaluation commitments and completed reviews on time (assumption: registry exists)
- share of key admin series with published data quality statements (assumption)
