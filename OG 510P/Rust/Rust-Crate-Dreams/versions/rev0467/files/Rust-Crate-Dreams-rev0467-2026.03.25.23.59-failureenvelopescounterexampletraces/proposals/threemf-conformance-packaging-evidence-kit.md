---
id: P-0325
title: 3MF Conformance & Packaging Evidence Kit — extension-aware model validation, package diffs, and reproducible additive-manufacturing bug bundles
status: idea
domains: [manufacturing, additive-manufacturing, 3mf, packaging, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://3mf.io/spec/
  - https://3mf.io/spec/core-v1-3-0/
  - https://github.com/3MFConsortium/test_suites
  - https://docs.rs/lib3mf
  - https://docs.rs/threemf
  - https://github.com/sscargal/lib3mf-rs
---

# Problem

Rust now has real 3MF momentum, but the painful manufacturing failures do not stop at “can we read the ZIP container?” They happen at the packaging and extension seam:

- package relationships and resources that are valid enough to open but not portable enough to trust,
- extension usage that degrades silently across slicers and printers,
- beam-lattice/material/slice/signature assumptions drifting between tools,
- and support cases that still circulate as giant model files plus “works in slicer A, fails in slicer B.”

The worthy crate contribution is a **3MF conformance and packaging evidence kit** that turns 3MF documents into deterministic, extension-aware, diffable artifacts tied to real conformance suites.

# What it provides

- `threemf-ir` — canonical IR for package parts, relationships, resources, build items, metadata, geometry references, and extension usage.
- `threemf-profile` — lockfiles pinning core/extension assumptions, allowable extension sets, packaging policies, and downstream compatibility targets.
- `threemf-verify` — structural, packaging, and extension-aware semantic checks.
- `threemf-diff` — explainable diffs: “resource moved packages”, “extension required by model no longer declared”, “beam lattice downgraded to mesh”, “signature material changed”.
- `threemf-suite` — adapters for official 3MF conformance test suites and local corpora.
- `cargo threemf` — emit `*.3mfbundle.zip` for CAD/slicer/printer compatibility bugs and CI regressions.

# What the crate should provide other people

1. **A boring-default way to compare 3MF packages semantically**.
2. **Profile lockfiles** for the subset of 3MF and extensions a workflow depends on.
3. **Conformance-suite adapters** that make official tests feel native in Rust workflows.
4. **Portable, redactable issue bundles** for toolchain disagreements.
5. **A bridge from parser/writer crates to manufacturing-grade validation**.

# Persona / who it’s for

- CAD and slicer developers
- Additive-manufacturing pipeline teams
- Printer-vendor QA engineers
- Rust library authors working on 3MF tooling
- CI owners maintaining geometry/package regression suites

# Users & user stories

- **Slicer engineer**: “Tell me whether this failure is packaging, extension support, or geometry semantics.”
- **Printer vendor**: “Replay the exact package and conformance case that broke our import pipeline.”
- **Pipeline maintainer**: “Diff the exported 3MF against last release in extension-aware terms.”
- **Library author**: “Run a Rust-native subset of the official conformance suite in CI.”

# Prior art (and why it’s insufficient)

- The 3MF Consortium publishes the core specification plus extensions and now ships conformance test suites.
- Rust substrate exists in `lib3mf`, `threemf`, and newer projects like `lib3mf-rs`.
- That means the parser/writer frontier is no longer empty.
- What remains missing is a shared Rust layer for **profile pinning + conformance-suite ingestion + semantic package diffing + issue bundles**.

# Design goals

1. **Package-first** — 3MF portability depends on relationships/resources, not only XML snippets.
2. **Extension-aware** — core-only validation is not enough for real AM workflows.
3. **Conformance-aligned** — official suite materials should shape the crate’s worldview.
4. **Deterministic normalization** — the same package should normalize the same way every time.
5. **Toolchain-neutral** — useful across CAD, slicers, printers, and archives.

# MVP surface

- Minimal types: `PackageModel`, `ThreeMfProfile`, `ConformanceCase`, `ThreeMfReport`, `PackageDelta`
- Minimal functions:
  - `read_package()`
  - `verify_package()`
  - `diff_package()`
  - `run_case()`
  - `write_bundle()`
- Feature flags:
  - `core`
  - `materials`
  - `beam-lattice`
  - `slice`
  - `secure-content`
  - `suite`

# Compatibility story

- Interoperates with existing parser/writer crates as adapters.
- Treats official conformance-suite inputs as first-class fixtures.
- Intentionally avoids becoming a CAD kernel or slicer.

# Conformance & fixtures

- Official 3MF conformance suites.
- Small synthetic packages for relationship/resource edge cases.
- Extension-focused fixtures for beam lattice, slice, secure content, and materials.
- Cross-tool normalization fixtures for deterministic diffing.

# Path to boring stability

- Start with package and manifest semantics before complex geometry analysis.
- Freeze the normalization and bundle format early.
- Add extension modules only when each has a public fixture corpus.
- Keep mesh-heavy inspection optional and adapter-based.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A tool that ingests a `.3mf` file, verifies package/resource/extension integrity against a pinned profile, optionally runs an official conformance case, and emits a `*.3mfbundle.zip` with normalized package views and explainable findings.

# De-risk plan

1. Make packaging and relationships the first-class MVP, not mesh geometry perfection.
2. Consume official suite cases before inventing custom ones.
3. Support only a small extension subset first.
4. Validate normalization against at least two Rust parser/writer backends.

# Non-goals

- Not a CAD authoring environment.
- Not a slicer or printer firmware stack.
- Not a full geometry kernel.

# Architecture & API sketch

```rust
pub struct ThreeMfReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub package_findings: Vec<PackageFinding>,
    pub extension_findings: Vec<ExtensionFinding>,
    pub diffs: Vec<PackageDelta>,
}

pub fn verify_package(profile: &ThreeMfProfile, model: &PackageModel) -> ThreeMfReport;
```

Bundle draft: `profile.toml`, `original/model.3mf`, `normalized/package.json`, `resources/index.json`, `verdicts.json`, `diff.json`, `suite-results.json`, `notes.md`.

# Security / safety model

- Bound decompression and XML parsing.
- Treat signatures/encryption metadata carefully; raw sensitive payloads should be optional.
- Preserve provenance hashes for each package part.
- Keep large geometry blobs optional in bundles.

# Maintenance & governance plan

- Pin spec and extension versions explicitly in profile packs.
- Map official suite cases to stable IDs.
- Publish synthetic issue corpora for package-level failures.
- Keep extension modules separate so support can grow incrementally.

# Milestones

## 0.1
- Package IR
- Profile lockfiles
- Core packaging verification

## 0.2
- Suite adapters
- Semantic package diffs
- Initial extension modules

## 1.0
- Stable `*.3mfbundle.zip`
- Cross-backend normalization guarantees
- CI-ready conformance and regression workflows

# Open questions

- How much geometry semantics belongs in core versus specialized adapters?
- Should secure-content and signatures stay metadata-only in MVP?
- Can extension support remain modular without fragmenting the user experience?

# Sources

- 3MF specification hub: https://3mf.io/spec/
- 3MF core page: https://3mf.io/spec/core-v1-3-0/
- 3MF conformance test suites: https://github.com/3MFConsortium/test_suites
- `lib3mf`: https://docs.rs/lib3mf
- `threemf`: https://docs.rs/threemf
- `lib3mf-rs`: https://github.com/sscargal/lib3mf-rs
