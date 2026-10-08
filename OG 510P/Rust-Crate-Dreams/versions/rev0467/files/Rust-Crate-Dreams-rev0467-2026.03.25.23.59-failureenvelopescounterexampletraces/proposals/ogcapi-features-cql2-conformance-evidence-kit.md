---
id: P-0314
title: OGC API Features + CQL2 Conformance & Evidence Kit — geospatial query lockfiles, semantic result diffs, and profile-aware shareable bug bundles
status: idea
domains: [geospatial, ogc, api, standards, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.ogc.org/standards/ogcapi-features/
  - https://github.com/opengeospatial/ogcapi-features
  - https://crates.io/crates/ogcapi
  - https://crates.io/crates/ogcapi-types
---

# Problem

The geospatial ecosystem is steadily moving toward OGC API building blocks and modern filter/query behavior, but implementation pain is still high:

- Features results differ because of CRS handling, bbox interpretation, query semantics, paging, and filter translation,
- CQL2 support is subtle enough that “supports filtering” often hides meaningful divergence,
- debugging still relies on raw HTTP logs and hand-compared GeoJSON,
- Rust has real OGC API building blocks now, but not yet a strong **conformance/evidence workbench**.

The missing epic crate is therefore not merely a server framework. It is a **profile-aware conformance, query-lockfile, and evidence kit** for geospatial APIs.

# What it provides

- `ogcapi-lock` — pin supported parts, query parameters, CRS assumptions, filter features, and pagination expectations.
- `ogcapi-cql2` — normalized filter IR with parser/serializer adapters for text and JSON encodings.
- `ogcapi-verify` — checks landing page, collections, items, query semantics, CRS behavior, content negotiation, and error contracts.
- `ogcapi-diff` — semantic result diffs for geometry/attribute/query-behavior changes.
- `ogcapi-replay` — deterministic replay of request/response bundles against servers or fixtures.
- `cargo ogcapi` — emit `*.ogcbundle.zip` for vendor support, regression CI, and procurement evaluation.

# What the crate should provide other people

1. **A machine-readable geospatial capability contract** instead of vague “OGC API compatible” claims.
2. **Semantic diffing** that understands geospatial results better than plain JSON text comparison.
3. **Portable bug bundles** that data providers, clients, and vendors can replay.
4. **A CQL2 normalization layer** that keeps filter portability from devolving into ad hoc SQL-ish dialects.
5. **A high-leverage test surface** for the growing GeoRust OGC API stack.

# Users & user stories

- **Geospatial platform teams**: “Show whether our new server still honors the same filter and CRS semantics.”
- **Client authors**: “Replay a failing feature query from production without access to the original database.”
- **Data providers**: “Publish a small conformance bundle that proves our API contract to integrators.”
- **Procurement / QA teams**: “Compare two OGC API vendors on the exact subset we care about.”

# Prior art (and why it’s insufficient)

- OGC has already done the hard work of defining modular API standards and publishing testable behavior.
- GeoRust now has emerging OGC API crates, including `ogcapi` and `ogcapi-types`.
- The missing piece is the boring but powerful layer: **profile lockfiles, reproducible queries, semantic result diffs, and compact evidence bundles**.

# Design goals

1. **Standards-modular** — embrace the OGC API building-block model.
2. **Query-first** — CQL2 and filtering behavior are first-class, not afterthoughts.
3. **Geospatial semantics-aware** — geometry/CRS/result meaning beats raw JSON textual equality.
4. **Client/server neutral** — valuable to both implementers and consumers.
5. **Good CI ergonomics** — easy enough to run in routine regression workflows.

# Non-goals

- Not a desktop GIS.
- Not a full geospatial database.
- Not a replacement for OGC’s broader standards ecosystem.

# Architecture & API sketch

```rust
pub struct OgcApiReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub query_findings: Vec<QueryFinding>,
    pub result_divergences: Vec<ResultDivergence>,
}

pub fn verify_server(profile: &Profile, transcript: &HttpTranscript) -> OgcApiReport;
```

Bundle draft: `profile.toml`, `requests.jsonl`, `responses/`, `normalized-results.json`, `verdicts.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support geometry simplification or hashing for sensitive layers.
- Preserve CRS and query provenance even when payloads are redacted.
- Bound capture size for large collections.
- Separate public evidence bundles from provider-internal dataset snapshots.

# Maintenance & governance plan

- Pin exact OGC API parts and CQL2 versions used in fixture packs.
- Publish minimal public fixture datasets that exercise bbox, CRS, filtering, pagination, and feature-id access.
- Keep normalization logic separately versioned from HTTP capture logic.
- Encourage provider/client interop contributions around well-labeled conformance subsets.

# Milestones

## 0.1
- Profile lockfiles
- Basic landing-page/collections/items verification
- CQL2 normalization + request replay

## 0.2
- Semantic geometry/result diffs
- CRS and pagination diagnostics
- Public fixture packs

## 1.0
- Stable `*.ogcbundle.zip`
- CI/procurement comparison workflows
- Adapter support around broader GeoRust server/client stacks

# Open questions

- Which geometry canonicalization strategy is the least surprising across backends?
- How should floating-point tolerance be encoded in profiles?
- Should CQL2 live as an independent reusable crate with this workbench wrapping it?

# Sources

- OGC API Features standard overview: https://www.ogc.org/standards/ogcapi-features/
- OGC API Features repository: https://github.com/opengeospatial/ogcapi-features
- `ogcapi`: https://crates.io/crates/ogcapi
- `ogcapi-types`: https://crates.io/crates/ogcapi-types
