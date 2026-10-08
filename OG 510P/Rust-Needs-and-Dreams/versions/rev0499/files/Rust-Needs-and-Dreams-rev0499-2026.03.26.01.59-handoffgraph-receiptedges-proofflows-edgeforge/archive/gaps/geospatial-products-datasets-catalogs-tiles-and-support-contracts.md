# Gap: geospatial products still lack one portable boundary above spatial semantics, cloud-native data/catalog truth, tile/publication truth, and shipped support claims

## Why this matters
Rust geospatial is no longer just a geometry-and-format story.
It now spans several **real but non-equivalent product lanes**:
- geometry/CRS/projection and native-driver-heavy GIS lanes,
- cloud-native tabular geospatial data (GeoArrow, GeoParquet, object-store-friendly publication),
- catalog/discovery lanes (STAC),
- tile/archive/publication lanes (PMTiles and adjacent map-delivery paths),
- and interactive client/rendering lanes (portable map renderers, desktop/mobile/web shells).

That maturity changes the missing contribution.
The missing thing is **not** another geometry crate, map engine, format wrapper, or “Rust GIS platform.”
The missing thing is the **product boundary above the ingredients**.

## Current ecosystem signals
- GeoRust explicitly presents itself as “an ecosystem of geospatial tools and libraries written in Rust.”
  https://georust.org/
- The existing Rust geospatial surface is already plural: `geo`, `geo-types`, `geozero`, `geoarrow`, `proj`, `gdal`, FlatGeobuf, and related crates each own materially different truths.
  https://docs.rs/geo/
  https://docs.rs/geo-types/
  https://docs.rs/crate/geozero/latest
  https://docs.rs/geoarrow/
  https://docs.rs/proj/
  https://docs.rs/crate/gdal/latest
  https://docs.rs/flatgeobuf/
- GeoArrow now has an explicit spec and Rust implementation, and the Rust crate has been refactored into smaller subcrates with narrower scope. That is a strong signal that Rust geospatial memory/interchange lanes are maturing rather than remaining one monolith.
  https://geoarrow.org/
  https://docs.rs/geoarrow/
- GeoParquet is now an incubating OGC standard with a current v1.1.0 specification. That means cloud-native geospatial publication is no longer just project-local convention.
  https://geoparquet.org/
  https://geoparquet.org/releases/v1.1.0/
- STAC is now an OGC Community Standard, and Rust has current `stac`, `stac-client`, and rustac lanes. That means catalog/discovery truth is already a real part of the Rust geospatial product story.
  https://docs.ogc.org/cs/25-004/25-004.html
  https://docs.rs/stac/
  https://docs.rs/stac-client/
  https://stac-utils.github.io/rustac/
- PMTiles has both an official product/distribution story and live Rust crates. That means single-file tile/archive publication is part of the ecosystem reality, not just a JS-side concern.
  https://docs.protomaps.com/pmtiles/
  https://crates.io/crates/pmtiles
- `maplibre-rs` now explicitly documents a portable WebGPU-based renderer for web/mobile/desktop, and GeoPolars explicitly treats zero-copy GeoArrow-based dataframe work as part of the story, while also being honest that it is still a prototype.
  https://docs.rs/maplibre/
  https://maplibre.org/maplibre-rs/docs/book/introduction.html
  https://geopolars.org/

## What is still missing
Today, support truth for a geospatial product is still scattered across:
- geometry and CRS assumptions in code/docs,
- dataset layout and publication posture in data-pipeline configs,
- STAC/catalog truths in separate JSON and service notes,
- tile/archive truth in build or deployment scripts,
- map renderer/backend/runtime assumptions in app docs,
- and final support claims in README prose and issue archaeology.

So a reviewer still cannot easily answer:
- what spatial semantics are actually public and supported,
- what dataset/catalog/tile publications are part of the product,
- what map/query/download behavior is first-class versus illustrative,
- what runtime/native/object-store/cache/backend settings materially changed behavior,
- what freshness windows or update contracts are part of the promise,
- and what release/support/docs consumers may safely conclude.

## Affected consumers
1. **library and tool authors** who need spatial semantics and format/runtime truth to be portable,
2. **data publishers and map-service teams** who need dataset/catalog/tile publication truth to be reviewable,
3. **client and interactive teams** who need renderer/runtime/backend assumptions attached to the same subject,
4. **support/release/docs consumers** who need one honest artifact instead of scraping configs, fixture folders, and screenshots,
5. **search, service, and scientific consumers** who need to import geospatial truths without silently becoming the new authority.

## What a worthy contribution should look like
The next worthy move is a thin **Geospatial Productization Stack** above the existing Geospatial Surface Kit.
It should:
- keep **spatial semantics** explicit (`geo-pack`-level truth),
- keep **dataset/catalog/publication truth** explicit,
- keep **runtime/native/backend/object-store activation** explicit,
- keep **map/render/download/query attachments** explicit when present,
- keep **support/docs/release truth** explicit,
- and let service/search/client/scientific consumers import those truths without flattening them.

In other words: Rust needs something closer to a **`cargo geo-product` / `geo-product-pack/v0`** layer than another GIS kernel, vector-tile renderer, STAC server, or dataframe wrapper.
