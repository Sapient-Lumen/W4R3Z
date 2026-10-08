---
id: P-0336
title: MARC 21 + BIBFRAME Conversion Workbench Kit — profile-pinned cataloging transforms, explainable graph/record diffs, and replayable library-metadata bundles
status: idea
domains: [libraries, metadata, marc, bibframe, rdf, xml, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.loc.gov/marc/
  - https://www.loc.gov/marc/bibliographic/
  - https://www.loc.gov/bibframe/
  - https://www.loc.gov/bibframe/mtbf/
  - https://www.loc.gov/bibframe/bftm/
  - https://crates.io/crates/marc
  - https://docs.rs/mrrc
  - https://github.com/lcnetdev/marc2bibframe2
---

# Problem

Libraries and metadata vendors are still living at the seam between **MARC records, MARCXML, and BIBFRAME graphs**. The hard part is not “can I parse ISO 2709 bytes?” It is:

- converting records into graphs without silently losing meaning,
- understanding why round-trips change identifiers, titles, names, authorities, or holdings-relevant semantics,
- comparing transformations in a way catalogers can actually review,
- and shipping reproducible incidents without sending whole ILS exports or bespoke XSLT environments.

The worthy Rust contribution is a **conversion workbench** that treats MARC↔BIBFRAME as a first-class interoperability problem: profile-pinned transforms, explainable semantic diffs, and portable evidence bundles.

# What it provides

- `marc-ir` — canonical Rust IR for leader/control fields, variable fields/subfields, encoding assumptions, MARCXML mappings, and provenance.
- `bf-ir` — canonical Rust IR for BIBFRAME work/instance/item/hub-oriented graph structures, identifiers, contributions, subjects, and relations.
- `conversion-profile` — lockfiles pinning MARC update assumptions, local field mappings, script/transliteration policy, authority-link expectations, and chosen conversion direction.
- `converter-adapter` — wrappers around existing official or de facto conversion workflows, normalizing outputs into stable Rust snapshots.
- `catalog-diff` — semantic diffs: “245 title lost alternate script”, “authority URI introduced/removed”, “instance/work split changed”, “round-trip dropped local field”.
- `cargo bib-evidence` — emit `*.bibbundle.zip` for migration testing, vendor handoff, or cataloging review.

# What the crate should provide other people

1. **A boring artifact for MARC/BIBFRAME migration incidents** instead of shipping whole exports and screenshots.
2. **Profile pinning** for local conversion policy and version assumptions.
3. **Explainable diffs** between record-centric and graph-centric views.
4. **Round-trip evidence** that makes lossiness visible and testable.
5. **A neutral bridge** above ILS platforms, XSLT stacks, and linked-data services.

# Persona / who it’s for

- Library-platform engineers
- Metadata migration teams
- Cataloging/reconciliation tool authors
- Vendors supporting MARC↔BIBFRAME transitions
- Rust developers building metadata infrastructure

# Users & user stories

- **Migration lead**: “Show me exactly what semantic information we lose when converting this MARC set into BIBFRAME and back.”
- **Cataloging engineer**: “Pin our local field and authority assumptions so upgrades stay testable.”
- **Vendor integrator**: “Package a small reproducible conversion incident without exporting the entire library.”
- **Metadata reviewer**: “Diff the graph and the record in domain language, not RDF triples alone.”

# Prior art (and why it’s insufficient)

- MARC remains an official, community-driven family of machine-readable metadata standards coordinated by the Library of Congress.
- The Library of Congress publishes MARC bibliographic documentation plus MARC→BIBFRAME and BIBFRAME→MARC conversion specifications.
- Rust has `marc`, `marc-record`, and newer `mrrc` substrate.
- But there is still no boring-default Rust crate family for **profile pinning + converter adaptation + semantic round-trip diffs + replayable library-metadata bundles**.

# Design goals

1. **Seam-first** — the record↔graph boundary is the unit of value.
2. **Explainability over raw RDF/XML churn** — findings should speak in cataloging terms.
3. **Round-trip awareness** — lossiness must be visible and testable.
4. **Local-policy explicitness** — because library metadata workflows are full of local choices.
5. **Implementation neutrality** — useful whether conversion is driven by XSLT, batch jobs, or online services.

# MVP surface

- Minimal types: `MarcSnapshot`, `BibframeSnapshot`, `ConversionProfile`, `ConversionReport`, `CatalogDiff`
- Minimal functions:
  - `load_iso2709()`
  - `load_marcxml()`
  - `convert_snapshot()`
  - `diff_roundtrip()`
  - `verify_profile()`
  - `write_bundle()`
- Feature flags:
  - `iso2709`
  - `marcxml`
  - `rdfxml`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **MARC 21 bibliographic records** and the currently published **Library of Congress conversion specifications** first.
- It should support both ISO 2709 and MARCXML ingress where practical.
- It should complement, not replace, existing cataloging systems or conversion programs.
- MVP should intentionally avoid becoming a full ILS or graph-store platform.

# Conformance & fixtures

- Small record fixtures covering titles, names, identifiers, subjects, notes, links, local fields, and non-Latin-script/transliteration cases.
- Positive/negative round-trip fixtures for MARC→BIBFRAME and BIBFRAME→MARC.
- Golden semantic verdicts for field loss, authority-link drift, and graph-shape changes.
- Optional adapters for existing Library of Congress conversion tooling outputs.

# Path to boring stability

- First stabilize the IRs and round-trip diff vocabulary.
- Then prove usefulness on synthetic and public demonstration records.
- Freeze bundle layout only after redaction preserves enough bibliographic meaning for review.
- Keep local-policy packs explicit and versioned.

# Scorecard

- Impact: 3/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that ingest one MARC 21 record set, run a pinned MARC→BIBFRAME conversion workflow, diff the graph against a round-tripped MARC snapshot, explain any semantic losses, and emit a redactable `*.bibbundle.zip`.

# De-risk plan

1. Start with bibliographic records only.
2. Wrap existing official conversion tooling instead of claiming a perfect new converter immediately.
3. Keep the IR narrow around bibliographic essentials before taking on authorities/holdings.
4. Use public demonstration records and synthetic edge cases first.

# Non-goals

- Not a full ILS.
- Not a general RDF graph database.
- Not a replacement for cataloging policy or authority control workflows.

# Architecture & API sketch

```rust
pub struct ConversionReport {
    pub profile_id: String,
    pub transform_findings: Vec<Finding>,
    pub roundtrip_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn convert_snapshot(profile: &ConversionProfile, marc: &MarcSnapshot) -> Result<BibframeSnapshot>;
pub fn diff_roundtrip(profile: &ConversionProfile, before: &MarcSnapshot, after: &MarcSnapshot) -> ConversionReport;
```

Bundle draft: `profile.toml`, `input/`, `normalized/`, `output/`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact patron or local-inventory data if present in exports.
- Bound XML/RDF expansion and external-entity behavior.
- Preserve field/subfield provenance after redaction where possible.
- Record exact converter and profile versions used.

# Maintenance & governance plan

- Keep conversion adapters and semantic diff vocabularies separate.
- Version local policy packs explicitly.
- Encourage public sample records and redacted migration fixtures.
- Treat authorities/holdings as future companions unless the core remains small.

# Milestones

## 0.1
- MARC/BIBFRAME IRs
- adapter for one conversion direction
- bundle writer

## 0.2
- round-trip diffs
- redaction support
- local-policy packs

## 1.0
- Stable `*.bibbundle.zip`
- regression fixtures for representative record families
- documented adapter policy for converter/version drift

# Open questions

- How much MARCXML/RDFXML normalization belongs in core versus adapters?
- Should authorities and holdings remain out of scope until after 1.0?
- Can we keep round-trip diffs cataloger-friendly without building a full review UI?

# Sources

- MARC standards hub: https://www.loc.gov/marc/
- MARC 21 bibliographic format: https://www.loc.gov/marc/bibliographic/
- BIBFRAME initiative: https://www.loc.gov/bibframe/
- MARC 21 to BIBFRAME conversion specifications: https://www.loc.gov/bibframe/mtbf/
- BIBFRAME to MARC 21 conversion specifications: https://www.loc.gov/bibframe/bftm/
- `marc`: https://crates.io/crates/marc
- `mrrc`: https://docs.rs/mrrc
- `marc2bibframe2`: https://github.com/lcnetdev/marc2bibframe2
