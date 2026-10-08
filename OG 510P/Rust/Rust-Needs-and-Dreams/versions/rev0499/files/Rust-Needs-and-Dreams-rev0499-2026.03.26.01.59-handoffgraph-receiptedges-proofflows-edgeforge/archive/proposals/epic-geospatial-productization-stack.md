# Epic proposal: Geospatial Productization Stack (`cargo geo-product`, `geo-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **geospatial products** that links **declared spatial semantics**, **dataset/catalog/archive publication**, **runtime activation**, **client/render/query attachments**, and **support/docs truth** into one portable review boundary without pretending GeoRust, GeoArrow, GeoParquet, STAC, PMTiles, map renderers, and data/analytics tools have already converged into one framework or one source of truth.

## Why this is now worth doing
Rust geospatial is no longer “a few geometry crates if you want them.”
It now has multiple real product lanes:
- spatial geometry/CRS/projection libraries,
- cloud-native tabular publication and zero-copy memory lanes,
- catalog/discovery lanes,
- tile/archive publication lanes,
- interactive map/rendering lanes,
- and analytics/dataframe integration lanes.

That maturity changes the missing contribution.
The missing thing is **not** another format wrapper, GIS engine, STAC server, tile helper, or renderer.
It is the attachable product boundary above them.

## The ecosystem evidence
The current ecosystem already shows the exact fragmentation pattern that calls for a shared product layer:
- GeoRust is explicitly an ecosystem, not a single crate.
- GeoArrow provides a real zero-copy and cross-language memory/interchange lane.
- GeoParquet has become an incubating OGC standard with a current stable specification.
- STAC is now an OGC Community Standard and already has current Rust implementations and clients.
- PMTiles is an explicit low-ops archive/publication format with live Rust crates.
- `maplibre-rs` makes portable WebGPU map rendering a real Rust lane.
- GeoPolars shows geospatial dataframe work is emerging on top of GeoArrow while still being honest that maturity is uneven.

That is exactly when Rust should add a **thin pack/report/import layer** instead of another winner-take-all pitch.

## What this epic should provide
A thin, portable geospatial-product contract layer with:
- subject identity for the exact app/service/dataset/release/deployment being reviewed,
- imported geospatial-surface artifacts,
- imported dataset/catalog/archive publication and freshness artifacts,
- imported runtime/native/object-store/cache/backend attachments,
- optional imported search/service/client/rendering attachments,
- bounded support/docs/release handoffs,
- explicit diff and lossiness reporting between revisions or consumers,
- and no pretense that one engine, one catalog format, one archive format, or one renderer owns the whole product.

## This epic should not own
- a universal GIS API,
- a universal catalog server,
- a universal map-rendering runtime,
- a hosted geospatial control plane,
- a giant canonical geodata schema,
- or a fake one-number “geospatial readiness” badge.

## Candidate artifact family

### `geo-product-brief/v0`
Why the product exists, intended consumer set, geospatial roles in scope, freshness/update expectations, and review status.

### `geo-product-subject/v0`
The exact service/app/dataset/release/deployment subject, imported `geo-pack` and dataset/publication attachments, comparison base, and environment/support scope.

### `geo-product-pack/v0`
The portable review bundle linking:
- imported `geo-pack` attachments,
- imported dataset/catalog/archive publication attachments,
- imported runtime-settings attachments,
- optional imported search/service/client/interactive attachments,
- imported support/docs/release handoffs,
- local notes, waivers, caveats, and integrity metadata.

### `geo-product-diff/v0`
What changed between two review points, with separate sections for:
- geometry/CRS/format/runtime surface,
- dataset/catalog/archive publication,
- freshness/update posture,
- client/render/query/service attachments,
- runtime/native/object-store/backend activation,
- docs/support/release conclusions.

### `geo-product-handoff/v0`
Bounded consumer summaries for:
- dataset/catalog publishers,
- service/search/API consumers,
- client/interactive/map consumers,
- support/release review,
- scientific/robotics/atlas consumers,
- assistant/editor rendering.

## Recommended rollout
1. spatial-semantics lane
2. dataset/catalog/publication lane
3. client/render/query attachment lane
4. runtime/native/object-store activation lane
5. support/release/consumer handoff lane

This should be driven by [`design/geospatial-productization-pilot-program.md`](../design/geospatial-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer CRS wrapper,
- a nicer GeoParquet writer,
- a nicer STAC helper,
- a nicer PMTiles builder,
- a nicer renderer integration,
- or a nicer geospatial dashboard.

An epic contribution here instead gives Rust one **portable geospatial-product contract** above those lanes.
That is strategically different because it can:
- make dataset/catalog, map/render, service/search, and support/release reviews share the same geospatial subject boundary;
- let cloud-native data, catalog/discovery, tiled distribution, and interactive map workflows stay specialized without pretending any one defines the whole product;
- keep spatial semantics, publication/freshness, runtime activation, imported consumers, and support claims distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping specs, configs, archives, screenshots, and README prose.

## Design principles
- **Spatial semantics are not publication truth.**
- **Publication truth is not runtime activation truth.**
- **Client/render/search/service attachments are imports, not the whole product.**
- **Support/docs truth is not implied by one working map demo.**
- **Consumer summaries are intentionally lossy and say so.**
- **The stack stays thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact geospatial product subject,”
- “these are the geometry/CRS/format/runtime semantics we actually support,”
- “these are the datasets/catalogs/archives we actually publish and how fresh they are expected to be,”
- “these are the map/query/service consumers we imported when relevant,”
- “these are the runtime/native/object-store/backend settings that materially changed behavior,”
- “this is what changed from the prior review,”
- and “this is what support/release/docs/scientific/robotics consumers may safely conclude,”

without inventing a bespoke geospatial-readiness schema for every repository.

## Read this with
- `gaps/geospatial-products-datasets-catalogs-tiles-and-support-contracts.md`
- `design/geospatial-productization-stack.md`
- `design/geospatial-productization-pilot-program.md`
- `design/geospatial-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
