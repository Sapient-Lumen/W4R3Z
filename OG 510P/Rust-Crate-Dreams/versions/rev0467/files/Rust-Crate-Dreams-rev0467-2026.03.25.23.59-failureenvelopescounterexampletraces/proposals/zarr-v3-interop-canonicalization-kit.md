---
id: P-0227
title: Zarr v3 Interop & Canonicalization Kit
status: idea
domains: [data-formats, scientific-computing, storage, interop, canonicalization]
last_reviewed: 2026-03-05
evidence:
  - https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html
  - https://www.ogc.org/standards/zarr-storage-specification/
---

# Problem

Zarr is becoming a **de facto cloud-native chunked array** storage format across scientific and geospatial workflows, but Rust lacks a *default* crate that can:

- implement **Zarr v3 core** correctly (including metadata, chunk key encodings, codecs, and stores),
- produce **deterministic/canonical** representations suitable for PR diffs and reproducible builds,
- provide **interop-grade test fixtures** and explainable validation.

Existing Rust efforts tend to be partial (limited feature coverage, v2-only, or storage/backend constraints), leaving teams to build bespoke pipelines for each project.

# What it provides

Deliverables other people can rely on:

1. `zarr3` workspace (crates):
   - `zarr3-core`: spec-faithful metadata model + validation.
   - `zarr3-store`: store abstraction (FS, HTTP range, S3-compatible, Azure/GCS optional via feature flags).
   - `zarr3-codec`: codec pipeline (compressors, filters, sharding hooks per spec modules).
   - `zarr3-canon`: canonicalization + semantic diff tools.
   - `zarr3-cli`: `zarr3 validate|canon|diff|pack|unpack`.

2. **Evidence bundle format**: `*.zarrbundle.zip`
   - minimal, redactable, reproducible interop artifacts (inputs, normalized metadata, hashes, validation results).

3. Conformance/interop harness:
   - golden fixtures aligned to Zarr v3 core/codec/store modules,
   - fuzz + minimization hooks for metadata and chunk key decoding,
   - cross-implementation comparison mode (when other language toolchains are available in CI).

# Users & user stories

- **Geoscience / remote sensing teams**: “We store multi-TB arrays on object storage; we need deterministic metadata and a validator that catches subtle incompatibilities before data lands.”
- **ML/data platform engineers**: “We want a Rust-native reader/writer for chunked arrays without pulling in Python; also need canonical diffs for code review.”
- **Tool authors**: “We want a stable IR + codec/store plug-in surface for new backends.”

# Prior art (and why it’s insufficient)

- Zarr v3 spec is modular and evolving (core + codecs + stores + transformers). Many ecosystems implement subsets; Rust lacks a cohesive, spec-led, conformance-driven implementation.
- The OGC has endorsed a Zarr community standard (v2) and Zarr v3 is defined via its own specs set—both raise the stakes for interoperability and correctness.

# Design goals

- **Spec-first correctness** for v3 core (with extensibility for codecs/stores).
- **Canonical-by-default** output (stable JSON ordering, normalized paths, stable chunk keys).
- **Interop evidence**: bundles that let another team reproduce a failure without private data.
- **Composable architecture**: crates usable independently; CLI is thin glue.
- **Performance**: parallel chunk IO, streaming codecs, bounded memory.

# Non-goals

- Being a full analytics engine (no query optimizer / dataframe layer).
- Owning every compressor implementation (prefer adaptors to mature crates).

# Architecture & API sketch

```rust
// core: model + validation
pub struct ZarrArrayMeta { /* ... */ }
pub fn validate(meta: &ZarrArrayMeta) -> Result<ValidationReport>;

// store abstraction
pub trait Store {
  async fn get(&self, key: &str) -> Result<Bytes>;
  async fn put(&self, key: &str, data: Bytes) -> Result<()>;
  async fn list_prefix(&self, prefix: &str) -> Result<Vec<String>>;
}

// canonicalization
pub fn canon_metadata(meta_json: &[u8]) -> Result<Vec<u8>>;
pub fn diff_semantic(a: &ZarrHierarchy, b: &ZarrHierarchy) -> DiffReport;

// bundle
pub fn write_bundle(inputs: BundleInputs) -> Result<PathBuf>;
```

Bundle layout (initial):

- `manifest.json` (hashes, versions, environment)
- `normalized/` (canonical metadata, chunk key map)
- `reports/validate.json`
- `samples/` (optional small chunks or redacted stats)

# Security / safety model

- Explicit “no secret exfiltration” policy for bundles: default redaction and size caps.
- Store backends must support **allowlists** and **signed URL** use; never log credentials.

# Maintenance & governance plan

- Start with **v3 core + stores + key encodings**, ship a stable validator/canon CLI.
- Add codecs behind feature flags; require golden tests and fuzz corpora for each.
- Publish a clear compatibility matrix by Zarr v3 module.

# Milestones

1. **MVP (4–8 weeks)**
   - v3 core metadata parsing + validation
   - local FS store + HTTP range store
   - canonicalization + semantic diff
   - `zarrbundle` writer + minimal schema

2. **Interop (next)**
   - S3-compatible store
   - codec pipeline skeleton + a few common codecs
   - golden fixtures + fuzz targets

# Open questions

- Which codecs should be “tier-1” for MVP (beyond passthrough)?
- How to represent store capabilities and transformer pipelines in a stable IR?

# Sources

- Zarr v3 core specification (modules, goals). https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html
- OGC Zarr Storage Specification (community standard context/endorsement). https://www.ogc.org/standards/zarr-storage-specification/
