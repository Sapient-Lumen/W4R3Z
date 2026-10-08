# Design note: Geospatial Productization Stack (Geospatial Surface + Dataset Surface + Runtime Settings + Support Envelope, with Search / Protocol / Client / Interactive imports)

## Goal
Define the **division of labor and consumer flow** between Rust geospatial semantics, dataset/catalog publication, runtime activation, and shipped support truth so the ecosystem can make **geospatial products** reviewable without anointing one GIS engine, one data lake, one tile format, one catalog stack, or one map renderer as the winner.

This is **not** another GIS framework or map platform.
It is a stack note explaining how existing archive pieces should compose:
- [`design/geospatial-surface-kit.md`](./geospatial-surface-kit.md)
- [`design/dataset-surface-kit.md`](./dataset-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/client-app-surface-kit.md`](./client-app-surface-kit.md)
- [`design/interactive-productization-stack.md`](./interactive-productization-stack.md)
- [`design/search-productization-stack.md`](./search-productization-stack.md)
- [`design/protocol-productization-stack.md`](./protocol-productization-stack.md)
- [`design/service-surface-kit.md`](./service-surface-kit.md)

## Why this note is needed now
Rust geospatial signals no longer say only “you can do GIS in Rust.”
They say Rust now has **serious but non-equivalent product lanes**, and that the missing contribution is the product boundary above them:
- GeoRust is now unmistakably an ecosystem rather than a single flagship crate.
- GeoArrow and GeoParquet make cloud-native, columnar, and zero-copy geospatial publication a serious lane rather than an experiment.
- STAC is now a formal OGC standard and already has live Rust crates, which means discovery/catalog truth is not just external glue.
- PMTiles is now a real Rust-facing publication lane for low-ops tiled delivery.
- `maplibre-rs` makes web/mobile/desktop map rendering a live Rust runtime lane rather than a distant aspiration.
- GeoPolars shows the dataframe/analytics lane is real, while also being honest that product maturity remains uneven.

Together those signals justify treating geospatial shipping quality as a **frontier-worthy productization seam** instead of leaving Rust geospatial split across `geo-pack` declarations, dataset metadata, STAC JSON, PMTiles archives, renderer configs, native/runtime caveats, and support prose.

## Stack layers

### 1) Geospatial Surface: spatial semantics truth
Geospatial Surface owns the **declared spatial boundary**:
- geometry families and dimensions,
- CRS / axis-order / projection posture,
- format/interchange support,
- native GIS/runtime assumptions,
- and checked spatial evidence.

This layer answers questions like:
- “What geometry and CRS behavior is actually part of the product?”
- “Which formats are first-class rather than merely ingestible?”
- “Which runtime/native GIS assumptions are already part of the supported story?”

Design rule: **spatial semantics stay separate from dataset publication, runtime activation, and support claims**.

### 2) Dataset Surface: dataset, catalog, and publication truth
Dataset Surface owns the **published data side of the geospatial promise**:
- source datasets and derived artifacts,
- GeoParquet / Arrow / row-oriented / tiled / auxiliary data products,
- STAC collections/items/assets when relevant,
- publication cadence and freshness windows,
- partitioning/object-store layout/tiling assumptions,
- and import/export provenance.

This layer answers questions like:
- “What geospatial data is actually part of the product?”
- “Which catalog, asset, or archive forms are first-class?”
- “How stale can published data become before the support claim changes?”

Design rule: **dataset/catalog/publication truth must not be flattened into one renderer config or one spatial-surface declaration**.

### 3) Runtime Settings: activation and live-mode truth
Runtime Settings owns the **live activation boundary**:
- GDAL / PROJ / native-provider activation,
- object-store endpoints, region/profile/cache settings,
- tile/archive source selection,
- renderer/backend/device/profile activation,
- offline/cache/fallback modes,
- and environment/secret/config inputs that materially change product behavior.

This layer answers questions like:
- “Which settings changed what data could be read, transformed, served, or rendered?”
- “Was the product running in online, cached, or offline mode?”
- “Which renderer/backend/provider/runtime lane was actually active?”

Design rule: **activation truth must not live only in deploy scripts, env docs, or operator memory**.

### 4) Support Envelope + DocProof: shipped promise truth
Support Envelope and DocProof own the **what is actually promised** boundary:
- supported platforms/backends/providers,
- supported dataset/catalog/archive/rendering modes,
- supported freshness/update expectations,
- checked docs/examples/snippets,
- and release/support attachments that explain what geospatial story actually shipped.

This layer answers questions like:
- “Which geospatial capabilities are supported, best-effort, or experimental?”
- “What may release/support/docs consumers legitimately conclude?”
- “What is documented but not yet evidenced, and vice versa?”

Design rule: **a map demo, notebook, or screenshot is not the support contract**.

### 5) Downstream consumers and imports
The stack becomes ecosystem-worthy when real consumers can import it without flattening it:
- **Client App Surface / Interactive Productization** consumers can attach map UI, offline caches, gesture/input, and rendering/runtime truth without redefining spatial semantics.
- **Search Productization** consumers can attach spatial discovery/filter/ranking truth without becoming the hidden source of geometry/CRS authority.
- **Protocol / Service / Schema** consumers can attach STAC/API/tile/query/download interfaces without redefining published data truth.
- **Scientific / Data / Robotics** consumers can import selected geospatial artifacts for analysis, physical-world models, and domain workflows.
- **Release / support / atlas / agent** consumers can import selected evidence instead of reverse-engineering catalogs, renderer configs, and deployment notes.

Design rule: **consumers import selected evidence; they do not become the hidden source of truth for geospatial semantics or publication posture**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the one true Rust GIS platform.”
It is a portable, reviewable stack with explicit boundaries:

1. **spatial-semantics truth first**
   - prove geometry/CRS/format/runtime claims on one real subject;
2. **dataset/catalog/publication truth second**
   - make GeoParquet/STAC/archive/layout/freshness posture explicit;
3. **client/render/query attachments third**
   - attach map/render/search/service lanes without flattening them into core geospatial truth;
4. **runtime activation and evidence fourth**
   - make provider/backend/cache/object-store/native activation and degraded modes explicit;
5. **support/release/docs consumers fifth**
   - prove that release notes, support docs, service APIs, and interactive or scientific consumers can import the artifacts honestly.

An eventual aggregate artifact may exist, but it should be a **thin referenced pack** such as `geo-product-pack/v0`, not a new mega-framework.

## Non-goals
- not a universal GIS engine API;
- not a map renderer winner declaration;
- not a STAC server or tile-service control plane;
- not a dataframe or geodata lakehouse framework;
- not a fake one-number “geospatial readiness” badge;
- not a giant canonical schema that flattens semantics, catalogs, tiles, clients, and support into one object.

## Archive implications
- The archive should now treat **Geospatial Surface + Dataset Surface + Runtime Settings + Support Envelope** as a coupled **Geospatial Productization Stack** in frontier discussions.
- Future revisions should prefer **spatial semantics truth, dataset/catalog/publication truth, runtime activation truth, client/render/search attachments, and shipped/support truth** over another GIS kernel, wrapper, tile helper, or map demo.
- When Search, Protocol, Service, Client, Interactive, Scientific, Robotics, Release, Support, or Documentation work cites geospatial readiness, they should import **spatial truth**, **publication/freshness truth**, **activation truth**, and **support truth** separately.

## References (signals)
- GeoRust:
  https://georust.org/
- GeoArrow:
  https://geoarrow.org/
  https://docs.rs/geoarrow/
- GeoParquet:
  https://geoparquet.org/
  https://geoparquet.org/releases/v1.1.0/
- STAC:
  https://docs.ogc.org/cs/25-004/25-004.html
  https://docs.rs/stac/
  https://docs.rs/stac-client/
  https://stac-utils.github.io/rustac/
- PMTiles:
  https://docs.protomaps.com/pmtiles/
  https://crates.io/crates/pmtiles
- MapLibre Rust:
  https://docs.rs/maplibre/
  https://maplibre.org/maplibre-rs/docs/book/introduction.html
- GeoPolars:
  https://geopolars.org/
