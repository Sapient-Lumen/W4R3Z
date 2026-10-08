---
id: P-0088
title: Columnar Data Interop Kit (Arrow/Parquet subset + adapters + conformance vectors)
status: idea
domains: [data, interop, arrow, parquet, analytics, io]
last_reviewed: 2026-03-05
evidence:
  - https://arrow.apache.org/blog/2025/10/30/arrow-rs-57.0.0/
  - https://crates.io/crates/datafusion-datasource-parquet
  - https://users.rust-lang.org/t/arrow-parquet-official-vs-2/82963
---

# Problem

Rust has strong columnar/data tooling (Arrow, Parquet, DataFusion), but end users still hit pain:
- multiple Arrow “ecosystems” (official arrow-rs vs other implementations) and version friction
- incomplete/awkward interop between crates and versions
- “getting data in/out” across IPC/Parquet/object stores is still glue-heavy
- many libraries need *a stable, minimal columnar interface* without depending on a huge stack

# What it provides

A **Columnar Data Interop Kit** (“datakit”) aimed at *interoperability-first*:

## 1) A stable minimal columnar core
- schema + datatype model (subset, explicitly versioned)
- buffers + validity bitmaps + offsets conventions
- an optional “C Data Interface” bridge for FFI and cross-crate interop

## 2) Adapter layer to major implementations
- adapters for arrow-rs and arrow2-style arrays (feature-gated)
- “loss map” documentation: what can/can’t roundtrip

## 3) Artifact formats & tooling
- reference readers/writers:
  - Arrow IPC streaming/file (core subset)
  - Parquet subset with predictable feature flags
- object-store friendly IO helpers (range requests, async)
- `cargo data doctor` to validate schemas/roundtrips and spot compatibility traps

## 4) Conformance vectors
- `.datavec` packs:
  - schemas + record batches + expected serialized bytes
  - cross-version expectations
- CI runner to ensure adapters stay correct

# Users & user stories

- **Data tool authors**: “I want to accept columnar data without forcing one Arrow implementation.”
- **App teams**: “I want stable read/write pipelines without dependency explosions.”
- **Interop maintainers**: “I want conformance vectors, not tribal knowledge.”

# Prior art (and why it’s insufficient)

- Arrow Rust is fast and evolving, but consumers often struggle with versioning and cross-crate interop.
- Discussions comparing implementations highlight real gaps around object store integration and ecosystem coordination.

# MVP

- minimal core types + `.datavec` format + runner
- arrow-rs adapter (read-only first)
- IPC streaming writer/reader for the subset
- a small “roundtrip matrix” doc + example repository

# v1 path

- Parquet subset (read + write)
- object store “range IO” reference implementation
- second adapter (arrow2) to prove the abstraction

# Design risks / mitigations

- **Scope creep**: keep the core small; make adapters optional.
- **Competing standards**: be explicit that this is an interop shim, not “Arrow replacement.”
