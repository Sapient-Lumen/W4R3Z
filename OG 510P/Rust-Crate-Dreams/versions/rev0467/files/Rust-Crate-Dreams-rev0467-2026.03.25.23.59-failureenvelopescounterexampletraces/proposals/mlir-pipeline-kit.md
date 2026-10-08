---
id: P-0130
title: MLIR Pipeline Kit — ergonomic Rust APIs + cargo workflows for MLIR-based compilers
status: idea
domains: [compilers, ml, devtools, api-bindings]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/melior
  - https://edg-l.github.io/melior/
  - https://discourse.llvm.org/t/dialect-attributes-in-mlir-c-api/87800
  - https://github.com/mlir-rs
---

# Problem

MLIR is widely used for modern compiler pipelines, but Rust teams face friction:
bindings exist, yet end-to-end “pipeline ergonomics” (pass graphs, dialect registration, textual/bytecode I/O, golden tests, reproducible repro bundles) are inconsistent and often reimplemented.

# What it provides

A practical “pipeline layer” above raw bindings:

- `mlir_pipeline_kit` library:
  - safe-ish builders for contexts/dialects/modules
  - pass-pipeline authoring helpers (typed pass lists, parameter validation)
  - deterministic serialization helpers (normalize textual output; stable printing profiles)
  - a minimal “golden test” harness (roundtrip + diff + corpus replay)
- `cargo mlir` subcommands:
  - `cargo mlir fmt` (stable printing profiles for diffs)
  - `cargo mlir test` (goldens + corpus replay; emits bundle on failure)
  - `cargo mlir bundle` (captures module + dialect/pass registry + environment)
- Standard artifact: `*.mlirbundle.zip`:
  - IR (text + optional bytecode), pass pipeline, dialect list, toolchain hashes, and a replay script.

# Users & user stories

- **Compiler engineer**: “I need to share a failing MLIR reduction as a portable bundle.”
- **ML team**: “I want stable IR diffs in CI and easy corpus replay.”
- **Bindings maintainer**: “I need conformance vectors that track MLIR C-API surface changes.”

# Prior art (and why it’s insufficient)

- `melior` provides Rust bindings to MLIR, but does not standardize testing/bundling/CI conventions or ‘pipeline UX’.
- MLIR C-API surface gaps and evolution can impact bindings; teams need a layer that isolates churn and provides robust diagnostics.

# Design goals

- **Stable diffs**: IR printing modes that are intentionally CI-friendly.
- **Reproducible bug reports**: portable `mlirbundle` artifacts.
- **Interop**: allow calling out to `mlir-opt`/friends when present, but keep a library-first mode.
- **Churn resistance**: isolate MLIR C-API changes with compatibility shims and feature gates.

# Non-goals

- Replacing melior (or other bindings).
- Shipping full MLIR toolchain binaries.

# Architecture & API sketch

- `ContextProfile`: controls dialect registration and printing options.
- `Pipeline`: typed pass graph (ordered) + parameters, serializable.
- `Bundle`: deterministic manifest + payloads; `Bundle::replay()` helper.

# Security / safety model

- Bundles are untrusted inputs: require explicit opt-in to execute replay scripts.
- Default to parsing/printing only; side-effecting execution is behind flags.

# Maintenance & governance plan

- Keep the artifact schema stable; treat it like an interop contract.
- Provide “known-good” corpus fixtures and compatibility CI across MLIR versions.

# Milestones

- **MVP**: printing profiles + `cargo mlir test` + `mlirbundle` schema.
- **v0.2**: pipeline authoring helpers + corpus tooling (minimize + replay).
- **v1.0**: version-matrix conformance suite + compatibility shims.

# Open questions

- Best boundary between in-process APIs vs external tools (`mlir-opt`) for minimization?
- How to represent pass parameters and dialect options in a stable schema?

# Sources

- `melior` crate and its documentation site.
- MLIR ecosystem org (`mlir-rs`).
- Discussion showing that C-API limitations can affect higher-level bindings.
