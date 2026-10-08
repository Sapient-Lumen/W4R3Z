---
id: P-0132
title: Formal Spec ↔ Rust Test Connector Kit (TLA+/Apalache/embedded model checking → replayable corpora)
status: idea
domains: [formal-methods, correctness, testing, devtools, distributed-systems]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/tla-checker
  - https://docs.rs/tla-connect
  - https://github.com/stateright/stateright
  - https://github.com/spacejam/tla-rust
---

# Problem

Formal methods in Rust are *real* but fragmented:

- TLA+ (and Apalache) can generate traces; several projects integrate it into testing.
- Rust has model checking efforts and embedded model checkers (e.g., actor-model with exploration UIs).
- There are crates emerging around TLA tooling written in Rust.

What’s missing is a **single, ergonomic, cargo-native bridge** that turns specifications into:
- replayable test corpora,
- CI-friendly reports,
- and minimized counterexample bundles.

# What it should provide other people

## 1) A unified “spec → traces → replay” pipeline

A crate + `cargo model` that supports:
- `cargo model check`: run a checker (TLA/TLC-like, Apalache, embedded checker) and output a normalized report.
- `cargo model gen-traces`: generate traces/corpora (ITF or another normalized format).
- `cargo model replay`: replay traces against a Rust `Driver` trait with assertions.

## 2) Standard artifacts

- `model-report.json`: model name, params, invariants, counterexample summary, tool version.
- `model-corpus.zip`: traces + metadata + seeds + environment.
- `counterexample.zip`: minimized traces + readable “story” markdown + reproduction harness.

## 3) Adapters (pluggable backends)

- `tla-checker` / tla-rs integration for an all-Rust stack
- Apalache integration via `tla-connect` style ITF traces
- optional “embedded checker” backend using `stateright`-like exploration for Rust-native models

# MVP scope

- Replay harness with a clean `Driver` interface
- One backend: Apalache → ITF → replay (batch)
- One backend: `tla-checker`-style check + emit traces
- A minimal “minimizer” pass: shrink traces (delta-debug) while preserving invariant violation

# v1 scope

- Parameter sweeps with comparison tables
- Coverage-style metrics (“how much behavior space did we explore?”)
- Interactive UI hooks (TUI/web) for exploring counterexamples
- Loom/Miri-friendly hooks for invariants inside the Rust implementation

# Conformance & testing

- Fixture specs with known counterexamples (locks, leases, leader election)
- Golden traces that must replay deterministically
- Cross-check: compare invariant outcomes between backends where possible

# Risks and constraints

- “Spec drift”: make the artifact bundles include spec source + tool version + params.
- Tool availability in CI: provide containerized backends and pure-Rust modes.

