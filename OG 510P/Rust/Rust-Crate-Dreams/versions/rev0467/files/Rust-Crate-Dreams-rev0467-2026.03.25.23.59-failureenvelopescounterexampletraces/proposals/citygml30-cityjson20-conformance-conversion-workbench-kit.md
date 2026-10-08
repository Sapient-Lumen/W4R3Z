---
id: P-0343
title: CityGML 3.0 + CityJSON 2.0 Conformance & Conversion Workbench Kit — schema-aware validation, semantic diffs, and explainable GML↔JSON evidence bundles
status: idea
domains: [geospatial, digital-twins, cities, standards, citygml, cityjson, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.ogc.org/standards/citygml/
  - https://www.ogc.org/standards/cityjson/
  - https://github.com/cityjson/cjval
  - https://docs.rs/ecitygml
  - https://3dcitydb-docs.readthedocs.io/en/version-2024.0/impexp/cli/validate.html
---

# Problem

The Rust geospatial ecosystem is getting better at parsing and geometry, but 3D city-model interoperability still breaks at the seam between **rich CityGML semantics and simpler CityJSON exchange**:

- datasets that are valid against schemas but semantically inconsistent,
- CityGML ↔ CityJSON conversions that lose meaning without saying where,
- extension and ADE-like information that becomes opaque after translation,
- and support/debugging workflows that still ship whole municipal datasets instead of small, explainable repro bundles.

The worthy crate contribution is a **conformance and conversion workbench** that makes 3D city-model interchange testable, diffable, and explainable across XML and JSON surfaces.

# What it provides

- `citymodel-ir` — canonical IR for city objects, geometries, LoDs, appearance/attribute metadata, extensions, and provenance.
- `citymodel-profile` — lockfiles pinning CityGML/CityJSON versions, supported feature subsets, extension policies, and validator pack assumptions.
- `citymodel-verify` — normalized schema and semantic checks over both CityGML and CityJSON inputs.
- `citymodel-diff` — semantic diffs such as “LoD changed meaning”, “building part flattened”, or “extension attribute could not round-trip”.
- `citymodel-convert` — explainable conversion helpers between targeted CityGML 3.0 subsets and CityJSON 2.0.
- `cargo citymodel-evidence` — emit `*.citymodelbundle.zip` for vendor handoff, procurement tests, and municipal ETL regression suites.

# What the crate should provide other people

1. **A boring default for validating 3D city data across XML and JSON encodings**.
2. **Explainable conversion loss reports** rather than silent field disappearance.
3. **Pinned validator behavior** tied to exact schema/extension assumptions.
4. **Small evidence bundles** suitable for issue trackers and procurement tests.
5. **A Rust-native bridge** between digital-twin pipelines and official validation surfaces.

# Persona / who it’s for

- Municipal and regional geospatial platform teams
- 3D city ETL and digital-twin vendors
- Rust geospatial developers
- QA teams evaluating procurement/interop requirements

# Users & user stories

- **Data engineer**: “Show me exactly what semantic information was lost during CityGML→CityJSON conversion.”
- **Vendor integrator**: “Pin the subset of CityGML 3.0 we support and fail clearly when the data leaves it.”
- **Procurement evaluator**: “Run the same conformance bundle against two toolchains and compare results.”
- **City platform team**: “Ship a tiny repro instead of a citywide dataset dump.”

# Prior art (and why it’s insufficient)

- OGC publishes current **CityGML 3.0** and **CityJSON** standards.
- `cjval` is an official Rust validator for CityJSON and CityJSONSeq.
- `ecitygml` provides early Rust CityGML 3.0 substrate.
- 3D City DB tooling can validate CityGML and CityJSON against official schemas.
- But Rust still lacks a shared **IR + conversion-loss reporting + semantic diff + portable evidence bundle** story.

# Design goals

1. **Subset-aware honesty** — make supported and unsupported semantics explicit.
2. **Semantic validation over pure schema validation** — explain what is wrong in city-model terms.
3. **Round-trip accounting** — conversion should report meaning preserved, inferred, or lost.
4. **Adapter-first** — build on existing validators and schemas.
5. **Procurement-friendly evidence** — bundles should be easy to archive and compare.

# MVP surface

- Minimal types: `CityModel`, `CityProfile`, `SemanticFinding`, `ConversionReport`, `CityModelBundle`
- Minimal functions:
  - `load_citygml()`
  - `load_cityjson()`
  - `verify_citymodel()`
  - `convert_subset()`
  - `diff_semantics()`
  - `write_bundle()`
- Feature flags:
  - `citygml-3-0`
  - `cityjson-2-0`
  - `cityjsonseq`
  - `extensions`
  - `serde`

# Compatibility story

- MVP targets CityGML 3.0 and CityJSON 2.0 subset interoperability first.
- It complements existing parsers/validators rather than replacing them.
- It intentionally avoids becoming a general 3D GIS renderer or spatial database.

# Conformance & fixtures

- Tiny building, bridge, vegetation, and transportation examples.
- Known-invalid fixtures for geometry/topology/attribute inconsistencies.
- Round-trip fixtures showing supported vs unsupported subset mappings.
- Extension fixtures with explicit “preserved / downgraded / dropped” outcomes.

# Path to boring stability

- Stabilize the IR around a documented CityGML/CityJSON overlap subset first.
- Freeze the loss-report vocabulary before broad converter ambitions.
- Keep extension handling explicit and opt-in.
- Prefer content-hash-pinned validator/schema packs.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that validate one CityGML 3.0 file and one CityJSON 2.0 file against a pinned profile, attempt a documented overlap conversion, report semantic losses/diffs, and emit a replayable `*.citymodelbundle.zip`.

# De-risk plan

1. Start with a small overlap subset instead of “all of CityGML”.
2. Reuse `cjval` and schema packs where possible.
3. Treat conversion-loss reporting as the differentiator, not aggressive feature coverage.
4. Validate on tiny public datasets and synthetic fixtures first.

# Non-goals

- Not a full 3D GIS viewer.
- Not a city database.
- Not a promise of lossless conversion for all CityGML semantics.

# Architecture & API sketch

```rust
pub struct ConversionReport {
    pub profile_id: String,
    pub semantic_findings: Vec<Finding>,
    pub conversion_losses: Vec<LossFinding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_citymodel(profile: &CityProfile, model: &CityModel) -> ConversionReport;
pub fn convert_subset(profile: &CityProfile, model: &CityModel) -> Result<CityModel>;
```

Bundle draft: `profile.toml`, `source/`, `normalized.json`, `validator-results.json`, `conversion-report.json`, `semantic-diff.json`, `notes.md`.

# Security / safety model

- Guard XML and JSON parsing against resource amplification and path abuse.
- Keep bundle capture small and path-normalized.
- Record exact schema and validator versions.
- Prefer extension manifests over arbitrary executable logic.

# Maintenance & governance plan

- Keep the core focused on overlap IRs, validators, and loss reporting.
- Version profile packs and extension packs separately.
- Accept community fixtures only when licensing and redistribution are clear.
- Document every unsupported semantic family explicitly.

# Milestones

## 0.1
- CityJSON 2.0 verification
- CityGML 3.0 subset loader
- shared IR and bundle draft

## 0.2
- explainable subset conversion
- semantic diffs
- extension/loss reporting

## 1.0
- stable `*.citymodelbundle.zip`
- procurement-friendly fixture corpus
- versioned validator/schema packs

# Open questions

- What is the sharpest useful overlap subset between CityGML 3.0 and CityJSON 2.0 for MVP?
- Should geometry/topology checks live in core or optional geospatial adapters?
- How much extension support can be made boring without over-promising ADE round trips?

# Sources

- OGC CityGML standard: https://www.ogc.org/standards/citygml/
- OGC CityJSON standard: https://www.ogc.org/standards/cityjson/
- `cjval`: https://github.com/cityjson/cjval
- `ecitygml`: https://docs.rs/ecitygml
- 3D City DB validate command: https://3dcitydb-docs.readthedocs.io/en/version-2024.0/impexp/cli/validate.html
