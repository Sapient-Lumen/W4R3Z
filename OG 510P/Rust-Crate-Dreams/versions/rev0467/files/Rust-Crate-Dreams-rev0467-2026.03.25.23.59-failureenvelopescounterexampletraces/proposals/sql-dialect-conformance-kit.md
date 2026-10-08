---
id: P-0139
title: SQL Dialect Conformance Kit — sqllogictest corpora + multi-engine diffs + portable failure bundles for Rust SQL engines
status: idea
domains: [databases, testing, devtools, data]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/sqllogictest
  - https://github.com/risinglightdb/sqllogictest-rs
  - https://crates.io/crates/datafusion-sqllogictest
  - https://github.com/apache/datafusion/issues/13812
needs:
  - A neutral, repeatable way to measure **SQL correctness drift** over time (and across engines) without each project reinventing harness glue.
  - A standard artifact format for “this query failed under this dialect + planner config”, to make bug reports actionable.
  - Dialect-aware corpora curation: tests should declare their dialect expectations and tolerated differences.
non_goals:
  - Replacing each engine’s internal tests; this is about shared corpora, standard harness interfaces, and actionable evidence bundles.
---

## What this crate should provide

### 1) A shared conformance corpus format
Build on `.slt` (sqllogictest) but standardize metadata headers:

- dialect expectations (e.g., “postgres-ish”, “sqlite-ish”, “ansi-core”)
- feature flags (window functions, json, regex, etc.)
- determinism requirements (stable ordering rules)
- numeric tolerance rules

### 2) Multi-engine runner + diff reports
A `cargo sql-conformance` CLI that can:

- run corpora against one engine (regression mode)
- run differential tests against 2+ engines (triangulation mode)
- emit `conformance-report.json` with:
  - failures grouped by feature/dialect
  - minimized repro cases
  - stable “fingerprints” for recurring failures

### 3) Portable failure bundles
Standardize `*.sqlfail.zip`:

- `case.slt` (minimized)
- `inputs/` datasets (CSV/JSON/Parquet as needed)
- `engine-config.json` (planner settings, runtime, extensions)
- `observed.json` (results/errors)
- `expected.json` (oracle results or alternative-engine results)
- `notes.md`

### 4) Engine adapter trait
A small trait surface so engines can plug in without heavy deps:

- `execute(sql: &str) -> Result<Table, Error>`
- `load_fixture(dataset) -> Result<()>`
- `capabilities() -> CapabilitySet` (declares supported features)

## MVP plan
- Ship the artifact formats (`sqlfail.zip`, `conformance-report.json`)
- Provide adapters for:
  - DataFusion (via `datafusion-sqllogictest`)
  - SQLite (via rusqlite) as a baseline oracle for a subset
- Curate 200–500 tests:
  - start with a small ANSI core subset + tricky semantics (NULLs, joins, aggregates)
  - add a “planner regression” lane (predicate pushdown / constant folding edge cases)

## v1 plan
- Add optional “fuzz lane”: generate random queries, minimize with delta-debugging
- Add CI “compat matrix” output:
  - engine version × feature flags × dialect profiles
- Add a “triangulation mode” that runs 3 engines and flags “odd one out”.

## Adoption strategy
- Make it easy for engine maintainers to accept bug reports:
  - `sqlfail.zip` should be attachable to issues
  - `cargo sql-conformance replay` should reproduce without network
- Encourage projects to publish “conformance badges” by profile (not a single score).

## Risks and mitigations
- **False positives** from dialect differences: require explicit metadata + capability checks.
- **Data-dependent nondeterminism**: enforce ordering rules and deterministic seeds in harness.
