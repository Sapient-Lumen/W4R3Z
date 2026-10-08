---
id: P-0078
title: Structured Concurrency Standard Kit — portable nurseries + cancellation contracts for async Rust
status: idea
domains: [async, concurrency, correctness, runtimes, tooling]
last_reviewed: 2026-03-04
evidence:
  - https://crates.io/crates/futures-concurrency
  - https://github.com/nikomatsakis/moro
  - https://kobzol.github.io/rust/2025/01/15/async-rust-is-about-concurrency.html
---

## Problem
Async Rust ecosystems often encourage “spawn and hope you remember to join/cancel”. Libraries cannot reliably express:
- task lifetime structure (parent/child)
- cancellation propagation guarantees
- panic/error aggregation policies

There are promising pieces (`moro`, `futures-concurrency`, runtime-specific structured spawn crates), but there is no **runtime-agnostic standard contract** that libraries can target.

## Thesis
Structured concurrency should be as foundational as `Iterator`:
- small core traits
- rich combinators
- clear cancellation semantics
- portable across runtimes

## What it should provide other people (MVP)
### 1) Nursery traits
- `Nursery` / `Scope` trait:
  - `spawn(F) -> ChildHandle`
  - `join(self) -> Result<…>`
  - explicit cancellation hooks
- Runtime adapters (Tokio, async-std, smol)

### 2) Cancellation algebra with guarantees
- `CancelToken` that is cheap to clone and propagate
- “drop means cancel” vs “drop means detach” is explicit and testable
- timeouts as composable wrappers

### 3) Error & panic policy
- configurable:
  - first error cancels siblings
  - collect-all errors
  - panic = abort scope vs convert to error

### 4) Introspection hooks
- task tree export (IDs, parent links, tags)
- optional integration with `tracing` for visualization

### 5) Test suite & soundness frontier
- loom-friendly mode
- Miri smoke tests for tricky drop/cancel patterns
- documented “what is impossible safely” (the frontier)

## “Epic” extension ideas
- Interop guidelines for library authors (“how to accept a nursery from your caller”)
- Compatibility with observability tooling (Tokio console-style UIs)
- A reference implementation that emphasizes boring correctness over speed
