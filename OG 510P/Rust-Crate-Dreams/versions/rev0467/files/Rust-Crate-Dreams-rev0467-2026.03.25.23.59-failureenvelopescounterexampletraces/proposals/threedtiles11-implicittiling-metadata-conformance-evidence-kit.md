---
id: P-0376
title: 3D Tiles 1.1 + Implicit Tiling + Metadata Conformance & Evidence Kit — tileset/profile locks, subtree diagnostics, and portable 3D geospatial bug bundles
status: idea
domains: [geospatial, 3d, visualization, standards, interoperability, testing, digital-twins]
last_reviewed: 2026-03-06
evidence:
  - https://docs.ogc.org/cs/22-025r4/22-025r4.html
  - https://portal.ogc.org/public_ogc/compliance/implementing.php?specid=1255
  - https://github.com/3DGI/tyler
  - https://crates.io/crates/geo-tileset
  - https://crates.io/crates/etiles
  - https://crates.io/crates/tyler
---

# Problem

Rust has early but real 3D Tiles substrate, and the standard now spans metadata, implicit tiling, and glTF-adjacent content in ways that make “it renders” an inadequate correctness test. The painful failures sit at the seam between:

- `tileset.json` structure and profile assumptions,
- implicit-tiling subtree generation and traversal,
- metadata classes/properties and the content they allegedly describe,
- geometric content and the packaging/index layers around it,
- and cross-tool compatibility claims that are hard to prove from screenshots alone.

The missing Rust contribution is not another 3D engine. It is a **conformance-and-evidence crate** for tileset structure, subtree semantics, metadata integrity, and reproducible bug bundles.

# What it provides

- `tileset.lock` — pins 3D Tiles/profile assumptions, extension usage, metadata schema expectations, and tiling rules.
- `tiles-irx` — a neutral IR for tilesets, subtrees, availability, metadata classes, content references, and validation findings.
- `subtree-audit` — checks implicit-tiling availability, subtree boundaries, content-address/path consistency, and metadata linkage.
- `tileset-diff` — semantic diffs such as “same city model, different subtree shape”, “same content, different metadata surface”, or “same root but incompatible profile assumptions”.
- `cargo 3dtiles-evidence` — emits `*.3dtilesbundle.zip` with lockfile, redacted tileset snapshot, normalized findings, and human notes.

# What the crate should provide other people

1. **A boring default artifact for 3D Tiles interoperability bugs**.
2. **Explicit tileset/profile locks** instead of vague “supports 3D Tiles”.
3. **Subtree and metadata diagnostics** that explain rendering/selection failures.
4. **Portable evidence across generators, validators, and viewers**.
5. **A bridge from emerging Rust geospatial substrate to conformance workflows**.

# Persona / who it’s for

- Geospatial tooling authors in Rust
- Digital-twin and 3D city pipeline engineers
- Teams converting datasets into 3D Tiles outputs
- Viewer/integration developers debugging compatibility issues

# Users & user stories

- **Pipeline engineer**: “Tell me whether this bug is in subtree availability, metadata, or content references.”
- **Viewer author**: “Compare two tilesets semantically without depending on screenshots.”
- **Conversion maintainer**: “Ship a compact repro bundle for a failing generated tileset.”
- **Standards implementer**: “Pin the subset of 3D Tiles/extensions we actually claim to support.”

# Prior art (and why it’s insufficient)

- OGC publishes the 3D Tiles 1.1 standard and tracks implementations.
- Rust has generator/parser footholds in projects such as `tyler`, `geo-tileset`, and `etiles`.
- These pieces are promising, but they do not yet form a shared, portable **evidence-grade** conformance layer.

What is missing is a Rust-native crate for **tileset/profile locks, subtree audits, semantic diffs, and bug bundles**.

# Design goals

1. **Tileset-first** — package/index/metadata correctness matters as much as geometry.
2. **Implicit-tiling aware** — subtree semantics are a first-class review surface.
3. **Metadata-honest** — mismatches between schemas and content must be explainable.
4. **Viewer-neutral** — evidence should outlive any one renderer.
5. **Deterministic** — bundle generation should be CI-friendly.

# MVP surface

- Minimal types: `TilesetLock`, `TilesetReport`, `SubtreeFinding`, `MetadataFinding`, `TilesBundle`
- Minimal functions:
  - `inspect_tileset()`
  - `audit_subtrees()`
  - `diff_tilesets()`
  - `write_bundle()`
- Feature flags:
  - `tileset-json`
  - `implicit-tiling`
  - `metadata`
  - `redaction`
  - `recording`

# Compatibility story

- Complements existing Rust crates instead of replacing them.
- Can begin with `tileset.json`, metadata, and subtree surfaces before deeper geometry checks.
- Treats viewers/converters as adapters or comparison targets.
- Keeps the bundle/lockfile schema stable while generator/viewer adapters evolve.

# Conformance & fixtures

- Tiny fixtures for invalid availability bitstreams, bad subtree boundaries, missing content references, and metadata-class drift.
- Goldens for “same source, different subtree layout” and “same geometry, different metadata semantics”.
- Redaction tests for path rewriting and content stripping while preserving structure.
- Public profile packs for narrow extension combinations as the ecosystem matures.

# Path to boring stability

- Stabilize lockfile, IR, and finding taxonomy before chasing every extension.
- Start with structure/subtree/metadata conformance, not rendering.
- Publish a small public corpus of failing and valid tilesets.
- Keep viewer/generator integrations modular.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that inspect one 3D Tiles dataset, validate a pinned structural/profile surface, and emit a `*.3dtilesbundle.zip` with subtree findings, metadata diffs, and a compact reproducible snapshot.

# De-risk plan

1. Start with tileset/subtree/metadata inspection before deeper geometry semantics.
2. Keep profile/extension support narrow and explicit.
3. Use tiny public fixtures rather than large city datasets.
4. Treat generator/viewer disagreement as normalized findings, not as proof that one side is “correct”.

# Non-goals

- Not a 3D renderer.
- Not a full geospatial tiling pipeline.
- Not a replacement for every validator or viewer.
- Not a giant digital-twin platform.

# Architecture & API sketch

```rust
pub struct TilesetLock {
    pub profile: String,
    pub extensions: Vec<String>,
    pub metadata_policy: MetadataPolicy,
}

pub fn inspect_tileset(path: &Path) -> Result<TilesetReport>;
pub fn diff_tilesets(a: &TilesetReport, b: &TilesetReport) -> TilesetDiff;
```

Bundle draft: `tileset.lock`, `tileset.json`, `subtrees/`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat tilesets, metadata, and subordinate assets as untrusted input.
- Support redaction or path-rewriting of content while preserving structural evidence.
- Record validator/adapter versions in every bundle.
- Keep outputs deterministic enough for CI and issue exchange.

# Maintenance & governance plan

- Keep the core centered on lockfiles, findings, diffs, and bundle semantics.
- Version extension-specific adapters separately where practical.
- Publish a small public corpus focused on subtree and metadata seams.
- Avoid drifting into a broad visualization engine.

# Milestones

## 0.1
- tileset inspection
- lockfile schema
- subtree findings

## 0.2
- metadata audits
- semantic diffs
- redaction support

## 1.0
- stable `*.3dtilesbundle.zip`
- public fixture corpus
- documented compatibility guarantees for supported profile surfaces

# Open questions

- Which extension/profile combinations belong in the MVP versus later packs?
- How much of metadata/class semantics can be normalized without overfitting one toolchain?
- What is the smallest public corpus that still catches real implicit-tiling failures?

# Sources

- OGC 3D Tiles 1.1 specification: https://docs.ogc.org/cs/22-025r4/22-025r4.html
- OGC implementation database entry: https://portal.ogc.org/public_ogc/compliance/implementing.php?specid=1255
- `tyler` repository: https://github.com/3DGI/tyler
- `geo-tileset`: https://crates.io/crates/geo-tileset
- `etiles`: https://crates.io/crates/etiles
- `tyler` crate: https://crates.io/crates/tyler
