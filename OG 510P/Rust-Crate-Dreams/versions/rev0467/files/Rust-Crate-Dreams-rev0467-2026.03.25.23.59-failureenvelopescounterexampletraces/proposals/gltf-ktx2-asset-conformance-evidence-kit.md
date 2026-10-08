---
id: P-0347
title: glTF 2.0 + KTX 2.0 Asset Conformance & Evidence Kit — validator-aware asset profiles, texture/package checks, and portable repro bundles
status: idea
domains: [graphics, gamedev, 3d, assets, tooling, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
  - https://github.khronos.org/glTF-Validator/
  - https://github.khronos.org/KTX-Specification/ktxspec.v2.html
  - https://docs.rs/gltf
  - https://docs.rs/gltf-validator
  - https://docs.rs/ktx2
---

# Problem

Rust now has real glTF substrate and even a wrapper around the official Khronos validator, but production asset failures still cluster at the seam between **core scene semantics, extension expectations, and external texture/package behavior**:

- a `.glb` that validates but still fails because a runtime or marketplace assumes a narrower extension/profile subset,
- KTX2 / Basis texture payloads that are structurally present but operationally wrong for the target pipeline,
- “works in engine A, breaks in engine B” incidents with no portable bundle explaining whether the fault lives in scene graph, textures, extensions, URI/package layout, or validator findings,
- batch validation outputs that are hard to diff meaningfully across exporter versions,
- and private asset triage workflows that devolve into screenshots, one-off scripts, and large binary handoffs.

The worthy missing crate is not “yet another loader.” It is a **validator-first asset conformance and evidence kit** that turns glTF/KTX2 compatibility failures into stable, replayable, explainable artifacts.

# What it provides

- `gltf-ir` — a canonical Rust IR for scenes, buffers, images, materials, extensions, referenced resources, validator findings, and texture-container metadata.
- `gltf-profile` — lockfiles pinning allowed core features, extensions, required MIME/container shapes, texture/transcode assumptions, and target-runtime quirks.
- `gltf-validator-adapter` — normalized import of Khronos glTF Validator results into a stable finding vocabulary.
- `ktx-check` — KTX2-specific checks for mip chains, supercompression/transcode expectations, metadata, and asset-package linkage.
- `gltf-diff` — semantic diffs such as “same topology, changed material graph”, “new extension required”, or “texture payload moved from PNG to KTX2 with changed transcode assumptions”.
- `cargo gltf-evidence` — emit `*.gltfbundle.zip` for CI, marketplace submissions, vendor handoff, or game-engine support cases.

# What the crate should provide other people

1. **A boring default for asset compatibility triage** that does not depend on one specific engine or DCC tool.
2. **A way to pin export/profile assumptions in Git** instead of rediscovering them from validator JSON and tribal lore.
3. **Portable evidence bundles** that can be shared without shipping an entire private project tree.
4. **Semantic diffs over asset revisions** rather than endless byte-level churn in binary blobs.
5. **A bridge between validator output and real production decisions** like marketplace acceptance, runtime fallback, and regression gating.

# Persona / who it’s for

- Engine and renderer maintainers
- Asset pipeline / tools engineers
- Marketplace ingestion teams
- Technical artists debugging export drift
- Rust developers building 3D viewers, validators, or converters

# Users & user stories

- **Pipeline engineer**: “Tell me whether this regression came from a new required extension, a KTX2 payload issue, or a validator finding that turned from warning to error.”
- **Marketplace QA**: “Accept only assets matching our supported extension and texture profile, and produce a shareable findings bundle when rejecting them.”
- **Engine maintainer**: “Diff exporter version N and N+1 on a corpus and cluster changes by semantics, not by raw file bytes.”
- **Tool author**: “Wrap the official validator but enrich it with package, texture, and target-profile diagnostics.”

# Prior art (and why it’s insufficient)

- Khronos publishes the official **glTF 2.0 specification** and the **glTF Validator**.
- Khronos also publishes the **KTX 2.0** specification for GPU-ready texture containers.
- Rust has real substrate in `gltf`, `gltf-validator`, and `ktx2`.
- But there is still no boring-default Rust crate family for **profile pinning + validator normalization + KTX/package-aware semantic diffs + portable evidence bundles**.

# Design goals

1. **Validator-first** — wrap and preserve official validator findings rather than inventing a parallel truth surface.
2. **Asset-pipeline aware** — package layout, external resources, and texture containers must be first-class.
3. **Engine-neutral** — useful for Bevy, wgpu-native tools, proprietary engines, and marketplace pipelines alike.
4. **Semantic over bytewise diffs** — findings should explain asset compatibility in domain terms.
5. **Small-share evidence** — bundles should prefer manifests, findings, hashes, and reduced fixtures over giant binary dumps.

# MVP surface

- Minimal types: `AssetSnapshot`, `TextureSnapshot`, `GltfProfile`, `ValidationReport`, `DiffFinding`
- Minimal functions:
  - `load_asset()`
  - `run_validator()`
  - `check_ktx()`
  - `diff_assets()`
  - `write_bundle()`
- Feature flags:
  - `validator`
  - `ktx2`
  - `serde`
  - `image-hashes`
  - `redaction`

# Compatibility story

- MVP should target **glTF 2.0** plus KTX2-backed texture checks first.
- The crate should complement existing loaders and importers, not replace rendering engines.
- Extension support should be profile-driven and explicitly partial where needed.
- Validation bundles should work whether assets are `.gltf` + external files or `.glb` packages.

# Conformance & fixtures

- Tiny public fixture corpus covering plain `.glb`, external-resource `.gltf`, and KTX2-heavy assets.
- Goldens for extension enable/disable drift.
- Reduced repro fixtures for missing buffers, broken URIs, incompatible KTX2 metadata, and validator-warning escalation.
- Corpus adapters that normalize official validator findings into stable snapshots.

# Path to boring stability

- Stabilize the profile format and semantic finding vocabulary first.
- Keep KTX2 checks narrowly focused on package/conformance semantics before adding heavyweight transcoding ambitions.
- Freeze bundle layout only after proving small bundles can still explain real incidents.
- Add extension-specific enrichments only after the core report model stops thrashing.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A CLI and library that load a glTF asset, run the official Khronos validator, inspect KTX2-linked resources, normalize findings into a stable report, and emit a compact `*.gltfbundle.zip` suitable for CI failures or vendor handoff.

# De-risk plan

1. Start with asset manifests, validator wrapping, and file/link integrity before deep material semantics.
2. Keep texture checks metadata- and structure-focused before promising universal transcoding support.
3. Use a tiny public corpus and minimized fixtures.
4. Separate target-profile policy from core IR so engine-specific quirks do not infect the base crate.

# Non-goals

- Not a renderer or scene runtime.
- Not a DCC exporter.
- Not a full transcoding farm.

# Architecture & API sketch

```rust
pub struct ValidationReport {
    pub profile_id: String,
    pub validator_findings: Vec<Finding>,
    pub package_findings: Vec<Finding>,
    pub texture_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn run_validator(asset: &AssetSnapshot, profile: &GltfProfile) -> Result<ValidationReport>;
pub fn check_ktx(asset: &AssetSnapshot, profile: &GltfProfile) -> Result<Vec<Finding>>;
```

Bundle draft: `asset.json`, `profile.toml`, `validator.json`, `textures.json`, `resource-hashes.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat all asset inputs as untrusted.
- Prefer hash-and-reference capture over bundling raw binaries by default.
- Separate bundle metadata from optional binary attachments.
- Record exact validator and profile versions for reproducibility.

# Maintenance & governance plan

- Keep the core focused on IRs, adapters, and evidence bundles.
- Version profiles separately from bundle layout.
- Encourage public fixture corpora and reduced repro assets.
- Keep engine-specific policy packs outside the core crate tree where possible.

# Milestones

## 0.1
- asset/resource manifest loader
- validator adapter
- bundle writer

## 0.2
- KTX2 checks
- semantic diffs
- profile packs

## 1.0
- stable `*.gltfbundle.zip`
- public fixture corpus
- documented compatibility policy for extensions and texture profiles

# Open questions

- How much KTX2/transcoding knowledge belongs in core versus optional adapters?
- Should profile packs be engine-specific, marketplace-specific, or both?
- What minimum artifact subset is enough for useful vendor handoff?

# Sources

- glTF 2.0 specification: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- official glTF Validator: https://github.khronos.org/glTF-Validator/
- KTX 2.0 specification: https://github.khronos.org/KTX-Specification/ktxspec.v2.html
- `gltf`: https://docs.rs/gltf
- `gltf-validator`: https://docs.rs/gltf-validator
- `ktx2`: https://docs.rs/ktx2
