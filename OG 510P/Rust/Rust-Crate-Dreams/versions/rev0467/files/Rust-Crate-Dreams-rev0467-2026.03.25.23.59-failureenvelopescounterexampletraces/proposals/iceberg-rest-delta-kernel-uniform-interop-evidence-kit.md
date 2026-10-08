---
id: P-0359
title: Apache Iceberg REST Catalog + Delta Kernel / UniForm Interop & Evidence Kit — catalog locks, metadata drift diffs, and replayable lakehouse bundles
status: idea
domains: [data-engineering, lakehouse, catalogs, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://iceberg.apache.org/rest-catalog-spec/
  - https://iceberg.apache.org/
  - https://docs.delta.io/delta-kernel/
  - https://docs.delta.io/delta-uniform/
  - https://crates.io/crates/iceberg
  - https://crates.io/crates/iceberg-catalog-rest
  - https://crates.io/crates/deltalake
---

# Problem

Rust now has serious substrate for open lakehouse formats, but the most painful integration failures still happen at the seam between:

- catalog APIs and table metadata evolution,
- Iceberg REST semantics and actual backend behavior,
- Delta transaction-log features and connector expectations,
- UniForm/Iceberg cross-format visibility,
- and engine upgrades that quietly change metadata, snapshots, or feature compatibility.

The missing Rust contribution is not a new warehouse or query engine. It is a **catalog-and-table interoperability workbench** that makes open-lakehouse failures portable and explainable.

# What it provides

- `lakehouse-ir` — stable IR for namespaces, tables, snapshots, schema/partition specs, feature flags, and catalog capabilities.
- `catalog-lock` — lockfiles pinning REST catalog endpoints, auth assumptions, supported features, metadata hashes, and cross-format visibility expectations.
- `catalog-replay` — portable create/load/scan/commit/rename cases for catalog and table operations.
- `lakehouse-check` — compare live Iceberg REST and Delta/UniForm behavior against a pinned lock or fixture pack.
- `lakehouse-diff` — semantic diffs such as “same table, different snapshot visibility”, “catalog commit semantics drift”, or “UniForm metadata lag”.
- `cargo lakehouse-evidence` — emit `*.lakehousebundle.zip` for connector CI, catalog debugging, or engine-vendor bug reports.

# What the crate should provide other people

1. **A boring artifact for lakehouse metadata and catalog bugs**.
2. **Pinned catalog/table expectations** that survive connector or engine upgrades.
3. **Cross-format visibility checks** for Delta/UniForm versus Iceberg readers.
4. **Replayable catalog scenarios** that are smaller than standing up whole engine stacks.
5. **Semantic diffs across metadata revisions and feature-compatibility changes**.

# Persona / who it’s for

- Data-platform teams
- Rust connector and catalog authors
- Lakehouse interoperability engineers
- Engine/plugin developers
- Teams standardizing on open table formats but mixing multiple runtimes

# Users & user stories

- **Connector author**: “Tell me whether the breakage is in the REST catalog, metadata interpretation, or Delta feature compatibility.”
- **Platform maintainer**: “Pin exactly what this catalog and table are expected to expose so upgrades cannot drift silently.”
- **Migration engineer**: “Check whether Iceberg readers see the same table surface after UniForm metadata generation.”
- **QA maintainer**: “Replay a failing table operation against multiple backends with one neutral artifact.”

# Prior art (and why it’s insufficient)

- Apache Iceberg publishes a REST Catalog specification and official Rust crates now exist.
- Delta publishes Delta Kernel and UniForm documentation, and Rust has `deltalake`.
- But Rust still lacks a boring-default crate for **catalog locks + scenario replay + metadata/feature diffs + portable evidence bundles**.

# Design goals

1. **Metadata-first** — center on table/catalog semantics, not query-engine execution.
2. **Cross-format aware** — handle Iceberg-native and Delta/UniForm surfaces without pretending they are identical.
3. **Backend-neutral** — adapters for catalog services and object stores, not one preferred vendor stack.
4. **Replayable** — model small, deterministic scenarios rather than giant data pipelines.
5. **Compatibility-explicit** — record exact feature and version assumptions.

# MVP surface

- Minimal types: `CatalogLock`, `TableSurface`, `ReplayScenario`, `LakehouseReport`, `LakehouseDiffFinding`
- Minimal functions:
  - `snapshot_catalog()`
  - `snapshot_table()`
  - `run_scenario()`
  - `diff_surfaces()`
  - `write_bundle()`
- Feature flags:
  - `iceberg-rest`
  - `delta-kernel`
  - `uniform`
  - `object-store`
  - `redaction`

# Compatibility story

- MVP should target Iceberg REST catalog semantics and read-focused Delta/UniForm comparisons first.
- The crate should complement existing Rust table-format crates rather than replace them.
- Engine-specific execution can stay out of scope initially; focus on catalog and metadata surfaces.
- Auth and cloud-backend details should be kept behind adapters.

# Conformance & fixtures

- Tiny fixture tables with deliberate schema, partition-spec, and snapshot changes.
- Scenarios for namespace/table creation, listing, loading, rename/drop, and failed commits.
- Visibility checks for Iceberg readers against UniForm-generated metadata.
- Goldens for “metadata changed but table surface should match”, “feature compatibility changed”, and “catalog returns semantically different error”.

# Path to boring stability

- Freeze the catalog/table IR and bundle layout before growing backend adapters.
- Keep early scenarios intentionally small and deterministic.
- Prefer metadata and lockfile explainability over broad engine integration.
- Add more feature-pack coverage only after the first diff reports are genuinely useful.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that snapshot an Iceberg REST catalog and one or more tables, replay a small set of catalog/table operations, compare the results against a lockfile, and emit a compact `*.lakehousebundle.zip`.

# De-risk plan

1. Start with metadata and catalog semantics, not query execution.
2. Keep Delta support read/visibility oriented before modeling every write path.
3. Make UniForm checks explicitly asynchronous/lag-aware rather than assuming synchronous equivalence.
4. Use tiny local or in-memory fixture backends in the first corpus.

# Non-goals

- Not a new catalog server.
- Not a distributed query engine.
- Not a data-ingestion framework.
- Not a replacement for Iceberg or Delta Rust crates.

# Architecture & API sketch

```rust
pub struct LakehouseReport {
    pub lock_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<LakehouseDiffFinding>,
}

pub fn snapshot_catalog(endpoint: &CatalogEndpoint) -> Result<CatalogSnapshot>;
pub fn run_scenario(lock: &CatalogLock, scenario: &ReplayScenario) -> Result<LakehouseReport>;
```

Bundle draft: `profile.toml`, `catalog.json`, `table-surfaces.json`, `scenarios.jsonl`, `report.json`, `diff.json`, `auth-redaction.json`, `notes.md`.

# Security / safety model

- Treat metadata, credentials, and backend responses as sensitive.
- Default to redaction of URIs, tokens, bucket names, and internal identifiers.
- Record exact format and feature versions in every bundle.
- Keep scenarios deterministic and side-effect-light wherever possible.

# Maintenance & governance plan

- Keep the core focused on metadata, replay, diffs, and bundle schemas.
- Version backend adapters separately.
- Grow a public corpus of tiny but semantically tricky catalog/table fixtures.
- Avoid absorbing engine execution or warehouse orchestration concerns.

# Milestones

## 0.1
- catalog/table snapshots
- lockfiles
- bundle writer

## 0.2
- scenario replay
- semantic diffs
- optional Delta/UniForm visibility checks

## 1.0
- stable `*.lakehousebundle.zip`
- public fixture corpus
- documented compatibility policy for catalog and table feature packs

# Open questions

- What minimum Delta/UniForm comparison is useful without recreating an engine?
- Which catalog errors should be normalized semantically versus preserved verbatim?
- How should asynchronous metadata generation be represented in replay cases?

# Sources

- Apache Iceberg REST Catalog Specification: https://iceberg.apache.org/rest-catalog-spec/
- Apache Iceberg overview: https://iceberg.apache.org/
- Delta Kernel: https://docs.delta.io/delta-kernel/
- Delta Universal Format (UniForm): https://docs.delta.io/delta-uniform/
- `iceberg`: https://crates.io/crates/iceberg
- `iceberg-catalog-rest`: https://crates.io/crates/iceberg-catalog-rest
- `deltalake`: https://crates.io/crates/deltalake
