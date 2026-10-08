# Identity & Recognition (Who Counts, and Across Which Boundaries)

**Purpose:** bound identity/recognition systems so they enable access and remedy without becoming a control choke‑point.

**Person served:** the person whose identity/eligibility is being computed or contested (often at high stakes) who needs inclusion, error correction, and protection from surveillance misuse.

**From-below:** This makes sure you can be recognized and served without being erased, misclassified, or trapped behind identity gates you can’t meet.
**Join constraints:** joins/identifiers MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**Material floor (one sentence):** identity proofing/verification MUST have an offline, assisted alternative (paper/oral/in‑person) and MUST NOT require devices/accounts; degraded-mode fallbacks still issue receipts and allow correction propagation. (See `101-claude-rev142-normative-requirements.md` (NR-13, NR-07).)

Governance cannot be “rights-first” if people cannot *prove* who they are, cannot be *recognized* as legal persons, or cannot carry status/credentials across boundaries. This memo defines a minimal **identity + recognition stack** that is compatible with privacy, inclusion, and cross-scope interoperability.

**Canonical interface spec:** identity proofing / credential issuance / verification systems should be published as `IDN-*` entries; see `44-identity-credential-and-eligibility-systems-register.md`.

**Risk note:** identity systems can protect access **and** enable targeting. Where legibility can be weaponized, designs MUST minimize unnecessary joining, publish strong error‑correction and exclusion safeguards, and plan for regime change (see `77-sensitive-information-and-secrecy-governance.md` and `99-protective-legibility-and-adoption-dynamics.md`). In plural societies, “identity” is not singular; systems SHOULD accommodate multiple legitimate forms of recognition where feasible.

**Terminology note:** in this archive, `EID` refers to an **entity identifier** (for organizations/counterparties) used for cross-register joins (`70-interoperability.md`). Do not confuse this with *electronic identity* (eID) programs such as eIDAS/EUDI.

## Kernel anchors (do not repeat)

- **EXP pointer:** identity systems must counter EXP-03 Proof burden, EXP-04 Error, and EXP-08 Invisibility (see `98-persons-path-and-accessibility-invariants.md`).
- Person-facing invariants (no AI-only gate; non-reading options): `98-persons-path-and-accessibility-invariants.md` and service journeys `47-...`.
- Identity/eligibility system register (`IDN-*`/`ELG-*`): `44-...`.
- Data protection and secrecy constraints: `33-...`, `77-...`.
- Records + publication integrity for rules/versions and corrections: `31-...`, `53-...`, and `70-...`.
- Remedy/appeals for identity errors and harms: `08-...`, `36-...`, `76-...`.
- Protective legibility + adoption dynamics (identity constraints are contested and weaponizable): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- **Inclusion + portability vs targeting/surveillance**
- **Uniqueness/anti‑fraud vs exclusion + administrative burden**
- **Interoperability vs error propagation**
- **Legibility vs safety** (especially for collective persons and under regime change)

**Once-only / proof burden rule:** where the state already possesses a required fact/document (from prior interactions or another agency), requiring the person to repeatedly re-prove it by default is a design defect; identity gates MUST publish reuse/consented retrieval options and least-burdensome acceptable alternatives, and missing‑doc denials MUST surface whether the state could have obtained the item itself. (See `101-claude-rev142-normative-requirements.md` (NR-06).)

**Cascading error rule:** joined identity/eligibility data can propagate mistakes across systems; corrections MUST be “fix once” at the source and propagate with downstream notification/ack visibility for high‑stakes fields (see `70-...`). (See `101-claude-rev142-normative-requirements.md` (NR-07).)

## Collective persons and group recognition (don’t flatten communities into individuals)
Some governed subjects are **collective**: Indigenous nations, customary communities, cooperatives, unions, associations, municipalities, and other group legal persons. Their governance relationship is not just the sum of individual member interactions.

**Minimum discipline:**
- define a group’s legal personality and representation rules as `RULE-*` / `IDN-*` (who can speak/consent on behalf of the group),
- provide a contestable membership/status process with remedy (`DRR-*` + `AL-*`) where the state makes determinations that bind the group,
- avoid publishing joinable rosters in hostile environments; treat group registries as potential targeting tools (regime‑change posture applies).

**Collective harms:** identity/recognition systems must support collective filing and recognized representation (communities, unions, NGOs, nations) when harms are experienced collectively; see `36-...`, `41-...`, and `101-claude-rev142-normative-requirements.md` (NR-12).

## Person’s Path failure modes in identity (proof, error, fear)

Identity is where the **person’s path** is most fragile: people are asked to prove they exist, and errors propagate into denial of services, mobility, and voice.

**Minimum requirements (wire to `98`):**
- **No receipt, no effect:** any denial, revocation, or adverse verification result MUST emit a portable `DRR-*` receipt with rule basis (`RULE-*` as-of), reasons (`RC-*`), and a discoverable remedy lane (`AL-*`). (`31`, `39`, `36`, `98`)
- **No AI‑only front door:** enrollment, verification, and correction MUST have a staffed/non‑digital path (in‑person/phone/paper) and must not require proprietary apps or private tooling; otherwise identity becomes a gate and a weapon. (`98-persons-path-and-accessibility-invariants.md`, `44-...`, `82-...`)
- **Error correction is a service:** publish correction lanes, time promises, and interim protections while corrections propagate (especially for status needed to work, vote, travel, or access essential services). (`44`, `70`, `82`)
- **Fear + retaliation:** provide safe proxy/advocate options and confidential filing where complaining can trigger harm (domestic violence, policing risk, immigration precarity). (`08`, `36`, `98`)
- **Residual / “no-fit” handling:** when a person cannot satisfy the formal category (missing papers, nonstandard family structures, customary recognition), the system MUST provide an escalation path to authorized human adjudication; do not silently exclude. (`44`, `85`) (See `101-claude-rev142-normative-requirements.md` (NR-10).)
## What this primitive covers (and what it does not)
Covers:
- civil registration and vital events (**CRVS**): birth, death, marriage/divorce, etc.
- legal identity and authentication for access to services
- civil status and membership decisions (citizenship, residency, asylum status) as *administrative determinations with remedy*
- recognition and portability of official documents/credentials across jurisdictions

Does not cover:
- surveillance architectures (explicitly treated as a threat to be constrained)
- national security intelligence systems (separate governance problem)

## Minimal identity + recognition stack

### 1) CRVS as the “ground truth” layer
- MUST: universal, accessible, and timely registration of births and deaths (and other vital events where applicable).
- MUST: no prohibitive fees; late registration path that is feasible in practice.
- SHOULD: health-sector integration for births/deaths to reduce drop-off and fraud.
- Evidence anchors: see [BIB-WHO-CRVS]; [BIB-UNICEF-BR].

### 2) Legal identity issuance (credential layer)
- MUST: a **legal identity for all** target and an implementation plan (SDG 16.9 framing).
- MUST: non-discrimination; accessible enrollment for remote/rural populations; options for people without documents.
- MUST: separation-of-functions (registration authority, credential issuance, service providers) to reduce misuse.
- MUST: purpose limitation, minimization, and redress for data errors/abuse (`LAW-5`, `ACC-3`).
- SHOULD: follow “do no harm” identity principles (avoid exclusion-by-design).
- Anchor set: see [BIB-UN-LIA]; [BIB-WB-ID-PRINCIPLES].

### 3) Status & membership decisions (rights-affecting determinations)
Examples: citizenship, residency, refugee/asylum status, voting eligibility, name/sex marker changes.
- MUST: publish decision criteria and evidence rules.
- MUST: meaningful notice + reasons, and a fast appeal path (`LAW-5`; see `08-remedy-and-grievance.md`).
- SHOULD: limit discretionary gatekeeping by using checklists + audit trails.
- MUST: protect against statelessness and arbitrary denial of legal personhood (rights baseline: UDHR Art. 6).

### 4) Registries that matter (property, licenses, benefits, sanctions)
Registries are “invisible law.” They control access.

- MUST: publish registry purpose, authority, data fields, retention, and correction process.
- MUST: correction path with deadlines; immutable audit log for changes (`IOP-5` patterns).
- SHOULD: correction actions issue a `DRR` receipt that includes the correction decision, the remedy lane (`AL-*`), and (where feasible) a **downstream notification list** (which dependent systems were notified). For high‑stakes identity/eligibility errors, provide interim protection / fallback service while correction propagates (see `70-...`, `44-...`, `08-...`).

- SHOULD: stable identifiers to connect registries without creating unnecessary surveillance linkages (minimize joinability).
- SHOULD: for legal persons/corporations, beneficial ownership disclosures and exchanges use an open schema (BODS) so procurement, licensing, and anti‑corruption controls can interoperate (see [BIB-BODS]).

### 5) Cross-boundary recognition (paper and digital)
- MUST: a clear rule for when documents/credentials are recognized across jurisdictions (default recognize; document exceptions).
- SHOULD: use standard authentication mechanisms for public documents where available (e.g., HCCH Apostille Convention) rather than ad hoc legalization.
- SHOULD: where digital credentials are used, prefer open standards and verifiable claims over proprietary formats.
- Anchor set:
  - HCCH Apostille Convention (1961): see [BIB-HCCH-APOSTILLE].
  - W3C Verifiable Credentials Data Model v2.0 (2025): see [BIB-W3C-VC2].
  - EU digital identity framework overview (eIDAS / EUDI): see [BIB-EU-EIDAS].

### 6) Participation and voice (anti‑Sybil without surveillance)

Participation ranges from low‑stakes consultations to binding allocations (PB) and voting. Treat identity/uniqueness as a **risk‑tuned control**, not a default requirement.

- MUST: if eligibility, weighting, or one‑person‑one‑input is material, disclose the **assurance profile** (use NIST IAL/AAL/FAL vocabulary or a local equivalent) and reference the `IDN-*` gate used. (See [BIB-NIST-800-63-4].)
- MUST: publish (in `ENG-*` provenance) how uniqueness is enforced (e.g., in‑person check, one‑time participation token, or privacy‑preserving credential presentation) and what is allowed anonymously (labeled **unverified**).
- SHOULD: separate “proof of eligibility” from “content of participation” where feasible (minimize linkability); do not mint globally joinable person IDs in public participation data.
- SHOULD: treat proof‑of‑personhood / Sybil‑resistance schemes as **high‑risk** and document tradeoffs (inclusion, coercion, surveillance, failure recovery). (See [BIB-POPP-SIDDARTH-2020].)

## Failure modes (and how to constrain them)
- **Exclusion-by-design:** strict document requirements, fees, or remote access gaps → use alternative enrollment paths; mobile units; fee waivers; audits for denial disparities.
- **Function creep / surveillance:** identity becomes tracking → strict purpose limitation, independent oversight, and prohibitions on certain linkages.
- **Registry capture:** vendors or factions control the “truth layer” → open specs, audit rights, exit clauses, and public governance (`IOP-4/5`).
- **Data error harms:** wrong entries deny benefits → fast correction + remedy, and “no irreversible harm without human review” for high-stakes cases.

## Minimal metrics (hook into `03-metrics-and-evidence.md`)
Prefer metric IDs from `03-metrics-and-evidence.md` packs; keep ≤10 total.
- birth registration coverage + time-to-registration [LRR-7]
- adult legal ID coverage (disaggregated) + issuance/renewal time [LRR-7]
- denial/deferral rates and appeal outcomes for status decisions (and time-to-remedy) [LRR-4]
- correction request throughput + time-to-correction [LRR-3] / [LRR-4]
- cross-jurisdiction recognition turnaround time for documents/credentials (where applicable) [LRR-4]

## Scope notes (where to place this primitive)
- Municipal: enrollment/access points; service integration; local documentation support.
- National: CRVS backbone; legal identity authority; membership rules; oversight and remedy.
- Supranational: mutual recognition of credentials/identity with rights baselines.
- Global: minimum standards + document authentication pathways to reduce friction and statelessness.
