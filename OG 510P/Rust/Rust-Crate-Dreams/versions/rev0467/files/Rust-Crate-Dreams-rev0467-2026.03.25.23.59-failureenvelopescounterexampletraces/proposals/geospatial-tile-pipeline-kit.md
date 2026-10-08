---
id: P-0144
title: Geospatial Tile Pipeline Kit — PMTiles/COG/GeoParquet ETL + conformance bundles in Rust
status: idea
domains: [geospatial, data, formats, pipelines, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/protomaps/PMTiles/blob/main/spec/v3/spec.md
  - https://docs.protomaps.com/pmtiles/
  - https://docs.ogc.org/is/21-026/21-026.html
  - https://geoparquet.org/releases/v1.1.0/
  - https://geoarrow.github.io/geoarrow-rs/
  - https://github.com/georust/geo
  - https://crates.io/crates/pmtiles
needs:
  - A modern Rust “golden path” for serverless map data distribution and analytics interoperability.
  - A coherent ETL toolkit that treats formats as contracts and ships conformance fixtures.
  - End-to-end reproducibility: build once, verify anywhere (byte-for-byte where possible).
---

## What this crate should provide (to other people)

A **format-aware, artifact-first pipeline toolkit** for geospatial data that produces “map-ready” outputs with verifiable properties:
- `cargo geoetl` workflows to build/validate:
  - vector tiles → **PMTiles** archives (spec v3) for serverless distribution
  - rasters → **Cloud Optimized GeoTIFF (COG)** (OGC standard) for range-request reads
  - columnar vectors → **GeoParquet** with correct metadata + geometry encodings
- A stable `*.geobundle.zip` for reproducible bug reports and CI evidence (inputs, outputs, checksums, validator outputs).

## Scope and non-goals

**In-scope**
- Pipeline orchestration + validators + deterministic fixture generation.
- Interop adapters to existing Rust ecosystems (GeoRust, GeoArrow, Parquet/Arrow).

**Out of scope**
- Re-implementing GDAL in Rust.
- A full GIS GUI or tile server (focus on artifacts and correctness).

## Design sketch

### Core abstractions
- **DatasetHandle**: source (S3/HTTP/file), schema, CRS, and chunking strategy.
- **Transform graph**: explicit nodes (reproject, simplify, clip, tile, encode).
- **Validators**: spec-checkers that output machine-readable results.

### Conformance and evidence
- Conformance fixtures:
  - “Known-good” tiny datasets per format (with expected metadata + invariants).
  - Roundtrip corpora for GeoArrow/GeoParquet conversions.
- `geoetl-report.json`:
  - deterministic summary (counts, bounds, CRS, tile matrix, compression stats)
  - format-specific validator results

### Artifact format: `geobundle.zip`
- `manifest.toml` (tool versions, CRS, tiling scheme, bounds)
- `inputs/` (small, licensed fixtures or synthetic generators)
- `outputs/` (PMTiles/COG/GeoParquet)
- `reports/` (`geoetl-report.json`, validator logs)

## MVP → v1 plan

**MVP**
- PMTiles writer/validator pipeline with `geobundle.zip`
- COG validator runner (structure + overview rules)
- GeoParquet metadata validator + minimal writer adapter

**v1**
- CRS + tiling policy profiles
- Deterministic “tile diffs” (semantic diffs beyond bytes)
- Multi-backend IO (S3 range reads; HTTP range reads)

## Adoption strategy

- Publish as a toolbox crate + `cargo geoetl` binary.
- Provide “profiles” for common use cases:
  - web map distribution (PMTiles)
  - cloud raster catalogs (COG)
  - analytics interchange (GeoParquet)
- Make validators usable standalone so other crates can depend on correctness checks.
