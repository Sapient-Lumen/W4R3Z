# Design: Geospatial Surface Kit (`cargo geocheck`, `geo-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust library or application’s supported **geospatial surface**: geometry families, CRS/projection posture, format and memory-layout support, precision/topology assumptions, runtime/native-driver dependencies, and evidence that the declared spatial behavior still matches reality.

This should **not** replace `geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, FlatGeobuf, or future GIS/data engines.
It should make them compose better and make support claims reviewable.

## References (signals)
- GeoRust is explicitly “an ecosystem of geospatial tools and libraries written in Rust.”
  https://georust.org/
- `geo` explicitly provides planar geospatial geometries and algorithms, including DE-9IM/topological operations, multiple distance models, projection support via PROJ, and IO through `geojson`/`geozero`.
  https://docs.rs/geo/
- `geo-types` explicitly defines the geometric types for the GeoRust ecosystem.
  https://docs.rs/geo-types/
- `geozero` explicitly provides zero-copy reading and writing of geospatial data and defines an API for processing formats without an intermediate representation.
  https://docs.rs/crate/geozero/latest
- `geoarrow` is explicitly a complete, safe, native Rust implementation of GeoArrow, and the GeoArrow specification explicitly uses Arrow extension metadata so CRS and related type-level metadata can propagate.
  https://docs.rs/geoarrow/
  https://geoarrow.org/
- `proj` explicitly provides coordinate transformation via bindings to the PROJ v9.6 API and is explicit about system-lib versus bundled builds.
  https://docs.rs/proj/
- `gdal` explicitly provides safe, idiomatic Rust bindings for GDAL’s raster/vector capabilities, while also being explicit that builds assume a compatible GDAL installation and that authoritative documentation remains upstream GDAL docs.
  https://docs.rs/crate/gdal/latest
- `flatgeobuf` explicitly provides a performant binary encoding for geographic data based on FlatBuffers.
  https://docs.rs/flatgeobuf/

## Problem statement
Rust geospatial support is now spread across several real lanes:
- common in-memory geometry types,
- algorithm crates,
- CRS/projection transforms,
- file/binary/columnar formats,
- native-driver-heavy GIS bindings,
- and zero-copy/tabular integration.

But the ecosystem still lacks one portable artifact saying:
- which geometry families and coordinate dimensions are part of the contract,
- which CRS/projection assumptions are claimed,
- which formats and memory layouts are first-class,
- which runtime/native dependencies matter,
- and which operations have actual checked evidence.

So support truth currently lives in examples, features, fixture folders, install docs, and maintainer memory.

## Proposed artifact family

### 1) `geo-surface/v0`
Top-level declaration of a crate/app’s supported geospatial surface.

Should capture:
- crate/app identity and version
- vector/raster/tiling/streaming scope at a coarse level
- supported operation classes (read, write, transform, validate, simplify, clip, overlay, index, tile, analyze, render-adjacent, etc.)
- declared support levels (first-class / import-export / experimental / illustrative only)
- attachment refs to the rest of the pack

Design rule: keep the top-level object concise and make subordinate truth explicit elsewhere.

### 2) `geometry-catalog/v0`
Stable identities for supported geometry families and related semantics.

Should capture:
- geometry families (Point, LineString, Polygon, Multi*, collections, rects, triangles, raster-like grids when in scope)
- coordinate dimensionality (2D / 3D / measured / mixed)
- numeric/precision posture when relevant
- empty/null/invalid geometry handling
- topology and validity assumptions
- support level and caveats for each family

Design rule: keep raw geometry truth explicit instead of burying it in format docs.

### 3) `crs-profile/v0`
Declared coordinate-reference and transformation posture.

Should capture:
- supported CRS identifiers and aliases
- axis-order assumptions
- projection / inverse-projection / conversion lanes
- datum/epoch qualifiers when relevant
- planar-versus-geodesic assumptions
- unsupported or lossy transform classes
- feature/runtime gates for transformation support

Design rule: do not let CRS truth hide in code examples or prose.

### 4) `geo-format-catalog/v0`
Declared file, binary, columnar, and interchange-format support.

Should capture:
- WKT/WKB/GeoJSON/MVT/FlatGeobuf/GeoArrow and other relevant formats
- import/export/read/write/roundtrip support levels
- metadata/CRS propagation posture per format
- zero-copy or Arrow-native lanes when relevant
- runtime/native dependency gates per format
- known-lossy or unsupported conversions

Design rule: distinguish “can ingest somehow” from “first-class supported format.”

### 5) `geo-runtime-profile/v0` (optional)
Native and runtime assumptions that materially affect support.

Should capture:
- GDAL / PROJ / GEOS / driver assumptions when relevant
- bundled-versus-system library policy
- supported version windows or minimums when relevant
- platform-specific caveats
- runtime plugin/driver inventories when relevant

Design rule: keep runtime truth explicit instead of burying it in install docs.

### 6) `geo-check-plan/v0`
Plan for validating that the declared geospatial surface still behaves as claimed.

Should capture:
- selected geometry/CRS/format ids to exercise
- representative fixture datasets and generated cases
- transformation and roundtrip scenarios
- topology/validity/precision scenarios
- platform/runtime combinations to exercise
- unsupported or illustrative-only scenarios

Design rule: distinguish demo data from actual checked coverage.

### 7) `geo-check-report/v0`
Portable results from geospatial checks.

Should capture:
- artifact versions and environment
- runtime/native-driver state
- formats/CRS/operations exercised
- pass/fail/unsupported outcomes
- roundtrip, validity, topology, or precision findings
- raw attachment refs (fixtures, hashes, logs, generated outputs, benchmark snippets)

Design rule: the report should be honest about scope. “One GeoJSON file parsed” is not proof of broad geospatial support.

### 8) `geo-diff-report/v0` (optional)
A compatibility-oriented comparison between two declared geospatial surfaces.

Should support:
- added/removed geometry families or operations
- changed CRS assumptions
- changed format support levels
- changed runtime/native gates
- possible compatibility hazards

### 9) `geo-pack/v0`
Bundle format for declarations, reports, fixture inventories, generated docs, and supporting artifacts.

## How it should compose
- **Dataset Surface Kit:** link spatial tables, Arrow/Parquet/GeoArrow surfaces, and bounded sample datasets without pretending a dataset contract is the same thing as a geospatial support contract.
- **Service Surface Kit / Event Surface Kit:** link spatial request/response or message payloads without confusing those API boundaries with the spatial semantics themselves.
- **Client App Surface Kit:** link map/offline/location/export features without making the app kit own CRS/geometry/format truth.
- **Support Envelope Kit:** link platform/runtime baselines without replacing the geospatial-specific runtime and driver declarations.
- **Runtime Settings Kit:** link projection options, driver toggles, data-path settings, and GDAL/PROJ env assumptions as runtime inputs.
- **Media Surface Kit:** keep raster/tile/media pipelines distinct where appropriate instead of flattening image/video support into generic “geo support.”

## Non-goals
- standardizing one universal GIS kernel
- replacing `geo`, GDAL, or PROJ
- forcing vector, raster, tiling, and map-rendering stacks into one fake canonical model
- claiming a format parser implies honest CRS propagation or topology support
- pretending native-driver-heavy and pure-Rust lanes have the same support posture
- pretending a couple of demo fixtures validate real-world spatial compatibility

## First implementation shape
A credible first implementation could be mostly adapters and validators:
- generate `geo-surface` + `geometry-catalog` + `crs-profile` from lightweight project config and crate/runtime annotations
- ingest `geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, and FlatGeobuf attachments without flattening away source truth
- record small fixture suites with hashes and expected transform/roundtrip/validity outcomes
- emit generated support/reference docs for geometry families, CRS assumptions, and format/runtime requirements
- attach raw logs and output artifacts as evidence
- provide a diff mode for spatial-support changes across releases

The winning version is intentionally boring: it turns “supports geospatial data” from folklore into reviewed artifacts.
