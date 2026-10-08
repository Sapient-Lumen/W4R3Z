# Identity & Recognition (Who Counts, and Across Which Boundaries)

Governance cannot be “rights-first” if people cannot *prove* who they are, cannot be *recognized* as legal persons, or cannot carry status/credentials across boundaries. This memo defines a minimal **identity + recognition stack** that is compatible with privacy, inclusion, and cross-scope interoperability.

**Canonical interface spec:** identity proofing / credential issuance / verification systems should be published as `IDN-*` entries; see `44-identity-credential-and-eligibility-systems-register.md`.

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
