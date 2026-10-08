---
id: P-0410
title: E57 + LAS/LAZ + COPC Loss-Aware Interop Workbench Kit — scan-model locks, conversion receipts, and point-cloud loss accounting
status: idea
domains: [geospatial, lidar, point-clouds, interoperability, conversion, validation, robotics]
last_reviewed: 2026-03-06
evidence:
  - https://libe57.org/
  - https://www.ogc.org/standards/las/
  - https://copc.io/
  - https://docs.rs/e57
  - https://docs.rs/las
  - https://docs.rs/copc-rs
  - https://docs.rs/e57-to-las
---

# Problem

Rust’s geospatial and point-cloud substrate is quietly getting real. There is now a pure-Rust `e57` crate, mature LAS support in `las`, COPC support in `copc-rs`, and conversion tooling such as `e57-to-las`. Meanwhile, the actual ecosystem pain is not “can I parse bytes?” but “what did I lose or normalize when I crossed file families designed for different worlds?”

E57 is a vendor-neutral exchange/container format for point clouds, images, and metadata from 3D imaging systems. LAS/LAZ and COPC dominate adjacent LiDAR and cloud-optimized workflows. These ecosystems overlap, but they do not mean the same thing.

The painful failures happen at the seam between:

- **scanner/station-oriented E57 content and flatter LAS/COPC point-record models**,
- **embedded images, transforms, spherical metadata, and acquisition context that may not survive export**,
- **coordinate/reference assumptions and quantization/scale policies**,
- **conversion tools that say “success” while silently dropping structure**,
- and **teams that still compare file sizes or point counts when they really need explicit loss accounting.**

The missing Rust contribution is not another parser. It is a **loss-aware interop workbench** for scan-model locks, conversion receipts, and portable point-cloud evidence bundles.

# What it provides

- `pointcloud.lock` — pins source format family, target format family, coordinate/reference assumptions, quantization policy, and conversion profile.
- `scan-model-receipt` — normalized record of point-cloud groups, transforms, imagery, attributes, and metadata surfaces present in the source.
- `conversion-loss-report` — explicit statement of preserved, normalized, dropped, and inferred content across E57↔LAS/LAZ/COPC boundaries.
- `evidence-snapshot` — bounded point/metadata digest for reproducible review without shipping giant datasets.
- `cargo pointcloud-evidence` — emits `*.pointcloudbundle.zip` with locks, receipts, loss reports, and notes.

# What the crate should provide other people

1. **A boring receipt for point-cloud conversion work**.
2. **Explicit loss accounting** between scan-oriented and LiDAR-oriented formats.
3. **Pinned conversion assumptions** for CRS, quantization, transforms, and attributes.
4. **Small review artifacts** for CI, bug reports, and customer handoff.
5. **A coordination layer above existing Rust point-cloud crates.**

# Persona / who it’s for

- geospatial and survey software teams
- robotics / digital-twin ingestion pipelines
- AEC and reality-capture tool authors
- support engineers debugging conversion drift

# Users & user stories

- **Conversion-tool maintainer**: “Tell me exactly what my E57→COPC export normalized or dropped.”
- **Integrator**: “Pin the coordinate/scale assumptions so future exports are comparable.”
- **QA engineer**: “Diff two conversions and see whether the drift is meaningful or just expected normalization.”
- **Customer-support engineer**: “Share a compact loss report instead of a multi-gigabyte source file.”

# Prior art (and why it’s insufficient)

- `e57`, `las`, and `copc-rs` prove Rust can already read and write important file families.
- `e57-to-las` shows conversion demand is real.
- Official LAS and COPC materials define their own constraints and point-record expectations.

What Rust still lacks is a **shared artifact model** for scan semantics, conversion profiles, and loss receipts across these families.

# Design goals

1. **Loss-explicit** — every conversion must say what was preserved, normalized, dropped, or guessed.
2. **Model-aware** — E57 scan groups/images/transforms are first-class, not accidental baggage.
3. **Dataset-light** — evidence bundles should work without copying entire point clouds.
4. **Format-honest** — LAS/COPC constraints and E57 affordances must remain distinct.
5. **Pipeline-friendly** — usable in batch conversion and CI workflows.

# MVP surface

- Minimal types: `PointCloudLock`, `ScanModelReceipt`, `ConversionLossReport`, `EvidenceSnapshot`, `PointCloudBundle`
- Minimal functions:
  - `inspect_source()`
  - `convert_with_receipt()`
  - `diff_conversion()`
  - `write_bundle()`
- Feature flags:
  - `e57`
  - `las`
  - `copc`
  - `snapshots`
  - `redaction`

# Compatibility story

- Works above existing `e57`, `las`, `copc-rs`, and conversion tooling.
- Supports offline inspection of preexisting files as well as active conversion runs.
- Keeps huge binary payloads out of the stable artifact format via digests and samples.
- Separates format-specific metadata from normalized IR.

# Conformance & fixtures

- Goldens for imagery loss, transform flattening, attribute truncation, and quantization drift.
- Tiny corpora for E57 single-scan, multi-scan, and image-bearing files.
- Fixtures for E57→LAS, E57→COPC, and LAS/COPC roundtrips.
- Public mini-corpus with sampled points and metadata digests.

# Path to boring stability

- Stabilize the lockfile and loss-report schema before richer visualization.
- Start with source inspection and conversion receipts.
- Keep coordinate assumptions and quantization policies explicit.
- Resist drift into becoming a full point-cloud processing engine.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that inspect E57/LAS/COPC sources, pin conversion assumptions, emit explicit loss reports, and package compact `*.pointcloudbundle.zip` artifacts.

# De-risk plan

1. Start with E57 inspection plus E57→LAS receipts.
2. Add COPC only after the loss-report schema is stable.
3. Keep CRS/reference handling explicit even if it begins as attachment metadata.
4. Pilot on public mini-datasets before making bigger performance claims.

# Non-goals

- Not a full point-cloud analytics framework.
- Not a renderer.
- Not a replacement for existing format crates.
- Not a guarantee of perfectly lossless conversion where the formats disagree.

# Architecture & API sketch

```rust
pub struct PointCloudLock {
    pub source_family: String,
    pub target_family: String,
    pub quantization_policy: String,
    pub metadata_overlays: Vec<String>,
}

pub fn inspect_source(path: &std::path::Path) -> Result<ScanModelReceipt>;
pub fn convert_with_receipt(job: ConversionJob) -> Result<ConversionLossReport>;
pub fn diff_conversion(a: &ConversionLossReport, b: &ConversionLossReport) -> Vec<String>;
```

Bundle draft: `pointcloud.lock`, `scan-model.json`, `loss-report.json`, `snapshots/`, `notes.md`.

# Security / safety model

- Support digest-only or sampled-point evidence to avoid oversharing large or sensitive survey data.
- Preserve provenance of source/target files and conversion profiles.
- Mark inferred metadata explicitly.
- Keep binary evidence bounded and reviewable.

# Maintenance & governance plan

- Keep the core about inspection, loss reports, and bundles.
- Version format adapters independently if necessary.
- Publish a small public corpus with known-loss scenarios.
- Resist scope creep into a giant point-cloud platform.

# Milestones

## 0.1
- `pointcloud.lock`
- E57 inspection
- E57→LAS loss report

## 0.2
- COPC support
- snapshot/digest corpus
- conversion diff engine

## 1.0
- stable `*.pointcloudbundle.zip`
- documented compatibility policy for E57/LAS/COPC adapters
- CI-friendly conversion gates

# Open questions

- What is the smallest neutral IR that still makes scan-oriented loss visible?
- Which metadata belongs in first-class fields versus attached overlays?
- How should CRS/reference assumptions be represented when source files are incomplete or inconsistent?

# Sources

- libE57 overview: https://libe57.org/
- OGC LAS overview: https://www.ogc.org/standards/las/
- COPC spec site: https://copc.io/
- `e57`: https://docs.rs/e57
- `las`: https://docs.rs/las
- `copc-rs`: https://docs.rs/copc-rs
- `e57-to-las`: https://docs.rs/e57-to-las

