# Gap: geospatial data, CRS, and format contracts

## What is missing
Rust now has a real geospatial ecosystem, but it still lacks a **shared geospatial-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which geometry families and dimensionality are officially supported,
- which coordinate reference systems, axis-order assumptions, epochs, and projection/transformation lanes are part of the promise,
- which validity/topology/precision/rounding/snap rules are assumed,
- which file, binary, columnar, or stream encodings are actually first-class,
- which native-library, driver, or runtime assumptions are required,
- which operations are only illustrative versus actually checked,
- and what evidence exists that the declared spatial support still matches the shipped library or application.

That missing layer matters because Rust no longer just has one geometry crate. GeoRust is explicitly an ecosystem of geospatial tools and libraries written in Rust; `geo` already provides planar geometries and algorithms with DE-9IM/topological operations and PROJ-backed projection support; `geo-types` defines the common geometry types for the GeoRust ecosystem; `geozero` already provides zero-copy reading and writing of geospatial data across multiple formats; `geoarrow` is a native Rust implementation of GeoArrow for Arrow-based geospatial memory; `proj` provides coordinate transformation via PROJ bindings; `gdal` provides safe Rust bindings for GDAL’s raster/vector capabilities; and `flatgeobuf` gives Rust a performant binary geographic-data encoding. The remaining pain is increasingly the **portable support boundary above those pieces**, not the bare existence of geospatial crates.

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

## The current seam is awkward
The ecosystem clearly has ingredients:
- `geo` already gives Rust a strong geometry-and-algorithms core, but it is explicit that it provides **planar** geometries and then separately supports CRS conversion/projection via PROJ;
- `geo-types` already exists so crate authors can share geometric types across GeoRust without each inventing their own geometry inventory;
- `geozero` already defines a format-processing API without an intermediate representation, which is exactly the kind of substrate that needs honest support declarations above it;
- `geoarrow` and the GeoArrow specification already make columnar geospatial memory and CRS-carrying extension metadata real, which means support truth is no longer just “we can parse GeoJSON”; 
- `proj` already exposes coordinate transformations but is explicit about bundled-vs-system libproj behavior;
- `gdal` already exposes a huge vector/raster/native-driver universe, but its Rust crate is explicit that it assumes a compatible GDAL installation and that the authoritative docs remain GDAL’s own C/C++ APIs;
- `flatgeobuf` already shows that fast, binary geospatial interchange is part of the real Rust story rather than an afterthought.

But actual support truth still gets split across:
- README prose about supported formats,
- Cargo feature flags,
- axis-order and CRS assumptions hidden in examples,
- native library install steps,
- GDAL/PROJ version caveats,
- optional zero-copy/Arrow paths,
- topology-validity and precision expectations,
- and ad hoc smoke tests over a few fixtures.

The result is not that Rust lacks geospatial code.
The result is that there is still no portable way to say:
- “these geometry families and coordinate dimensions are officially supported,”
- “these CRS/projection assumptions are checked versus illustrative,”
- “these formats and memory layouts are first-class versus import/export-only,”
- “these native drivers or bundled libraries are part of the contract,”
- or “these transformation, validity, roundtrip, and topology cases were actually run.”

That is exactly the archive pattern worth elevating: strong point libraries, weak shared review layer.

Sources:
- https://docs.rs/geo/
- https://docs.rs/geo-types/
- https://docs.rs/crate/geozero/latest
- https://docs.rs/geoarrow/
- https://geoarrow.org/
- https://docs.rs/proj/
- https://docs.rs/crate/gdal/latest
- https://docs.rs/flatgeobuf/

## Why this matters
This gap is bigger than “better GIS docs.”
It affects:
1. **product honesty** — “supports spatial data” can hide very different realities around geometry types, CRS handling, reprojection, axis order, topology repair, or file-format coverage;
2. **compatibility review** — changing CRS assumptions, validity rules, supported encodings, or projection behavior can be a real breaking change;
3. **runtime clarity** — bundled versus system PROJ, GDAL versions, available drivers, and Arrow/zero-copy lanes are support claims, not invisible implementation details;
4. **testing realism** — many projects check one GeoJSON or WKT happy path but do not ship one artifact saying which formats, CRS transforms, topology cases, or roundtrips were actually exercised;
5. **cross-domain composition** — Dataset Surface Kit, Service Surface Kit, Event Surface Kit, Client App Surface Kit, Media Surface Kit, and Support Envelope Kit all need a spatial boundary without owning it;
6. **future maintenance** — a field with native deps, format churn, CRS complexity, and algorithmic subtleties badly needs support artifacts that survive maintainer turnover.

There is also an honesty constraint: a geospatial-surface kit should not pretend every Rust project is or should become a full GIS stack. Some applications only need geometry algorithms; some only need coordinate transforms; some only need fast file interchange; some rely on heavy native GDAL/PROJ bindings. A good contribution should therefore make supported scope and non-goals explicit instead of selling “geospatial support” as a magical universal capability.

Sources:
- https://docs.rs/geo/
- https://docs.rs/proj/
- https://docs.rs/crate/gdal/latest
- https://docs.rs/flatgeobuf/
- https://geoarrow.org/

## What “good” looks like
A worthy contribution here is **not** another GIS mega-framework, another geometry kernel, or another format wrapper.

It is a shared geospatial-surface boundary:
- one `geo-surface/v0` describing library/app identity, supported operation classes, and top-level vector/raster scope,
- one `geometry-catalog/v0` giving stable identities for supported geometry families, dimensionality, precision classes, and validity/topology posture,
- one `crs-profile/v0` describing CRS identifiers, axis-order assumptions, epoch/datum qualifiers when relevant, and projection/transformation support levels,
- one `geo-format-catalog/v0` describing file/binary/columnar/stream encodings, import/export-only lanes, and feature/runtime gates,
- one optional `geo-runtime-profile/v0` describing native GDAL/PROJ/GEOS/driver assumptions and bundled-vs-system behavior,
- one `geo-check-plan/v0` describing which fixtures, transforms, validity/topology checks, roundtrips, and benchmark scenarios were exercised,
- one `geo-check-report/v0` recording checked formats/CRS/operations/platforms, failures, drift findings, and raw attachment pointers,
- one optional `geo-diff-report/v0` for additive/breaking support changes,
- and one `geo-pack/v0` bundle for CI, release review, SDK/app handoff, and later archaeology.

That would let Rust teams treat geospatial support as a reviewable product surface instead of a pile of crate docs, native install notes, test fixtures, and intuition about whether a reprojection, format roundtrip, or topology operation is “supposed” to work.
