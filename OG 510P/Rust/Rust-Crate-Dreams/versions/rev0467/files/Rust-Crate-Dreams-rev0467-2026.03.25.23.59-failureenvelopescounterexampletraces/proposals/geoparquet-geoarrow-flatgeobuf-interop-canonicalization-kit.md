---
id: P-0377
title: GeoParquet + GeoArrow + FlatGeobuf Interop & Canonicalization Workbench Kit — CRS/profile locks, conversion-loss diffs, and portable geospatial evidence bundles
status: idea
domains: [geospatial, data-formats, interoperability, validation, tooling, analytics, storage]
last_reviewed: 2026-03-06
evidence:
  - https://geoparquet.org/releases/v1.1.0/
  - https://geoarrow.org/geoarrow-rs/rust/
  - https://geoarrow.org/news/release-0-2.html
  - https://flatgeobuf.org/
  - https://docs.rs/crate/geozero/latest
---

# Problem

Rust now has meaningful substrate for modern geospatial interchange: GeoParquet has a current spec, GeoArrow has a real Rust implementation, and FlatGeobuf remains attractive for feature-oriented streaming and web delivery. But the painful failures still happen at the seam between:

- **columnar and feature-stream encodings**,
- **WKB and native GeoArrow encodings**,
- **CRS / metadata declarations and actual payload semantics**,
- **spatial filtering and bounding-box expectations across formats**,
- and **“round-trip worked” claims that hide conversion loss or metadata drift**.

The missing Rust contribution is not another geospatial file reader. It is a **canonicalization and evidence workbench** that makes conversion-loss, metadata drift, and profile mismatches reviewable.

# What it provides

- `geo-profile.lock` — pins geometry encodings, CRS expectations, row-group / chunk assumptions, nullable/empty semantics, and optional producer quirks.
- `geo-irx` — a neutral IR for geometry columns, feature schemas, CRS declarations, envelope summaries, and lossy-conversion findings.
- `format-bridge` — adapters for GeoParquet, GeoArrow memory, and FlatGeobuf inputs/outputs.
- `loss-diff` — semantic diffs such as “same features, different CRS declaration”, “same shapes, downgraded dimensionality”, or “same rows, changed null/empty interpretation”.
- `cargo geo-evidence` — emits `*.geobundle.zip` with lockfile, normalized summaries, sample extracts, conversion findings, and notes.

# What the crate should provide other people

1. **A boring default artifact for geospatial interchange bugs**.
2. **Explicit CRS and encoding locks** instead of vague “supports GeoParquet / FlatGeobuf”.
3. **Loss accounting** when converting between GeoParquet, GeoArrow, and FlatGeobuf.
4. **Portable evidence bundles** for CI, issue trackers, and vendor-neutral debugging.
5. **A shared review surface** for Rust geospatial libraries without forcing one storage or execution engine.

# Persona / who it’s for

- Geospatial data-platform teams exchanging datasets across pipelines and clouds
- Rust maintainers building geospatial readers, writers, and compute engines
- Data engineering teams validating public-sector or environmental data deliveries
- Developers debugging spatial-filter, CRS, or schema drift across formats

# Users & user stories

- **Pipeline owner**: “Show me whether this conversion only changed layout, or also changed geometry semantics.”
- **Library maintainer**: “Run one fixture corpus across GeoParquet, FlatGeobuf, and in-memory GeoArrow adapters.”
- **Data consumer**: “Prove that this published GeoParquet file still matches the promised CRS/profile contract.”
- **Support engineer**: “Share a redacted, small bug bundle instead of a giant production dataset.”

# Prior art (and why it’s insufficient)

- GeoParquet 1.1.0 defines metadata, geometry encodings, and compatibility rules.
- GeoArrow 0.2 now has active Rust support, and the geoarrow-rs stack includes GeoParquet and FlatGeobuf-facing crates.
- FlatGeobuf remains strong for fast transport and feature collections.
- `geozero` and related GeoRust tools offer format bridges and conversions.

What Rust still lacks is a **boring default workbench** for format-aware profile locks, loss diffs, and evidence bundles that multiple teams can exchange.

# Design goals

1. **Semantics-first** — compare geometry meaning, not just bytes.
2. **CRS-explicit** — never hide CRS or axis/order assumptions.
3. **Loss-honest** — every conversion should be able to say what was preserved, changed, or dropped.
4. **Dataset-scalable** — summarize big artifacts without requiring giant attachments.
5. **Adapter-friendly** — reuse GeoRust substrate instead of replacing it.

# MVP surface

- Minimal types: `GeoProfileLock`, `GeometrySummary`, `ConversionFinding`, `GeoBundle`
- Minimal functions:
  - `inspect_dataset()`
  - `compare_profiles()`
  - `diff_conversion()`
  - `write_bundle()`
- Feature flags:
  - `geoparquet`
  - `geoarrow`
  - `flatgeobuf`
  - `sampling`
  - `redaction`

# Compatibility story

- Starts above existing GeoRust crates rather than replacing them.
- Can operate on sampled extracts when whole datasets are too large.
- Treats GeoParquet, GeoArrow, and FlatGeobuf support as adapters around one stable evidence schema.
- Keeps producer-specific quirks explicit in overlays instead of silently changing semantics.

# Conformance & fixtures

- Tiny fixtures for CRS drift, 2D/3D downgrade, WKB/native-encoding differences, null-vs-empty confusion, and bbox mismatches.
- Goldens for “same features, different metadata” and “same metadata, changed geometry semantics”.
- Sampling fixtures for large datasets where only envelopes/column stats/small extracts ship.
- Public fixture packs for cross-format round-trips and conversion-loss scenarios.

# Path to boring stability

- Stabilize lockfile, summary schema, and loss-diff categories before expanding adapters.
- Start with the most common failure surfaces: CRS, geometry encoding, dimensionality, empties/nulls, bbox, and schema drift.
- Keep the first release focused on evidence and conversion transparency, not full geospatial ETL ambition.
- Prefer deterministic sample extraction and summary generation for CI.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect GeoParquet, GeoArrow, or FlatGeobuf artifacts, pin a profile lock, run narrow conversion checks, and emit a `*.geobundle.zip` describing CRS, encoding, schema, and conversion-loss findings.

# De-risk plan

1. Start with metadata + sampled-geometry summaries before ambitious full-dataset canonicalization.
2. Keep CRS and geometry-loss reporting explicit from day one.
3. Use public, small fixture corpora rather than giant production datasets.
4. Let adapter quality and evidence format be the main trust surface.

# Non-goals

- Not a new GIS engine.
- Not a replacement for GeoRust compute libraries.
- Not a tile server or full ETL platform.
- Not a generic metadata catalog.

# Architecture & API sketch

```rust
pub struct GeoProfileLock {
    pub crs_policy: String,
    pub geometry_encoding: String,
    pub dimensionality_policy: String,
}

pub fn inspect_dataset(bytes: &[u8], format: GeoFormat) -> Result<DatasetReport>;
pub fn diff_conversion(a: &DatasetReport, b: &DatasetReport, lock: &GeoProfileLock) -> ConversionDiff;
```

Bundle draft: `geo-profile.lock`, `summary.json`, `conversion-findings.json`, `sample/`, `crs-report.json`, `notes.md`.

# Security / safety model

- Treat geospatial files and metadata as untrusted input.
- Support bounding-box and schema-only bundles when geometry values are sensitive.
- Record exact adapter and spec/profile versions in every bundle.
- Keep outputs deterministic enough for CI and public bug reports.

# Maintenance & governance plan

- Keep the core centered on profile locks, neutral IR, loss findings, and bundle format.
- Version format adapters independently where needed.
- Publish a small public corpus covering loss and metadata drift.
- Avoid turning the project into a giant general geospatial framework.

# Milestones

## 0.1
- dataset inspection
- profile lockfile
- conversion/loss report writer

## 0.2
- cross-format diffs
- sampling + redaction support
- richer CRS/encoding diagnostics

## 1.0
- stable `*.geobundle.zip`
- public fixture corpus
- documented compatibility and loss-accounting policy

# Open questions

- Which CRS and axis-order mismatches deserve hard failure versus warning status?
- How much geometry sampling is enough to make bundles useful without becoming huge?
- Which producer quirks belong in stable overlays versus transient notes?

# Sources

- GeoParquet 1.1.0: https://geoparquet.org/releases/v1.1.0/
- GeoArrow Rust crates: https://geoarrow.org/geoarrow-rs/rust/
- GeoArrow 0.2 release notes: https://geoarrow.org/news/release-0-2.html
- FlatGeobuf spec/project: https://flatgeobuf.org/
- `geozero`: https://docs.rs/crate/geozero/latest
