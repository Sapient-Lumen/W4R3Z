---
id: P-0324
title: SDMX 3.0 Conformance & Canonicalization Kit — structure-aware query lockfiles, semantic dataset diffs, and reproducible statistics-exchange bundles
status: idea
domains: [data, statistics, sdmx, metadata, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://sdmx.org/standards-2/
  - https://github.com/sdmx-twg
  - https://github.com/sdmx-twg/sdmx-tck
  - https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/sdmx3.0
  - https://docs.rs/sdmx_json
  - https://github.com/neoncitylights/sdmx
---

# Problem

Rust now has early SDMX substrate, but the real difficulty is not deserializing one JSON response. It is keeping **structure, query, and data meaning aligned** across changing statistical systems:

- a query that still returns data but under a changed structure definition,
- dimension/version drift that silently changes interpretation,
- asynchronous or partial deliveries that are hard to compare semantically,
- REST, JSON, CSV, and structural metadata assumptions drifting apart,
- and analytical regressions that still travel as spreadsheets and hand-edited notes.

The worthy crate contribution is a **SDMX 3.0 conformance and canonicalization kit** that binds structure metadata, queries, and observations into version-pinned, diffable, replayable artifacts.

# What it provides

- `sdmx-ir` — canonical IR for structures, codelists, dimensions, attributes, observations, metadata attachments, and query context.
- `sdmx-lock` — lockfiles pinning REST API expectations, structure versions, content constraints, formats, and retrieval assumptions.
- `sdmx-verify` — semantic checks for structure/data coherence, observation-key integrity, metadata attachment validity, and response-shape expectations.
- `sdmx-diff` — explainable diffs: “dimension meaning changed”, “codelist version changed semantics”, “query now resolves to different structure”, “observation count differs only because filter semantics changed”.
- `sdmx-replay` — deterministic query/reply replay for regression testing and provider comparison.
- `cargo sdmx` — emit `*.sdmxbundle.zip` for data-pipeline bugs, provider migrations, and reproducible statistical ingestion tests.

# What the crate should provide other people

1. **Structure-aware diffs** instead of raw JSON/CSV comparisons.
2. **Query lockfiles** that freeze the exact assumptions behind a dataset pull.
3. **Replayable provider bundles** for API regressions and migrations.
4. **A bridge between Rust SDMX substrate and actual data-engineering workflows**.
5. **Deterministic evidence** for “the data changed” versus “the structure changed.”

# Persona / who it’s for

- Statistical-data platform teams
- Public-data ingestion and ETL developers
- Central-bank and public-sector data engineers
- Researchers maintaining reproducible SDMX pipelines
- QA teams validating SDMX provider compatibility

# Users & user stories

- **Data engineer**: “Did this pull fail because the API changed, or because the structure version changed?”
- **Research pipeline owner**: “Pin this dataset pull so we can reproduce the same shape six months later.”
- **Provider operator**: “Compare two SDMX implementations semantically, not only by HTTP payload.”
- **Auditor**: “Show which structural assumptions were in force when this extract was produced.”

# Prior art (and why it’s insufficient)

- SDMX 3.0 is established across official standards materials and public API deployments.
- The SDMX TWG maintains machine-readable specs and even a TCK for RESTful services.
- Eurostat exposes real SDMX 3.0 APIs and guidance, which makes provider-facing replay practical.
- Rust substrate exists in `sdmx_json` and the `neoncitylights/sdmx` project.
- But there is still no boring-default Rust layer for **query lockfiles + structure-aware diffs + replayable evidence bundles**.

# Design goals

1. **Structure-first** — data without pinned structures is not reproducible enough.
2. **Semantic comparison** — compare meaning, not only serialized shape.
3. **Format-neutral core** — JSON, CSV, and XML should meet in one IR where practical.
4. **Provider reproducibility** — queries and responses must be replayable offline.
5. **Statistical humility** — distinguish transport, structure, and content findings clearly.

# MVP surface

- Minimal types: `StructureSnapshot`, `DataPull`, `QueryLock`, `SdmxReport`, `DatasetDelta`
- Minimal functions:
  - `load_structure()`
  - `lock_query()`
  - `verify_pull()`
  - `diff_pull()`
  - `write_bundle()`
- Feature flags:
  - `json`
  - `csv`
  - `rest`
  - `metadata`
  - `redaction`

# Compatibility story

- Interoperates with SDMX 3.0 REST workflows first.
- Should accept existing Rust parsers as adapters rather than replacing them.
- Intentionally avoids becoming a full analytics engine or warehouse.

# Conformance & fixtures

- Synthetic structure/data fixtures with known version drift.
- Query lockfiles for common API patterns.
- Response bundles from at least one public SDMX 3.0 provider.
- Optional adapter to SDMX TCK scenarios where feasible.

# Path to boring stability

- Freeze IR around a narrow but representative observation/structure subset.
- Keep query-lock semantics explicit and hashable.
- Prove diff quality against public SDMX provider examples.
- Expand format coverage only after structure/data coupling is stable.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library/CLI that pins one SDMX 3.0 REST query against one structure snapshot, validates the returned data semantically, diffs it against a previous pull, and emits a reproducible `*.sdmxbundle.zip`.

# De-risk plan

1. Start with JSON data/structure messages and REST query locks.
2. Treat CSV/XML as adapters once the IR stabilizes.
3. Use public Eurostat-style queries for an initial corpus.
4. Add asynchronous and provider-quirk handling later.

# Non-goals

- Not a BI/visualization layer.
- Not a full statistical computation engine.
- Not a replacement for provider-specific API docs.

# Architecture & API sketch

```rust
pub struct SdmxReport {
    pub profile_id: String,
    pub verdicts: Vec<Verdict>,
    pub structure_findings: Vec<StructureFinding>,
    pub query_findings: Vec<QueryFinding>,
    pub diffs: Vec<DatasetDelta>,
}

pub fn verify_pull(lock: &QueryLock, pull: &DataPull) -> SdmxReport;
```

Bundle draft: `lock.toml`, `structure/*.json`, `query/request.json`, `response/body.bin`, `normalized.json`, `verdicts.json`, `diff.json`, `notes.md`.

# Security / safety model

- Bound very large responses and streaming decode paths.
- Support identifier redaction when private SDMX deployments are involved.
- Record hashes of structure snapshots and code lists.
- Preserve format provenance so “same data, different format” stays explainable.

# Maintenance & governance plan

- Ship profile packs for public providers and generic SDMX 3.0 REST assumptions.
- Keep bundle format independent of any single provider.
- Publish synthetic corpora for structure drift and metadata attachment edge cases.
- Encourage adapters rather than parser monoculture.

# Milestones

## 0.1
- Canonical IR for structure + data pull
- Query lockfiles
- Semantic validation and bundle format draft

## 0.2
- Structure-aware diff engine
- Replay support
- Public-provider fixture packs

## 1.0
- Stable `*.sdmxbundle.zip`
- Multi-format adapters
- CI-ready provider compatibility workflows

# Open questions

- How much of the REST query model belongs in core versus adapters?
- Can the IR unify data and metadata messages without becoming bloated?
- Should provider-specific quirks be profiles, patches, or separate crates?

# Sources

- SDMX standards hub: https://sdmx.org/standards-2/
- SDMX TWG org/repos: https://github.com/sdmx-twg
- SDMX TCK: https://github.com/sdmx-twg/sdmx-tck
- Eurostat SDMX 3.0 getting started: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/sdmx3.0
- `sdmx_json`: https://docs.rs/sdmx_json
- Rust SDMX monorepo: https://github.com/neoncitylights/sdmx
