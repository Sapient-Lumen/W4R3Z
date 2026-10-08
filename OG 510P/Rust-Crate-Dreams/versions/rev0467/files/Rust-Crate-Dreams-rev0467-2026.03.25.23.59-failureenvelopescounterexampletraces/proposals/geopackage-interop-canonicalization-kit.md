---
id: P-0226
title: GeoPackage Interop & Canonicalization Kit — stable GeoPackage I/O, extension management, and diffable bundles
status: idea
domains: [geospatial, sqlite, ogc, geopackage, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.ogc.org/standards/geopackage/
  - https://www.geopackage.org/
  - https://www.geopackage.org/spec/
  - https://crates.io/crates/gpkg
  - https://github.com/georust/geozero
needs:
  - A modern, well-tested Rust GeoPackage implementation that is extension-aware, works with common GIS tools, and supports canonical diffs for review/CI.
  - A way to bundle a minimal, redactable repro GeoPackage + metadata to debug interop issues across GDAL/QGIS/ArcGIS/etc.
risks:
  - The long tail of extensions (tiles, features, metadata, RTree/spatial indexes) can balloon scope.
  - SQLite behavior and spatial semantics differ across toolchains; need precise canonicalization rules.
---

## Problem
GeoPackage is a widely adopted OGC encoding standard for exchanging vector features and tile/raster content in a single SQLite file. Rust has some geospatial building blocks, but GeoPackage support is fragmented and often out-of-date.

Teams need:
- reliable read/write of core tables,
- extension discovery/management,
- and **diffable, reproducible** artifacts for interop debugging.

## What this crate provides
A workspace for GeoPackage as an operational artifact:

1. **Core GeoPackage IO** (features + tiles) with schema migrations.
2. **Extension registry**: discover/enable/validate extensions (e.g., RTree, metadata).
3. **Canonicalization**: produce a stable representation to enable diffs:
   - deterministic row ordering for export,
   - normalized geometry encoding,
   - stable metadata ordering.
4. **Interop bundles**: `*.gpkgbundle.zip` that contains a minimized gpkg + manifest + extracted canonical forms.
5. **Conformance probes**: run a suite that checks “this gpkg should open cleanly in common tools”.

### Bundle format: `*.gpkgbundle.zip`
- `manifest.json` (OGC version targeted, extensions, CRS info, generator)
- `input.gpkg` (optional minimized)
- `schema.sql` (canonical schema dump)
- `features.geojson` (canonical feature export per table)
- `tiles.index.json` (tile matrix + counts + hashes)
- `extensions.json` (detected/declared)
- `verdict.json` (probe results)

## Users
- Data platforms distributing offline map packages.
- Rust ETL pipelines that ingest/export gpkg.
- Teams debugging "works in QGIS but not in tool X" issues.

## Prior art (insufficient)
- `gpkg` exists but appears stale and doesn’t offer canonical diffs or interop bundles.
- `geozero` provides a useful zero-copy abstraction layer, but not GeoPackage conformance/extension workflows.

## Design goals
- **SQLite-first ergonomics**: work cleanly with `rusqlite`/`sqlx` backends via traits.
- **Geometry discipline**: explicit SRID/CRS handling; safe defaults.
- **Extension-aware**: treat extensions as structured modules with validation.
- **Diffability**: make it easy to review changes to a GeoPackage in PRs.

Non-goals:
- Replacing GDAL.
- Implementing every geospatial format.

## Architecture sketch
Workspace:
- `gpkg-core` — schema + IO for features/tiles + extension registry.
- `gpkg-geom` — geometry encode/decode helpers + canonical export.
- `gpkg-canon` — canonical schema dump + canonical feature export + hashing.
- `gpkg-probe` — conformance probes (integrity checks, extension validation).
- `gpkg-cli` — `inspect`, `export`, `canon`, `bundle`, `diff`, `probe`.

## MVP (4–8 weeks)
1. `inspect` + `export` for core feature tables (to canonical GeoJSON).
2. Canonical schema dump + stable hashing for “is this gpkg meaningfully changed?”.
3. `gpkgbundle.zip` emission for a minimal gpkg.

## De-risk plan
- Start with features-only (no tiles) and a small set of extensions.
- Use real corpora from open datasets and roundtrip through common tools.

## Maintenance
- Version the canonicalization profile.
- Keep extension modules independent and optional.
- Provide fixtures for common CRS + geometry edge cases.

## Sources
- OGC GeoPackage Encoding Standard.
- GeoPackage public site and HTML spec.
- Rust crates: `gpkg`, `geozero`.
