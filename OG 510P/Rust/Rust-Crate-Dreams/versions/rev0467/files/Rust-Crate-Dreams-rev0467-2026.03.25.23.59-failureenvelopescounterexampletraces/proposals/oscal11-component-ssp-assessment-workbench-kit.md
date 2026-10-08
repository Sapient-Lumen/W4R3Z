---
id: P-0366
title: OSCAL 1.1.x Component + SSP + Assessment Workbench Kit — cross-model locks, validation diffs, and audit-ready evidence bundles
status: idea
domains: [security, compliance, governance, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://pages.nist.gov/OSCAL/
  - https://pages.nist.gov/OSCAL/learn/concepts/validation/
  - https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/assessment-results/json-definitions/
  - https://pages.nist.gov/OSCAL-Reference/models/v1.0.2/system-security-plan/json-definitions/
  - https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-reference/
  - https://docs.rs/roscal_lib
  - https://oscal.io/tools/
---

# Problem

Rust now has real OSCAL substrate, but the operational pain is still concentrated at the seam between:

- catalogs, profiles, component definitions, SSPs, and assessment results,
- model-version and serialization-format assumptions,
- identifier/link consistency across documents,
- validation findings from schemas, metaschemas, and workflow-specific rules,
- and audit/support exchanges that still rely on giant document handoffs instead of small, replayable artifacts.

The missing Rust contribution is not another compliance dashboard. It is a **cross-model workbench** that makes OSCAL packages reproducible, comparable, and easier to debug or review.

# What it provides

- `oscal-lock` — lockfiles pinning model versions, document families, serialization format, identifier policy, profile dependencies, and validation rules in use.
- `oscal-ir` — a normalized IR for component definitions, SSPs, assessment plans/results, and cross-document links.
- `model-check` — validate one OSCAL document or a linked set and normalize the findings.
- `oscal-diff` — semantic diffs such as “same control implementation, different component linkage” or “assessment result no longer aligns to locked SSP identifiers”.
- `cargo oscal-evidence` — emits `*.oscalbundle.zip` with lockfiles, normalized reports, link graphs, redaction maps, and review notes.

# What the crate should provide other people

1. **A boring default artifact for OSCAL interoperability and audit-review bugs**.
2. **Pinned cross-model expectations** that survive schema/version and process changes.
3. **Explainable validation and linkage diagnostics** rather than giant document diff noise.
4. **Replayable review bundles** for SSP/component/assessment exchanges.
5. **A bridge from Rust OSCAL libraries to evidence-grade compliance automation workflows**.

# Persona / who it’s for

- Compliance-automation teams
- Federal and regulated-environment tooling authors
- Security engineering teams generating or reviewing OSCAL artifacts
- Rust developers building OSCAL conversion/validation tools

# Users & user stories

- **Compliance engineer**: “Tell me whether this package fails because of schema validity, broken cross-document identifiers, or stale assessment linkage.”
- **Tool maintainer**: “Diff two SSP/component/assessment packages semantically instead of by raw JSON churn.”
- **Review team**: “Ship a compact, audit-ready bundle with the minimum material needed to reproduce a finding.”
- **Automation engineer**: “Lock which OSCAL models and versions this workflow actually supports before connecting more generators.”

# Prior art (and why it’s insufficient)

- NIST publishes OSCAL model references, validation guidance, and metaschema-derived representations.
- Rust has real substrate in `roscal_lib` and related tooling recognized on the OSCAL tools index.
- But Rust still lacks a boring-default crate for **cross-model lockfiles + normalized validation/linkage diffs + portable evidence bundles**.

# Design goals

1. **Cross-document first** — model the linked package, not only one file at a time.
2. **Version-explicit** — lock exact OSCAL model/version assumptions.
3. **Identifier-aware** — UUID and linkage consistency should be first-class.
4. **Review-friendly** — findings should help humans reviewing compliance packages.
5. **Format-neutral** — JSON, YAML, and XML representations should normalize into one report model.

# MVP surface

- Minimal types: `OscalLock`, `OscalBundle`, `LinkGraph`, `ValidationFinding`, `LinkDiffFinding`
- Minimal functions:
  - `inspect_package()`
  - `validate_package()`
  - `diff_packages()`
  - `write_bundle()`
- Feature flags:
  - `component`
  - `ssp`
  - `assessment`
  - `redaction`

# Compatibility story

- MVP should focus on common component-definition, SSP, and assessment-results workflows.
- The crate should complement OSCAL parsers/builders rather than replace them.
- Rule packs for specific frameworks can live outside the stable lockfile/report schemas.
- Format normalization must remain deterministic across JSON/YAML/XML inputs.

# Conformance & fixtures

- Tiny linked packages consisting of component definition + SSP + assessment results.
- Cases for broken UUID references, stale control links, invalid model versions, and format-equivalent but semantically divergent packages.
- Goldens for “valid file, invalid package linkage” and “same control implementation, different assessment evidence mapping”.
- Redaction tests for implementation details, assessor names, and environment identifiers.

# Path to boring stability

- Stabilize the lockfile, link-graph, and bundle schemas before chasing framework-specific overlays.
- Start with schema/linkage validation and semantic diffs, not continuous-monitoring platform features.
- Keep human-review explanations short and operational.
- Build a small public corpus from tiny linked packages.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect a small linked OSCAL package, pin its model/version assumptions, validate linkage and document structure, and emit a compact `*.oscalbundle.zip` with normalized findings and semantic diffs.

# De-risk plan

1. Start with component-definition + SSP + assessment-results packages instead of every OSCAL model.
2. Treat identifier/linkage normalization as the hardest early design problem.
3. Keep framework-specific rule packs out of the core MVP.
4. Use tiny linked packages before large compliance-document corpora.

# Non-goals

- Not a GRC platform.
- Not a FedRAMP automation portal.
- Not a replacement for NIST reference tooling.
- Not a full continuous-monitoring product.

# Architecture & API sketch

```rust
pub struct OscalLock {
    pub model_versions: Vec<ModelVersionPin>,
    pub formats: Vec<OscalFormat>,
    pub identifier_policy: IdentifierPolicy,
}

pub fn inspect_package(paths: &[std::path::PathBuf]) -> Result<OscalLock>;
pub fn validate_package(lock: &OscalLock, package: &OscalPackage) -> Result<OscalReport>;
```

Bundle draft: `profile.toml`, `package/`, `link-graph.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat OSCAL documents and references as untrusted input.
- Support redaction of component details, identifiers, and organizational metadata.
- Record exact model versions and validation-rule packs in every bundle.
- Keep output deterministic enough for audits, review cycles, and regression tracking.

# Maintenance & governance plan

- Keep the core centered on lockfiles, link graphs, normalized findings, diffs, and bundle format.
- Version framework-specific overlays separately.
- Publish a small public corpus around common linkage and validation failure modes.
- Avoid coupling the workbench to any one assessor portal or compliance regime.

# Milestones

## 0.1
- package inspection
- model/version lockfile
- validation and linkage report

## 0.2
- semantic diffs
- format normalization
- redaction support

## 1.0
- stable `*.oscalbundle.zip`
- public fixture corpus
- documented compatibility policy for supported OSCAL model families

# Open questions

- Which linked-package shape is the smallest useful default corpus?
- How much validation detail belongs in the stable core report format?
- What redaction defaults preserve reviewer trust without leaking too much implementation detail?

# Sources

- OSCAL home: https://pages.nist.gov/OSCAL/
- OSCAL validation concepts: https://pages.nist.gov/OSCAL/learn/concepts/validation/
- OSCAL assessment-results model reference: https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/assessment-results/json-definitions/
- OSCAL SSP model reference: https://pages.nist.gov/OSCAL-Reference/models/v1.0.2/system-security-plan/json-definitions/
- OSCAL component-definition model reference: https://pages.nist.gov/OSCAL-Reference/models/v1.1.1/component-definition/json-reference/
- `roscal_lib`: https://docs.rs/roscal_lib
- OSCAL tools index: https://oscal.io/tools/
