---
id: P-0099
title: Schema Evolution Workbench Kit — versioned Serde data with verified migrations, reports, and fuzzable corpora
status: idea
domains: [data, serialization, reliability, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/serde-evolve
  - https://docs.rs/serde-evolve
  - https://serde.rs/
  - https://users.rust-lang.org/t/tools-for-supporting-version-migration-of-serialization-format/76292
needs:
  - teams need a boring, repeatable way to evolve persisted data formats safely
---

# Problem
Many Rust apps persist Serde-serialized state (save files, caches, DB blobs, IPC). Over time:
- Types change, fields move, enums restructure, and migrations become ad hoc.
- Regression testing of migrations is spotty; failures surface as production corruption.
- There is no standard artifact/report format to *prove* compatibility to reviewers.

A crate like `serde-evolve` shows the direction (typed migrations), but the ecosystem lacks a **workbench** that makes schema evolution *operational*.

# What it provides
- **Versioned wire schema registry**
  - `#[schema(version = N)]` derive helpers + explicit wire types
  - “domain model” separation (wire → migrate → domain)
- **Migration engine + verification harness**
  - compile-time reachable migration graph checks
  - “no data loss” assertions (opt-in, via user-defined invariants)
- **Artifacts & reports**
  - `evolve-report.json`: compatibility matrix, which versions can be read/written
  - `evolve-corpus.zip`: minimized failing cases + “golden” historical snapshots
- **Cargo UX**
  - `cargo evolve check`: run migrations + invariants + corpus
  - `cargo evolve bump`: scaffold a new wire version + migration stubs
  - `cargo evolve fuzz`: optional proptest-based corpus growth

# MVP (4–6 weeks)
- core registry + migration graph validation
- `cargo evolve check` producing a report + a “snapshot corpus” format
- CI recipe in `.github/workflows/evolve.yml`

# Design notes
- **Format-agnostic**: work with bincode/postcard/json/etc. (Serde-based)
- **Stable artifact formats**: JSON report, ZIP corpus with manifest
- **Backwards-first defaults**: support “read old forever; write new only”

# Testing & conformance
- property tests ensuring roundtrip invariants
- corpus replay runner: “re-run all historic samples” gate in CI

# Adoption path
- Start as a devtool + macros crate usable by games/services alike
- Publish “migration playbook” docs for teams

# Related work
- `serde-evolve` provides typed schema evolution primitives; this proposal focuses on the operational layer and standardized evidence artifacts.
