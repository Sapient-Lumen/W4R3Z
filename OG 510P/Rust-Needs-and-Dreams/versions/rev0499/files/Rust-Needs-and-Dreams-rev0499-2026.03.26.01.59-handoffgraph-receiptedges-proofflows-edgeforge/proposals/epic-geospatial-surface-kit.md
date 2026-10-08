# Epic proposal: Geospatial Surface Kit

## Thesis
Rust’s geospatial ecosystem is now strong enough that the missing contribution is no longer “yet another geometry helper” or “yet another format wrapper.”
The higher-leverage missing piece is a **portable geospatial-surface contract** that lets teams declare, diff, validate, and ship what their software actually promises: geometry families, CRS/projection posture, format support, runtime/native assumptions, and checked evidence.

In other words: Rust needs a boring, attachable `geo-pack/v0` more than it needs one more README that says “supports spatial data.”

## Why now
The ecosystem signals line up:
- GeoRust is now explicitly a real ecosystem rather than a lone crate.
- `geo` already covers a wide algorithmic surface but is explicit about planar semantics and CRS/projection support via PROJ.
- `geo-types` already provides shared geometry types for ecosystem compatibility.
- `geozero` already makes zero-copy format processing a real substrate.
- `geoarrow` plus the GeoArrow specification already make Arrow-native, CRS-aware geospatial memory a first-class lane.
- `proj` already handles coordinate transformations and exposes bundled-versus-system library realities.
- `gdal` already brings Rust into a vast vector/raster/driver ecosystem but with real native-runtime assumptions.
- FlatGeobuf already makes high-performance geospatial interchange part of the current story.

That means the missing substrate is not raw geospatial capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://georust.org/
- https://docs.rs/geo/
- https://docs.rs/geo-types/
- https://docs.rs/crate/geozero/latest
- https://docs.rs/geoarrow/
- https://geoarrow.org/
- https://docs.rs/proj/
- https://docs.rs/crate/gdal/latest
- https://docs.rs/flatgeobuf/

## What should be built
A first credible version should ship:
1. `geo-surface/v0`, `geometry-catalog/v0`, `crs-profile/v0`, `geo-format-catalog/v0`, optional `geo-runtime-profile/v0`, `geo-check-plan/v0`, `geo-check-report/v0`, optional `geo-diff-report/v0`, and `geo-pack/v0`
2. adapters for common Rust geospatial lanes (`geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, FlatGeobuf, and adjacent format crates)
3. generated support/reference docs for supported geometries, CRS assumptions, formats, runtime requirements, and checked scopes
4. validation/reporting support for unsupported CRS transforms, missing drivers, format-recognized-but-not-first-class cases, lossy roundtrips, invalid geometry handling, and regression drift across releases
5. release/CI examples showing geo packs attached to libraries, data-processing CLIs, services handling spatial payloads, Arrow/data pipelines, and desktop/mobile mapping apps

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one pure-Rust geometry-processing crate/app using `geo` and `geo-types` with explicit validity/topology assumptions and checked operation subsets
- one coordinate-transformation tool using `proj` with declared CRS assumptions and checked transform fixtures
- one GDAL-backed import/export app with explicit native dependency and driver/runtime claims
- one Arrow-native geospatial pipeline using `geoarrow` with explicit columnar/CRS propagation claims
- one file-ingestion or interchange tool using `geozero` and/or FlatGeobuf that proves inspect/import/export support can be declared separately from richer GIS behavior

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve geometry truth, CRS posture, format truth, and runtime truth separately
2. **v0.2 adapters**
   - support `geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, and FlatGeobuf attachments
   - support small fixture suites without flattening all spatial evidence into one fake canonical file format
3. **v0.3 cross-kit integration**
   - integrate with Dataset Surface, Service Surface, Event Surface, Client App Surface, Runtime Settings, and Support Envelope kits
   - support diff/baseline workflows across platforms/releases
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one runtime, one format lane, or one dependency posture

## Success metrics
- Teams can review spatial-support changes as explicit artifacts instead of reverse-engineering examples, feature flags, and install docs.
- Supported geometries, CRS assumptions, and format/runtime qualifiers remain documented from one declared source.
- Native/runtime requirements become easier to trust because checked and illustrative lanes stay distinct.
- Transformation and roundtrip behavior becomes less folkloric and more reviewable.
- Rust geospatial stacks become easier to hand off across data, services, client apps, docs, and operations workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Dataset Surface Kit covers table/layout/engine truth,
- Service Surface Kit and Event Surface Kit cover API/message boundaries,
- Client App Surface Kit covers app/package/lifecycle/capability truth,
- Support Envelope Kit covers platform/runtime baselines,
- Runtime Settings Kit covers runtime knobs,
- and Media Surface Kit covers media/content behavior.

But none of those is the portable contract for the **geospatial boundary itself**.
Geospatial Surface Kit is the missing substrate that keeps geometry families, CRS/projection posture, format/runtime assumptions, and checked evidence attached to one reviewable interface without absorbing the rest of the stack into one mega-GIS abstraction.
