# Design: Geospatial Productization Pilot Program (Spatial Semantics → Dataset/Catalog Publication → Client/Render/Query Attachments → Runtime Activation → Support/Release Consumers)

## Goal
Turn the **Geospatial Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust geospatial products are built, published, reviewed, and supported?

The pilot program should not chase a universal GIS platform.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Geospatial work is unusually prone to false convergence.
A team may use the same repository to:
- publish GeoParquet,
- expose STAC metadata,
- serve or ship PMTiles,
- render maps in a client,
- and perform CRS transformations or analytics.

Those activities share a subject, but they do **not** share one source of truth.
A credible plan therefore needs to decide:
- when spatial semantics alone are already worth exporting,
- when dataset/catalog/publication truth must be attached,
- when client/render/search/service lanes should be imported,
- when runtime/native/object-store/backend activation becomes part of the contract,
- and which support/release consumers justify graduation.

## Principles
1. **Start from spatial semantics, not product gloss**
   - a pack that proves geometry/CRS/format/runtime posture is worth more than a map demo or benchmark.
2. **Keep dataset/catalog/publication truth separate from rendering truth**
   - GeoParquet/STAC/PMTiles publication does not imply a supported map application.
3. **Keep runtime activation separate from authored declarations**
   - GDAL/PROJ/backends/object stores/caches/renderers should be attached as activation evidence, not silently merged into the authored surface.
4. **Search/service/client lanes are imports, not the core authority**
   - APIs, search endpoints, and map clients should import geospatial truth rather than redefine it.
5. **Support/release claims come last**
   - shipping and documentation posture should graduate only after the lower layers exist.

## Common artifacts this program should drive
- `geo-product-brief/v0` — declare which pilot lane is being exercised, scope, product roles, and non-goals.
- `geo-product-subject/v0` — exact app/service/dataset/release/deployment subject, imported `geo-pack` and dataset attachments, comparison base, and support scope.
- `geo-publication-brief/v0` — bounded summary of dataset/catalog/archive publication forms (GeoParquet, STAC, PMTiles, other) and their freshness/update posture.
- `geo-runtime-activation/v0` — GDAL/PROJ/object-store/cache/backend/device/runtime settings that materially changed behavior.
- `geo-consumer-handoff/v0` — what service/client/search/support/release consumers may conclude and what remains out of scope.
- `geo-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Spatial-semantics lane
**Why first:** it proves the narrowest, most reusable geospatial claim with the least product sprawl.

**Concrete scope**
- one real geospatial subject,
- exported `geo-pack` artifacts,
- geometry/CRS/format/runtime posture,
- checked fixtures for transforms/roundtrips/validity,
- docs/support notes stating semantics honestly.

**Graduation bar**
- a reviewer can tell what spatial behavior exists without reading raw code, format specs, or scattered docs.

### 2) Dataset / catalog / publication lane
**Why second:** once spatial semantics are explicit, the next hidden source of product confusion is what data is actually published and how.

**Concrete scope**
- GeoParquet / Arrow / row-oriented / tile/archive outputs,
- STAC collections/items/assets when present,
- source dataset identity and freshness/update cadence,
- partitioning/layout/object-store assumptions,
- lossy vs first-class publication modes.

**Graduation bar**
- the pack can explain what geospatial data is actually published, how fresh it is expected to be, and which catalog/archive forms are first-class.

### 3) Client / render / query attachment lane
**Why third:** this is where teams often start overclaiming from one successful demo.

**Concrete scope**
- `maplibre-rs` or similar renderer attachment when present,
- optional search/service attachment for dataset discovery or tile/query delivery,
- client/runtime role declaration,
- offline/cache posture,
- explicit note when a lane is prototype, experimental, or illustrative.

**Graduation bar**
- a reviewer can tell which map/query/client behaviors are imported consumers of geospatial truth and which are actually supported product lanes.

### 4) Runtime / native / object-store activation lane
**Why fourth:** this is where geospatial products often become hand-wavy unless activation is explicit.

**Concrete scope**
- GDAL / PROJ / native provider assumptions,
- object-store endpoints/regions/credentials or local-cache posture,
- renderer/backend/device selection,
- tile/archive source selection,
- degraded or offline fallback behavior.

**Graduation bar**
- a reviewer can tell what environment/settings materially changed the product and what worked only under one provider/backend/runtime posture.

### 5) Support / release / consumer-handoff lane
**Why fifth:** this is where the stack proves it matters beyond demos and notebooks.

**Concrete scope**
- supported platforms/providers/backends,
- checked docs/examples,
- release attachments importing lower-layer geospatial truth,
- support playbook handoff,
- atlas/comparison notes for serious Rust geospatial lanes.

**Graduation bar**
- a release or support consumer can answer what geospatial story is actually supported and what evidence accompanied it.

## What to defer
- a universal GIS kernel;
- a universal map renderer;
- a universal STAC/OGC/tiles control plane;
- one giant “cloud-native geospatial platform” crate;
- benchmark theater without publication or support truth;
- marketing claims that flatten datasets, tiles, maps, catalogs, and runtime posture into one story.

## Immediate archive consequences
- Treat **Geospatial Surface Kit** as the anchor of a broader **Geospatial Productization Stack** rather than an isolated spatial-semantics idea.
- Treat **Dataset Surface** as the publication/freshness/catalog half of the story instead of letting renderer or API docs silently absorb it.
- Treat **Client/Interactive/Search/Protocol** as importing attachment lanes rather than hidden geospatial authorities.
- Add a specific amnesia resistor so later revisions cannot collapse spatial semantics, dataset/catalog/archive publication, runtime activation, client/render/search imports, and support/release conclusions into one note.

## Read this together with
- `design/geospatial-productization-stack.md`
- `design/geospatial-surface-kit.md`
- `design/dataset-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
- `design/client-app-surface-kit.md`
- `design/interactive-productization-stack.md`
- `design/search-productization-stack.md`
- `design/protocol-productization-stack.md`

## Proposal-layer companion
The explicit proposal-layer candidate is now [`proposals/epic-geospatial-productization-stack.md`](../proposals/epic-geospatial-productization-stack.md): a thin `cargo geo-product` / `geo-product-pack/v0` layer above Geospatial Surface + Dataset Surface + Runtime Settings + Support Envelope, with Client/Interactive/Search/Protocol/Service lanes importing it rather than silently owning geospatial product truth. The pilot stays intentionally narrower than a universal GIS claim: prove spatial semantics first, then dataset/catalog publication, then client/render/query attachments, then runtime activation, then support/release consumers.
