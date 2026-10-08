---
id: P-0353
title: OME-Zarr / NGFF 0.5 Conformance & Dataset Evidence Kit — metadata/profile locks, validator wrapping, and reproducible bioimaging bug bundles
status: idea
domains: [bioimaging, science-data, cloud-formats, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://ngff-spec.readthedocs.io/
  - https://ome.github.io/ome-ngff-validator/
  - https://github.com/ome/ngff-spec
  - https://docs.rs/ome_zarr_metadata
  - https://docs.rs/zarrs
---

# Problem

Rust now has credible Zarr and OME-Zarr building blocks, but real interoperability failures in bioimaging datasets usually happen above simple JSON or chunk I/O:

- metadata may be syntactically valid but still violate group-role or multiscale expectations,
- datasets drift between OME-Zarr / NGFF versions or optional structures,
- labels, wells, plates, and image groups get mislinked,
- cloud-layout choices make a dataset technically readable yet operationally broken,
- and validator output is rarely turned into a stable, shareable Rust artifact for CI or handoff.

The missing Rust contribution is a **validator-wrapping conformance and evidence kit** for OME-Zarr datasets, not another raw Zarr reader.

# What it provides

- `ngff-ir` — canonical Rust IR for OME-Zarr group roles, multiscales, labels, tables, wells, plates, and selected storage metadata.
- `ngff-profile` — lockfiles that pin supported NGFF / OME-Zarr surfaces, optional features, and environment assumptions.
- `validator-adapter` — normalized import of OME-NGFF validator findings into stable Rust reports.
- `dataset-check` — lightweight structural checks spanning parent/child group links and selected chunk/layout assumptions.
- `ngff-diff` — semantic diffs such as “same image data, changed multiscale metadata”, “label target drift”, or “well/plate linkage regression”.
- `cargo ngff-evidence` — emit `*.omezarrbundle.zip` for CI, repository ingest, or cross-tool debugging.

# What the crate should provide other people

1. **A boring default artifact for OME-Zarr interoperability bugs**.
2. **Version-pinned dataset expectations in Git**, not just screenshots from viewers.
3. **One place to normalize validator output** and add a few Rust-native cross-object checks.
4. **Semantic diffs for dataset revisions** that distinguish metadata drift from storage drift.
5. **Compact shareable bundles** for public fixtures or redacted private datasets.

# Persona / who it’s for

- Bioimaging-tool maintainers
- Repository / portal ingestion teams
- Rust developers building microscopy and image-data infrastructure
- QA teams validating conversion pipelines
- Scientists or platform engineers debugging cross-tool dataset issues

# Users & user stories

- **Converter maintainer**: “Show me whether the failure is multiscales metadata, label linkage, or storage/layout drift.”
- **Repository operator**: “Normalize validator results and save a compact bundle for dataset-ingest failures.”
- **CI owner**: “Gate export changes on semantic findings instead of brittle text diffs of `.zattrs`.”
- **Cross-tool debugger**: “Send a minimized dataset bundle that reproduces the viewer/importer bug.”

# Prior art (and why it’s insufficient)

- OME publishes the **NGFF / OME-Zarr** specification and validator surfaces.
- The `ome/ngff-spec` repository already contains **conformance-test** framing.
- Rust has real substrate in `ome_zarr_metadata`, `zarrs`, and `zarrs_tools`.
- But there is still no boring-default Rust crate family for **profile locks + validator normalization + semantic diffs + portable evidence bundles**.

# Design goals

1. **Validator-first** — wrap the official validator instead of pretending Rust should replace it on day one.
2. **Dataset-structure aware** — not just metadata-schema checking.
3. **Version-pinned** — record exact spec / validator / profile versions.
4. **Cloud-layout aware** — include enough store/chunk context to debug real failures.
5. **Minimizable** — evidence should allow excerpted or synthetic bundles when full datasets are too large.

# MVP surface

- Minimal types: `NgffNode`, `DatasetRole`, `NgffProfile`, `NgffReport`, `NgffDiffFinding`
- Minimal functions:
  - `load_node()`
  - `run_validator()`
  - `check_links()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `validator`
  - `zarr3`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target OME-Zarr / NGFF 0.5 style surfaces first and clearly pin any 0.4 compatibility behavior.
- The crate should complement `zarrs` and metadata crates rather than replace them.
- Viewer- or repository-specific policy packs can remain optional adapters.
- The core should remain useful for local filesystems and object stores alike.

# Conformance & fixtures

- Tiny public image, labels, and well/plate fixtures.
- Goldens for broken multiscales metadata, orphan labels, wrong axes metadata, and parent/child linkage drift.
- Sampled storage fixtures that avoid shipping large private arrays.
- Normalizers for official validator output and conformance-test expectations.

# Path to boring stability

- Stabilize group-role IR and findings vocabulary before broadening feature coverage.
- Keep early scope to a small set of dataset structures.
- Freeze bundle layout only after it works for CI, repository ingest, and viewer bug handoff.
- Add richer storage-profile packs only after the core model proves durable.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect an OME-Zarr dataset, run the official validator, normalize the findings, add a few cross-object checks, and emit a compact `*.omezarrbundle.zip` with enough structure to reproduce common interoperability failures.

# De-risk plan

1. Start with metadata and structural checks before attempting heavy data-content validation.
2. Use only tiny public fixtures in the first corpus.
3. Normalize official validator findings before inventing many custom rules.
4. Keep object-store adapters optional.

# Non-goals

- Not a viewer.
- Not an image-analysis engine.
- Not a full bioimaging repository.
- Not a replacement for general-purpose Zarr crates.

# Architecture & API sketch

```rust
pub struct NgffReport {
    pub spec_version: String,
    pub validator_version: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<NgffDiffFinding>,
}

pub fn run_validator(profile: &NgffProfile, root: &NgffNode) -> Result<NgffReport>;
pub fn check_links(root: &NgffNode) -> Vec<Finding>;
```

Bundle draft: `profile.toml`, `tree.json`, `zattrs.json`, `validator.json`, `links.json`, `diff.json`, `excerpt-manifest.json`, `notes.md`.

# Security / safety model

- Treat stores and metadata as untrusted inputs.
- Default to metadata- and structure-first bundles, not full pixel payloads.
- Support store URL/token redaction.
- Record exact spec and validator versions in every bundle.

# Maintenance & governance plan

- Keep core focused on IRs, findings, and bundle formats.
- Version profile packs separately from the library.
- Grow a small public corpus that mirrors common OME-Zarr structures.
- Avoid coupling to one viewer or one repository implementation.

# Milestones

## 0.1
- metadata loader
- validator adapter
- bundle writer

## 0.2
- cross-object linkage checks
- semantic diffs
- profile packs

## 1.0
- stable `*.omezarrbundle.zip`
- public fixture corpus
- documented policy for spec / validator drift

# Open questions

- Which optional NGFF structures belong in core versus profile packs?
- What minimum excerpt format is enough for private-dataset debugging?
- How much storage-layout checking should live in core before the scope becomes “generic Zarr doctor”?

# Sources

- NGFF / OME-Zarr specification: https://ngff-spec.readthedocs.io/
- OME-NGFF validator: https://ome.github.io/ome-ngff-validator/
- `ome/ngff-spec`: https://github.com/ome/ngff-spec
- `ome_zarr_metadata`: https://docs.rs/ome_zarr_metadata
- `zarrs`: https://docs.rs/zarrs
- `zarrs_tools`: https://docs.rs/zarrs_tools
