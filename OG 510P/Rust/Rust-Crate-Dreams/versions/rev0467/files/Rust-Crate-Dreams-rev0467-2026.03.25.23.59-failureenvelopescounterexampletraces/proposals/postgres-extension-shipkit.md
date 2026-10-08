---
id: P-0169
title: Postgres Extension ShipKit — reproducible build/test/release for pgrx extensions
status: idea
domains: [database, postgres, tooling, release-engineering]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/pgcentralfoundation/pgrx
  - https://crates.io/crates/cargo-pgrx
  - https://archive.fosdem.org/2025/events/attachments/fosdem-2025-4317-writing-safe-postgresql-extensions-in-rust-a-practical-guide/slides/238202/writing_p_EGMYZay.pdf
  - https://docs.rs/crate/pgrx/latest/source/README.md
---

## What it should provide others

An ops-grade way to ship Postgres extensions in Rust that makes “works on my PG” a solved problem:

- A stable release artifact: `pgextbundle.zip`
  - compiled extension(s) per Postgres version + platform
  - SQL/control files, version metadata, migration notes
  - deterministic build manifest (pg_config, headers, features, rustc, linker)
  - test logs + pg_regress outputs (or pgTAP where used)
- `cargo pgext {build,test,package,doctor}`:
  - builds per-PG-version matrix (13..current) and emits reproducible manifests
  - spins ephemeral Postgres instances for integration tests
  - checks ABI / symbol export expectations and extension metadata correctness
- Distribution modes:
  - **source+tooling** (what most OSS needs)
  - **binary bundles** for controlled environments (with strict version capture)

## Why this is still missing

pgrx is strong for dev ergonomics, but the ecosystem lacks a shared **release engineering layer**:
version matrices, packaging norms, CI templates, and standardized evidence when a build fails.

## Design principles

- **Respect Postgres reality**: version/ABI matrix is central; make it cheap to test.
- **Bundles as evidence**: a maintainer can reproduce a user’s failure without access to their machine.
- **Don’t fork pgrx**: sit above it, treat cargo-pgrx as an input.

## MVP

- Bundle spec + validator
- `cargo pgext package` using existing pgrx build flows
- CI templates for Linux with a small PG version subset
- “Doctor” checks for common misconfigs (pg_config mismatch, headers, feature flags)

## v1

- Full PG matrix + macOS/Windows where feasible
- pgextbundle signatures + provenance (hooks into cargo provenance proposal)
- Extension upgrade testing harness (install old → upgrade → validate invariants)

## Risks / open questions

- Cross-platform packaging expectations vary widely (system packages vs custom deployment).
- Avoid over-promising “universal binaries”; focus on correctness and evidence.
