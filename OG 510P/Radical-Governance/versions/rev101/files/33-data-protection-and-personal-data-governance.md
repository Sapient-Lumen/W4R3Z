# Personal Data Governance (Privacy, Data Sharing, and Due Process)

Personal data is a **cross-scope power amplifier**: it enables targeting, exclusion, surveillance, and administrative domination. This memo defines a **Minimum Viable Data Protection (MVDP)** layer that makes personal-data use *legible, contestable, and bounded*.

**Core idea:** *if you can’t say what personal data is processed, by whom, for what purpose, and under what legal basis, you do not have accountable governance.*

## 1) What this primitive covers
- lawful basis + purpose limitation (Rule IDs, scope boundaries)
- minimization, retention, and security discipline
- rights and remedy for affected people (access/correction/objection; enforceable fixes)
- data sharing and vendor processing (processors, cross-border transfers)
- a small number of **public registers** that make personal-data governance auditable

## 2) Failure modes (design against)
(Threat linkage: **TM-15** “targeting & surveillance” is the cross-scope failure mode this primitive is designed to prevent.)

- **Shadow processing:** unknown data flows, “informal spreadsheets,” or vendor-owned black boxes.
- **Function creep:** data collected for X silently reused for Y (especially policing/immigration/eligibility).
- **Chilling effects:** pervasive logging and profiling suppress lawful behavior.
- **Leakage and breach externalities:** harms are pushed onto individuals, while institutions face weak consequences.
- **Access without remedy:** people can request data but cannot correct it, contest it, or stop misuse.
- **Inter-scope laundering:** local/national/global partners swap data to evade local legal constraints.

## 3) Minimum Viable Data Protection (MVDP)

### A) Legal basis + purpose limitation (joinable)
**MUST**
- identify a **legal basis** for each major processing activity, and link it to a **Rule ID** where feasible (`25-legal-legibility-and-rule-inventory.md`).
- state **purpose**, affected populations, and decision authority; prohibit repurposing without a new legal basis.
- for high-risk processing (rights/benefits/safety/immigration/child welfare), require explicit review gates and an appeal path (`LAW-3`, `LAW-5`).

### B) Data minimization + retention discipline
**MUST**
- collect the minimum necessary data and document why.
- define retention by data class and **bind it to the retention schedule** (`31-records-foi-and-government-memory.md`).
- log deletions/disposition and audit them (prevent “selective forgetting”).

### C) Rights, access, and enforceable fixes
**MUST**
- provide a **request channel** for access/correction/objection, with time bounds and an appeal path.
- ensure correction propagates to downstream systems (no “fixed here, wrong there”).
- publish a **reasons notice** for rights-affecting uses (including automated processing) with the legal basis and a remedy path (`06-digital-and-algorithmic-governance.md`, `08-remedy-and-grievance.md`).

### D) Vendor and cross-scope processing constraints
**MUST**
- require processor contracts to include: purpose limitation, security controls, audit rights, portability/exit, and breach notification.
- prohibit “vendor-only” logs or uninspectable processing in high-stakes domains.
- where cross-scope/cross-border data sharing exists, require a filed agreement/compact with: purpose, safeguards, retention, audit, and remedy (see `19-compacts-and-cooperative-governance.md`).

### E) Public Data Processing Register (DPR) (anti-shadow-processing)
A single register makes personal-data processing **legible as governance**.

**MUST**
- maintain a **Public Data Processing Register (DPR)** conforming to `IOP-9` (stable IDs + change logs) and link it from the competence ledger (`34-competence-ledger-and-mandate-registry.md`).
- treat each “processing activity” as a first-class object with an ID; changes produce a new version (no silent expansion).

#### DPR entry — minimum schema
| Field | Meaning |
|---|---|
| DPR ID | stable identifier (join-key) |
| Owning unit | Unit ID (competence ledger) |
| Purpose | narrow purpose statement |
| Legal basis | Rule ID / statute / compact |
| Data categories | high-level categories (avoid dumping schemas) |
| Subjects | populations affected |
| Sources | systems/registries providing data |
| Recipients/sharing | other units, vendors/processors, cross-border (if any) |
| Retention | retention class + deletion rule |
| Security | baseline controls + audit logs |
| Rights & remedy | access/correction/objection channel + appeal path |
| Links | `PROG-*`, `ADS-*`, `STD-*`, `REL-*` IDs (if aggregate outputs are published) |
| Change log | what changed and why |

**Rule:** if an `ADS-*` is used in a rights-affecting process, its ADS register entry (`ADS-*`) SHOULD reference the relevant **`DPR-*` IDs** (inputs and outputs), and vice versa.

### E2) Joinability vs privacy (avoid reidentification)
Join-keys increase legibility, but they can also enable *reidentification* if published naïvely.

**SHOULD**
- publish **public metadata** even when content must be redacted (so “secret processing” is still detectable),
- avoid publishing globally joinable person identifiers in public registers; prefer event/decision IDs (`DRR-*`, `ENF-*`) and keep person-linkage in protected layers with audited access,
- when linking individuals across systems is necessary, use **scope-limited pseudonyms** (salted hashes / tokenization) with strict access controls and an appeal/correction path.

See the cross-scope privacy interface note in `70-interoperability.md`.

### F) High-risk gate (small)
**SHOULD**
- require a risk gate for processing that is:
  - large-scale,
  - sensitive (health/biometrics/location),
  - coercion-adjacent (policing/immigration), or
  - used to allocate/deny essential services.
- publish a short gate output: risks, mitigations, and the appeal/remedy map.

## 4) Cross-scope implications
- **Micro-local:** default to *no* personal data collection; use consent, minimal rosters, and rapid deletion.
- **Municipal:** most risk concentrates in permits, housing allocation, safety, and benefits access → require DPR coverage, retention discipline, and enforceable correction.
- **Regional:** data sharing for network services (transit/utilities) should use compacts with explicit safeguards and auditability.
- **National:** define baseline rights, independent enforcement, and inter-scope constraints (no laundering); identity systems require strict separation from surveillance. Where identity gates exist, publish a system-level `IDN-*` entry and link its `DPR-*` processing record and correction/appeal lanes (see `44-...`).
- **Participation systems:** verification and rosters can become surveillance. If uniqueness/eligibility is required, prefer privacy‑preserving proof (selective disclosure / one‑time tokens) and publish only aggregate provenance; do not join public comments to identity by default (see `41-...`, `12-...`).
- **Supranational/Global:** interoperability SHOULD not mean data free-for-all; require minimum rights safeguards and auditability for any mutual recognition / cross-border processing.

## 5) Minimal metrics (use existing pack IDs)
- **[LRR-3] Petition/complaint throughput:** include subject access/correction requests + resolution time.
- **[LRR-4] Time-to-remedy:** include time to correct materially harmful data and to stop unlawful processing.
- **[DAG-4] ADS incident rate + response:** treat unlawful data expansions, major breaches, and undeclared sharing as incidents.
- **[DAG-6] DPR coverage (personal data):** share of high-risk processing activities listed/current + on-time access/correction outcomes.

## 6) Hooks into the toolkit
- `LAW-8` Personal data governance baseline (this memo)
- `OPEN-9` Records/retention discipline (privacy is meaningless without retention rules)
- `IOP-9` Register pattern (`DPR-*` IDs as join-keys)
- `IOP-5` ADS governance (DPR ↔ ADS register linkage)

## 7) Anchors (high-trust starting points)
- Baselines: see [BIB-EU-GDPR]; [BIB-OECD-PRIV-2013]; [BIB-COE-C108].
- ISO/IEC 27701 (privacy information management extension to ISO 27001/27002): [BIB-ISO-IEC-27701]
