---
id: P-0342
title: OpenUSD Core Spec 1.0 + USDZ Conformance & Evidence Kit — validator-aware scene/package replay, semantic diffs, and portable asset bug bundles
status: idea
domains: [graphics, media, 3d, interchange, openusd, usdz, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://aousd.org/blog/foundations-of-open-3d-development-introducing-aousd-core-specification-1-0/
  - https://openusd.org/release/toolset.html
  - https://openusd.org/dev/api/class_usd_validator.html
  - https://crates.io/crates/openusd
  - https://crates.io/crates/openusd-rs
---

# Problem

Rust now has early but real OpenUSD substrate, and the standards surface is getting clearer. The painful failures are no longer just “can I parse a USDA file?” They sit at the seam between **composition semantics, package rules, and validator behavior**:

- scenes that load in one tool but fail `usdchecker` or the newer validation framework,
- USDZ packages that are structurally legal ZIPs but operationally poor interchange artifacts,
- layered scene graphs where the bug is really composition/value-resolution drift rather than syntax,
- and bug reports that still travel as giant asset folders, screenshots, and vague “works in app X” claims.

The worthy crate contribution is a **validator-aware conformance and evidence kit** that turns OpenUSD interchange failures into replayable, shareable artifacts with stable findings.

# What it provides

- `usd-ir` — canonical IR for layers, prim paths, composition arcs, package metadata, referenced assets, and validator findings.
- `usd-profile` — lockfiles pinning OpenUSD core snapshot, expected file-format coverage (`usda`, `usdc`, `usdz`), validator pack/version, and packaging rules.
- `usd-verify` — semantic checks for package layout, referenced-asset closure, layer resolvability, and validator result normalization.
- `usd-diff` — semantic diffs such as “composition arc changed meaning”, “asset resolved in one package layout but not another”, or “validator warning set changed between releases”.
- `usd-replay` — deterministic re-run of validation and packaging checks against frozen bundle contents.
- `cargo usd-evidence` — emit `*.usdbundle.zip` for CI, DCC-tool interop debugging, and vendor handoff.

# What the crate should provide other people

1. **A boring default for OpenUSD bug bundles** that are smaller and clearer than entire project directories.
2. **Pinned validator behavior** so teams can tell “spec drift” from “tool drift”.
3. **Semantic diffs above bytes** for scene composition and packaging changes.
4. **A neutral Rust layer** above DCC-specific tooling and above raw format parsing.
5. **A bridge between Rust-native OpenUSD crates and official validation surfaces**.

# Persona / who it’s for

- Pipeline engineers moving assets between DCC/rendering tools
- Engine/runtime teams adopting OpenUSD
- Rust developers building OpenUSD readers, validators, or converters
- QA and interoperability teams for 3D content pipelines

# Users & user stories

- **Pipeline engineer**: “Tell me whether this USDZ failed because of package structure, missing assets, or stage semantics.”
- **Runtime author**: “Replay the same validator bundle across two parser/loader implementations and normalize the findings.”
- **Vendor support engineer**: “Ship a small artifact that preserves the bug without uploading the whole project.”
- **Tooling team**: “Pin a validation profile in CI so the release line does not silently change.”

# Prior art (and why it’s insufficient)

- AOUSD now publishes **Core Spec 1.0** and explicitly describes a **compliance framework**.
- OpenUSD ships `usdchecker` and the newer validator framework.
- Rust has native and wrapper substrate in `openusd`, `openusd-rs`, and `pxr_rs`-style efforts.
- But there is still no boring-default Rust crate family for **profile pinning + validator wrapping + semantic diffing + portable evidence bundles**.

# Design goals

1. **Adapter-first** — wrap official validators and specs rather than inventing a parallel standard.
2. **Scene semantics over file bytes** — explain failures in stage/layer/package terms.
3. **Package-aware reproducibility** — USDZ and external-asset closure should be first-class.
4. **Implementation-neutral evidence** — useful across Rust-native and C++-backed stacks.
5. **Small bundles** — portable enough for CI and support workflows.

# MVP surface

- Minimal types: `UsdBundle`, `UsdProfile`, `StageSnapshot`, `PackageSnapshot`, `ValidatorFinding`, `UsdReport`
- Minimal functions:
  - `load_stage()`
  - `verify_package()`
  - `run_validators()`
  - `diff_stage_semantics()`
  - `write_bundle()`
- Feature flags:
  - `usda`
  - `usdc`
  - `usdz`
  - `validators`
  - `serde`

# Compatibility story

- MVP targets OpenUSD core file/package semantics first, not rendering fidelity.
- It should complement existing Rust OpenUSD readers/writers and official validators.
- It intentionally avoids becoming a full DCC integration framework or asset-management platform.

# Conformance & fixtures

- Tiny USDA/USDC/USDZ examples with known validator outcomes.
- Package closure fixtures with missing, duplicated, and path-normalization edge cases.
- Composition fixtures showing layer-order, reference, variant, and value-resolution changes.
- Normalized snapshots of validator output across specific OpenUSD releases.

# Path to boring stability

- Stabilize the profile format and normalized findings vocabulary before broad API growth.
- Keep validator wrapping explicit, with version hashes recorded in every bundle.
- Add package mutation/diff tools only after scene-load semantics are boring and repeatable.
- Treat “same scene meaning across implementations” as the core promise, not byte identity.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that pin an OpenUSD validator profile, validate a tiny USDA/USDC/USDZ asset set, normalize the findings, and emit a replayable `*.usdbundle.zip` containing package snapshots, validator traces, and semantic diffs.

# De-risk plan

1. Start with package validation and scene/load semantics, not rendering.
2. Reuse official validators rather than cloning their rule logic.
3. Keep bundle contents tiny and synthetic first.
4. Treat scene composition diffs as the main differentiator.

# Non-goals

- Not a renderer.
- Not a full asset database or DCC plugin suite.
- Not a replacement for OpenUSD itself.

# Architecture & API sketch

```rust
pub struct UsdReport {
    pub profile_id: String,
    pub validator_findings: Vec<Finding>,
    pub package_findings: Vec<Finding>,
    pub semantic_diffs: Vec<DiffFinding>,
}

pub fn run_validators(profile: &UsdProfile, stage: &StageSnapshot) -> UsdReport;
pub fn verify_package(profile: &UsdProfile, package: &PackageSnapshot) -> Result<UsdReport>;
```

Bundle draft: `profile.toml`, `stage/`, `package-manifest.json`, `validator-results.json`, `semantic-diff.json`, `notes.md`.

# Security / safety model

- Default to path-normalized, manifest-first bundle capture rather than arbitrary asset trees.
- Record hashes and package entry metadata to preserve reproducibility.
- Avoid executing embedded scripts or tool plugins during evidence capture.
- Record exact validator and OpenUSD release versions.

# Maintenance & governance plan

- Keep core focused on IRs, validator adapters, and evidence bundles.
- Version profile packs separately from bundle layout.
- Use tiny synthetic fixtures and public sample assets first.
- Treat validator-version drift as a first-class release note item.

# Milestones

## 0.1
- USDA/USDC/USDZ snapshot loader
- package closure checks
- validator normalization

## 0.2
- semantic diffing
- profile lockfiles
- replayable evidence bundles

## 1.0
- stable `*.usdbundle.zip`
- public fixture corpus
- CI-ready validator profile packs

# Open questions

- How much of composition semantics can be normalized without embedding too much OpenUSD internals into the crate?
- Should package closure and validator normalization live in separate crates under one workspace?
- How much cross-tool metadata belongs in the core bundle versus optional adapters?

# Sources

- AOUSD Core Spec 1.0 and compliance framing: https://aousd.org/blog/foundations-of-open-3d-development-introducing-aousd-core-specification-1-0/
- OpenUSD toolset / `usdchecker`: https://openusd.org/release/toolset.html
- OpenUSD validator API: https://openusd.org/dev/api/class_usd_validator.html
- `openusd`: https://crates.io/crates/openusd
- `openusd-rs`: https://crates.io/crates/openusd-rs
