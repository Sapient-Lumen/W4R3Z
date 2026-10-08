---
id: P-0329
title: DDEX ERN 4.3 + MEAD Interop & Evidence Kit — profile-pinned release deliveries, explainable metadata failures, and portable DSP onboarding bundles
status: idea
domains: [music, metadata, ddex, ern, mead, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://ddex.net/standards/electronic-release-notification-message-suite/
  - https://kb.ddex.net/reference-material/standards-specifications
  - https://kb.ddex.net/implementing-each-standard/electronic-release-notification-message-suite-%28ern%29/
  - https://ddex.net/standards/media-enrichment-and-description/
  - https://crates.io/crates/ddex-parser
  - https://crates.io/crates/ddex-builder
---

# Problem

The Rust ecosystem is finally starting to grow credible DDEX substrate, but the expensive failures in practice do not happen at “can I parse XML?” They happen at the **profile, choreography, and trading-partner seam**:

- ERN documents that are schema-valid but fail profile or delivery expectations,
- release-profile assumptions drifting between label, distributor, and DSP,
- MEAD payloads that look harmless but break downstream enrichment or matching,
- upgrades from older message versions creating silent metadata loss,
- and partner escalations that still move around as giant XML files, spreadsheets, screenshots, and tribal-memory explanations.

The worthy crate contribution is a **DDEX interop and evidence kit** that turns deliveries, profiles, and validation results into deterministic, explainable, replayable bundles.

# What it provides

- `ddex-ir` — canonical IR for releases, resources, deals, territories, dates, parties, identifiers, and MEAD enrichment objects.
- `ddex-profile` — lockfiles pinning ERN schema/version, release-profile expectations, choreography assumptions, controlled vocabularies, and MEAD overlays.
- `ddex-verify` — semantic checks for profile compliance, release/resource linkage, deal logic, vocabulary mismatches, and metadata completeness.
- `ddex-replay` — deterministic replay of inbound/outbound message transformations, validation runs, and partner-specific delivery assumptions.
- `ddex-diff` — explainable diffs: “resource vanished”, “territory restriction changed”, “deal window shifted”, “MEAD enrichment detached from release”.
- `cargo ddex` — emit `*.ddexbundle.zip` for onboarding, regression CI, or redaction-safe DSP/label support handoff.

# What the crate should provide other people

1. **A boring default artifact for DDEX onboarding failures** instead of raw XML and screenshots.
2. **Profile pinning** for the exact ERN/MEAD assumptions a partner integration requires.
3. **Semantic validation** that talks in release, deal, and enrichment terms.
4. **Replayable deliveries** for regression testing across partner adapters.
5. **A neutral Rust layer** above proprietary platforms and bespoke transformation pipelines.

# Persona / who it’s for

- Distributor and label platform engineers
- DSP ingestion teams
- Metadata operations engineers
- Rights/royalty integration teams
- Rust developers building music-delivery infrastructure

# Users & user stories

- **DSP integrator**: “Tell me exactly which profile rule this release violated and where the offending metadata came from.”
- **Distributor engineer**: “Diff the current ERN output against last month’s known-good partner feed semantically, not just by XML node order.”
- **Metadata ops team**: “Redact sensitive commercial values and partner identifiers but keep the failure reproducible.”
- **Migration lead**: “Replay this ERN 3.x/4.x conversion and show what data changed in meaning.”

# Prior art (and why it’s insufficient)

- DDEX publishes formal ERN and MEAD standards plus explicit release-profile and choreography surfaces.
- The DDEX knowledge base explicitly recommends ERN 4.3 for new implementations.
- Rust now has `ddex-core`, `ddex-parser`, and `ddex-builder`, and there is already at least one open-source validation platform direction.
- But there is still no boring-default Rust crate family for **profile lockfiles + semantic diffs + replayable partner bundles + redaction-safe evidence artifacts**.

# Design goals

1. **Partner-profile first** — the real work is at the agreement boundary.
2. **Release semantics over raw XML** — findings must be expressed in music-metadata terms.
3. **Version-explicit** — every verdict must record exact ERN/MEAD/profile assumptions.
4. **Transformation-aware** — support migration and mapping diffs, not just raw validation.
5. **Implementation-neutral** — useful whether the production system is Rust, Java, Python, or SaaS.

# MVP surface

- Minimal types: `ReleaseSnapshot`, `MeadSnapshot`, `DdexProfile`, `DeliveryAttempt`, `DdexReport`
- Minimal functions:
  - `load_ern()`
  - `load_mead()`
  - `verify_delivery()`
  - `diff_delivery()`
  - `write_bundle()`
- Feature flags:
  - `ern43`
  - `mead`
  - `redaction`
  - `serde`
  - `legacy-adapters`

# Compatibility story

- MVP should target **ERN 4.3.x** and **MEAD 1.1** first.
- It should ingest older message variants through adapters where feasible, but keep stable semantics only for pinned profiles.
- It should complement existing validators and partner systems rather than replace them.
- MVP should intentionally avoid becoming a full music-supply-chain ERP.

# Conformance & fixtures

- Synthetic release fixtures for audio releases, mixed-media edge cases, territory/deal windows, identifier collisions, and contributor mismatches.
- MEAD fixtures for enrichment linkage, localization, and optional marketing metadata.
- Partner-profile fixture packs with known-good and known-bad outputs.
- Optional adapters for existing validation-platform reports.

# Path to boring stability

- First freeze IR and verdict vocabulary on synthetic fixtures.
- Then prove replay against at least two independently produced, redacted delivery corpora.
- Freeze bundle layout only after redaction keeps enough semantic evidence for partner debugging.
- Ship profile packs separately so version churn stays manageable.

# Scorecard

- Impact: 4/5
- Neglectedness: 3/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that ingest one ERN 4.3 message plus optional MEAD payload, validate them against a pinned partner profile, produce an explainable semantic report, diff them against a previous delivery, and emit a redactable `*.ddexbundle.zip`.

# De-risk plan

1. Start ERN-first and keep MEAD as a thin companion in MVP.
2. Avoid live delivery transport in core; focus on offline evidence and validation first.
3. Limit early rule scope to the most common onboarding failures.
4. Use redacted partner fixtures before broadening version coverage.

# Non-goals

- Not a full DSP ingestion platform.
- Not a rights-management or royalty-accounting suite.
- Not a general music XML editor.

# Architecture & API sketch

```rust
pub struct DdexReport {
    pub profile_id: String,
    pub release_findings: Vec<Finding>,
    pub enrichment_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_delivery(profile: &DdexProfile, release: &ReleaseSnapshot, mead: Option<&MeadSnapshot>) -> DdexReport;
pub fn diff_delivery(before: &ReleaseSnapshot, after: &ReleaseSnapshot) -> Vec<DiffFinding>;
```

Bundle draft: `profile.toml`, `input/ern.xml`, `input/mead.xml`, `normalized/release.json`, `verdicts.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact deal terms, partner IDs, commercial flags, and private comments where needed.
- Bound XML entity expansion and attachment sizes.
- Preserve enough identifiers for graph integrity after redaction.
- Record schema/profile hashes for reproducibility.

# Maintenance & governance plan

- Ship profile packs and vocabulary sets as versioned data.
- Keep IR additive and message-family-aware.
- Encourage contribution of small redacted onboarding corpora.
- Treat transport/choreography adapters as optional layers.

# Milestones

## 0.1
- ERN 4.3 IR
- Profile lockfiles
- Semantic validation and bundle writer

## 0.2
- MEAD linkage checks
- Semantic diffs
- Redaction support

## 1.0
- Stable `*.ddexbundle.zip`
- Multiple partner-profile packs
- CI-ready metadata-delivery regression workflows

# Open questions

- Should MEAD stay in the same crate family or be a companion bundle type long term?
- How much choreography logic belongs in profiles versus adapters?
- Is there a clean IR boundary that can support both validation and migration without becoming a giant data model?

# Sources

- DDEX ERN overview: https://ddex.net/standards/electronic-release-notification-message-suite/
- DDEX standards specifications table: https://kb.ddex.net/reference-material/standards-specifications
- DDEX ERN implementation guidance: https://kb.ddex.net/implementing-each-standard/electronic-release-notification-message-suite-%28ern%29/
- DDEX MEAD overview: https://ddex.net/standards/media-enrichment-and-description/
- `ddex-parser`: https://crates.io/crates/ddex-parser
- `ddex-builder`: https://crates.io/crates/ddex-builder
