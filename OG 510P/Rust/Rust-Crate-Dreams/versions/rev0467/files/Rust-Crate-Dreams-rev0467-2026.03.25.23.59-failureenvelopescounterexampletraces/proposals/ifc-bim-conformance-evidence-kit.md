---
id: P-0305
title: IFC / BIM Conformance & Evidence Kit — schema-aware validation, model diffs, and reproducible exchange bundles for building data
status: idea
domains: [aec, cad, data, interoperability, validation]
last_reviewed: 2026-03-06
evidence:
  - https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/
  - https://technical.buildingsmart.org/services/validation-service/
  - https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/
---

# Problem

The AEC/BIM ecosystem lives on interchange quality, and IFC is the center of that exchange surface. Rust now has visible parser/model momentum — `ifc_rs`, `bimifc-parser`, `ifc-lite-core`, and related crates — but real-world pain is not just “open the file.” It is:

- schema/version drift across IFC releases,
- model-export quirks between authoring tools,
- hard-to-explain validation failures,
- huge files and geometry-heavy diffs,
- lack of portable issue artifacts for vendors, integrators, and compliance programs.

buildingSMART’s validation service and validation tooling make it clear that the leverage point is **conformance, rule execution, and explainable model exchange quality**. Rust lacks a default evidence-grade workbench here.

# What it provides

- `ifc-lock` — pin schema/version/rule-set assumptions for a given exchange workflow.
- `ifc-canon` — canonical IR for syntax/schema/rule findings, object identity, property-set summaries, and exchange metadata.
- `ifc-diff` — semantic diffs for entities, properties, relationships, quantities, and selected geometry summaries.
- `ifc-fixtures` — reference corpora for export/import round-trips, validation regressions, and profile-specific exchange packs.
- `ifc-evidence` — build `*.ifcbundle.zip` artifacts for vendor support, CI, and conformance review.
- `cargo ifc-validate` — run validation, canonicalize results, diff models, and package incidents.

# What the crate should provide other people

1. **A stable way to talk about validation failures** across authoring tools and downstream pipelines.
2. **Model-diff primitives** that are useful for CI and vendor bug reports, not just generic text diff.
3. **Schema/rule pinning** so teams know exactly which IFC expectations were applied.
4. **Large-file pragmatism** with summaries and sampled evidence instead of naïve full copies everywhere.
5. **Adapter hooks** for both Rust-native parsers and external/reference validation services.

# Users & user stories

- **BIM platform teams**: “Explain why this exported model fails the rule set while last week’s passed.”
- **Tool vendors**: “Package one evidence bundle showing the object/property differences and validation findings.”
- **Construction / owner operators**: “Gate IFC deliveries in CI before they enter downstream systems.”
- **Rust parser authors**: “Compare our parse/validation interpretation against reference outputs.”

# Prior art (and why it’s insufficient)

- buildingSMART publishes the IFC schema specifications and runs a validation service; that is strong evidence that conformance is the real bottleneck.
- Rust parsing/model crates are emerging quickly, which means the ecosystem has substrate.
- What is still missing is the **bundle/diff/lockfile layer** that turns validator output and parser output into reproducible workflows.

# Design goals

1. **Validation-first** — prioritize conformance and explainability over renderer ambition.
2. **Schema explicitness** — every run records exact schema/rule assumptions.
3. **Scalable evidence** — handle huge models without producing uselessly gigantic artifacts.
4. **Semantic diffs** — compare entities/properties/relations, not just STEP text.
5. **Bridge reference and native tools** — Rust-native results should be comparable to buildingSMART-style validation outputs.

# Non-goals

- Not a full BIM authoring environment.
- Not a renderer-first toolkit.
- Not a replacement for every certification program.

# Architecture & API sketch

```rust
pub struct IfcEvidenceReport {
    pub schema_id: String,
    pub rule_pack: String,
    pub verdicts: Vec<Verdict>,
    pub entity_diffs: Vec<EntityDiff>,
}

pub trait IfcAdapter {
    fn load(&self, bytes: &[u8]) -> Result<CanonicalIfcModel, Error>;
    fn validate(&self, model: &CanonicalIfcModel) -> Result<Vec<ValidationFinding>, Error>;
}
```

Bundle draft: `ifc.lock`, `summary.json`, `findings.json`, `entity-diff.json`, `geometry-summary.json`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Treat uploaded IFC files and external references as hostile input.
- Permit selective suppression/tokenization of owner names, project identifiers, and embedded metadata when sharing bundles externally.
- Enforce size/time limits for validation and diff passes.

# Maintenance & governance plan

- Keep canonical findings and diff IR stable and additive.
- Separate heavy geometry helpers from core validation/reporting crates.
- Publish generic exchange-profile packs before tool-specific packs.

# Milestones

## 0.1
- Canonical findings IR
- Schema/rule lockfile
- Entity/property diff MVP

## 0.2
- Reference validator adapter
- Large-model summary mode
- `cargo ifc-validate diff`

## 1.0
- Stable `*.ifcbundle.zip`
- CI-friendly exchange gatekeeping
- Cross-tool comparison reports

# Open questions

- Which rule-pack abstractions are stable enough for a public lockfile format?
- How much geometry belongs in the initial evidence bundle versus follow-on artifacts?
- Which IFC releases should be mandatory for MVP support?

# Sources

- IFC schema specifications: https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/
- buildingSMART Validation Service: https://technical.buildingsmart.org/services/validation-service/
- buildingSMART IFC overview: https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/
- Validation service details: https://www.buildingsmart.org/users/services/validation-service/
- Rust crates: https://crates.io/crates/ifc_rs ; https://crates.io/crates/bimifc-parser ; https://crates.io/crates/ifc-lite-core ; https://crates.io/crates/ifc
