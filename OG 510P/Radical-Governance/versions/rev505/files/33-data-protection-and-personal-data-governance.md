# Personal Data Governance (Privacy, Data Sharing, and Due Process)

**Purpose:** bound personal‑data power (collection, sharing, retention) so targeting, exclusion, and surveillance are contestable and due process stays real.
**Person served:** a person whose data is collected and used who needs limits, control, and remedy when data processing harms them.

**From-below:** This keeps your data from becoming a trap by limiting uses and giving you rights to see, correct, and contest data-driven decisions.
**EXP pointer:** counters `EXP-03` (Proof burden) and `EXP-04` (Error) by making once-only + correction propagation enforceable (`98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**As-of & corrections:** any joinable artifacts introduced here MUST be versioned and “as‑of” answerable; corrections are append‑only and propagate across dependent systems via `31`/`53` and joins via `70` (no silent overwrites). (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)
**Join constraints:** joins/identifiers MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)

**Authority:** data rights must be enforceable: a binding lane can order access/correction/objection and stop unlawful processing (and impose penalties where supported), with escalation to court/tribunal when needed (`36`, `66`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** exercising data rights must not trigger adverse treatment; provide safe/proxy filing and monitor chilling, especially in hostile contexts (`98`, `83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** controllers bear the burden to show lawful basis/compliance for contested processing; prefer least-burdensome proof for individuals and “once-only” retrieval of state-held facts; adverse outcomes cite `RC-*` + an `AL-*` lane (`44`, `47`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)


Personal data is a **cross-scope power amplifier**: it enables targeting, exclusion, surveillance, and administrative domination. This memo defines a **Minimum Viable Data Protection (MVDP)** layer that makes personal-data use *legible, contestable, and bounded*.

**Core idea:** *if you can’t say what personal data is processed, by whom, for what purpose, and under what legal basis, you do not have accountable governance.*

## Kernel anchors (do not repeat)
- Person-facing invariants (data rights must be usable): `98-persons-path-and-accessibility-invariants.md`, remedy `08-...`, lanes `36-...`.
- Secrecy/legibility weaponization + protective disclosure: `77-...`, `99-protective-legibility-and-adoption-dynamics.md`.
- Publication integrity + government memory (no silent edits; durable records): `53-...`, `31-...`.
- AI/ADS governance where data drives determinations: `06-...`, `42-...`.
- Interoperability constraints (no universal person join-key; consented/purpose-limited joins): `70-...`.

## Named tensions (design must surface these)
- Legibility/accountability vs surveillance/targeting risk (especially under regime change).
- Data sharing for service integrity/fraud vs chilling effects and abuse.
- Centralization/interoperability vs minimization/segmentation (avoid building a single person graph).
- Transparency about processing vs security (don’t publish attack surfaces; publish receipts).
- Automation/personalization vs due process/human review.

## Regime-change / hostile takeover safety (first‑order threat)
Personal data protections must assume **hostile re‑use** is possible: a successor regime, captured agency, or vendor breach can turn “service optimization” into targeting.

**Minimum mitigations (tight):**
- **Minimize centralization:** avoid building a single cross-domain person graph unless absolutely necessary.
- **Key separation:** encryption keys and access approvals SHOULD be split across independent bodies (so capture of one unit is not enough).
- **Break‑glass protocol:** when credible targeting risk emerges, freeze or narrow access paths through a logged, reviewable emergency decision (`DRR-*` / `EMR-*`) with time bounds and independent oversight.
- **Person rights survive:** access/correction/objection lanes MUST remain reachable even during emergencies (with safe proxy/advocate options).
See `99-protective-legibility-and-adoption-dynamics.md` and `77-sensitive-information-and-secrecy-governance.md`.

## Data rights as a person-facing service (the `98` lens)

Data governance is not real if it is only a policy document. The governed experience is: **proof**, **error**, **waiting**, and **fear**.

**Minimum person-facing requirements:**
- **No-wrong-door intake:** any agency or vendor that uses personal data for eligibility, enforcement, or service delivery MUST accept (or route) data-rights requests and complaints; the person should not need to know the data controller structure.
- **Comprehension-tested responses:** access/correction/objection outcomes MUST be understandable and actionable (what was used, why, what to do next), not just legal boilerplate.
- **Once-only principle (proof is a burden):** if the state already possesses a required fact/document (from prior interactions or another agency), requiring the person to resubmit it by default is a design defect; any exception (verification, consent, time lapse) MUST be justified and the least-burdensome alternative offered. (See `101-claude-rev142-normative-requirements.md` (NR-06).)
- **Cascading error protection:** correction outcomes SHOULD include a downstream notification list (which systems were notified, and acknowledgement status) and, for high-stakes errors, interim protections while propagation is pending (pause adverse automation; provisional access where feasible). (See `101-claude-rev142-normative-requirements.md` (NR-07, NR-16); see `70-interoperability.md`.)
- **Delay is harm:** publish and meet time promises for data rights (ack / first contact / decision) and apply interim protections when delay increases targeting risk (e.g., freeze automated adverse actions tied to contested data where feasible).
- **Safe representation:** support proxy/advocate requests and confidential channels for people who cannot safely self-identify or who face retaliation for filing (`08`, `36`, `98`).
- **AI-mediated interfaces:** if chatbots/assistants handle data-rights requests, they are governance infrastructure and MUST preserve a human path + receipts (`42`, `06`).

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

### DPI and cross-system data sharing (special caution)
“Digital Public Infrastructure” (identity, payments, data exchange layers) amplifies both **service capacity** and **surveillance risk** because it creates cross-service linkability.

Minimum discipline for DPI-linked data sharing:
**High-risk DPI intersections:** revenue and benefits systems combine identity, payments, and enforcement incentives; treat cross-system sharing and profiling here as “red zone” processing and route governance through `93-tax-and-revenue-administration.md` / `64-social-protection-and-benefits-governance.md` plus this memo’s registers.

- **No silent federation:** every cross-system join MUST be justified by a `RULE-*` (purpose + necessity) and logged in the processing inventory (`DPR-*`).
- **Segmentation by default:** separate identifiers/contexts unless an explicit rights- and fraud-justified join is approved; publish the join rationale.
- **Independent verification:** DPI operators SHOULD publish assurance artifacts and incident reports with stable IDs (tie into `OFR-*` follow-through where material).

Anchors: OECD on DPI governance; World Bank DPI framework/primer; G20 DPI framework elements. See [BIB-OECD-DPI-DIGITALGOV-2024], [BIB-WB-DPI-PRIMER-2025], [BIB-G20-DPI-FRAMEWORK-2023].

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

**SHOULD**
- support a **once-only** principle where lawful and safe: when the state already holds a fact needed for eligibility/service delivery, it should not repeatedly demand the person re‑prove it (see `47-service-catalog-and-access-journeys-register.md` and `98-persons-path-and-accessibility-invariants.md`).

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
 - public health/biosecurity uses MUST be purpose-bound, time-bound, and auditable; see `57-public-health-and-biosecurity-governance.md`.
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
