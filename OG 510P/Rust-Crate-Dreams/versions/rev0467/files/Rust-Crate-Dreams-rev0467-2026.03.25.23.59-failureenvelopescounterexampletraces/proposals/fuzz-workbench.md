---
id: P-0080
title: Fuzz + Property Testing Workbench — a unified harness for generative testing, fuzzing, shrinking, and bug bundles
status: idea
domains: [testing, fuzzing, reliability, security, tooling]
last_reviewed: 2026-03-04
evidence:
  - https://rust-fuzz.github.io/book/cargo-fuzz/guide.html
  - https://google.github.io/oss-fuzz/getting-started/new-project-guide/rust-lang/
  - https://github.com/proptest-rs/proptest
  - https://docs.rs/proptest-stateful/
---

## What it should provide others

A single “happy path” for **generative testing at scale** in Rust that covers:

- classic property tests (Proptest-style shrinking),
- stateful/model-based tests,
- fuzzing (libFuzzer/corpus-driven),
- and *reproducible*, shareable failure artifacts (“bug bundles”).

The crate should let a team go from “we have tests” to “we continuously discover weird edge cases and can reproduce them on any machine” without building a bespoke harness.

## Why this is missing / the pain

Today you can fuzz with `cargo-fuzz` and do property testing with `proptest`, but the *workflow glue* is fragmented:
- corpus management, minimization/reduction, and failure artifact formats aren’t standardized;
- state-machine tests tend to be bespoke (hard to scale across teams);
- CI integration and “share this bug with a coworker” is still surprisingly ad‑hoc.

This proposal is to make **a first-class workbench** that *orchestrates* existing engines where possible, but adds the missing standard surfaces.

## Core deliverables (MVP)

### 1) A stable “bug bundle” format
A directory (or zip) that contains:
- failing input(s) (bytes and/or typed seed),
- engine metadata (fuzzer/strategy versions, features, MSRV, target triple),
- minimized reproducer (if available),
- stack trace + sanitizer logs (if present),
- and an optional “replay script” (`cargo test -p ... -- --exact ...` equivalent).

Goal: teams can attach a single artifact to an issue and anyone can replay it.

### 2) Unified runner API + CLI
- `cargo gencheck` (name placeholder): run property tests, stateful tests, and fuzzers under one command.
- Profiles: `quick`, `ci`, `overnight`, `oss-fuzz`.
- One place to configure: timeouts, max cases, shrinking/minimization budget, sanitizers, feature matrices.

### 3) Stateful/model-based testing that scales
Ship an opinionated pattern:
- “model” trait for state,
- action generation strategies,
- postconditions/invariants,
- automatic shrinking of action sequences,
- **trace capture** (what actions ran) and deterministic replay.

### 4) Corpus interoperability layer
- Import/export corpora between property tests and fuzz targets.
- Deduping, coverage heuristics (best-effort), and long-term storage layout.

## Design: how it should fit into Rust projects

### Library API
- `workbench::Harness` — registers suites (property/stateful/fuzz).
- `Suite` trait with hooks for:
  - “generate next case”
  - “execute”
  - “shrink/minimize”
  - “serialize seed”
- Transparent adapter layers for:
  - Proptest strategies,
  - libFuzzer-style `&[u8] -> ()`,
  - and model-based sequences.

### CLI and config
- `workbench.toml` or `[package.metadata.workbench]` in `Cargo.toml`
- Targets per crate, with feature matrices and platform constraints.

### Conformance & fixtures
Ship a `workbench-conformance` package:
- golden bug bundles,
- reference shrinking cases,
- determinism checks (same seed => same trace),
- and “no flake” fixtures for CI.

## Non-goals (initially)
- writing a brand-new fuzzer engine (use existing backends)
- guaranteeing cross-platform sanitizer availability
- providing coverage instrumentation beyond “best effort” integrations

## Related work (and why it’s not enough)
- `cargo-fuzz` is excellent for libFuzzer integration, but it’s fuzzing-first and doesn’t standardize artifact formats.  
- `proptest` provides strong shrinking-based property tests but doesn’t solve corpus lifecycle + shareable failure artifacts across multiple engines.  
- `proptest-stateful` helps stateful property testing, but the ecosystem still lacks a unified workflow and artifact standard that teams can adopt broadly.

## Adoption plan
1. Start with **artifact format + replay** (value immediately).
2. Add Proptest + `cargo-fuzz` adapters.
3. Add state-machine layer + shrinking of action sequences.
4. Add CI profiles + OSS-Fuzz oriented layout.

## Sustainability hooks
- Keep the workbench small: core types + adapters + format.
- Make adapters optional features (avoid dependency explosions).
- Treat the bug bundle format as the long-lived stable contract.
