---
id: P-0241
title: Formal Trace Connector — bridge TLA+/Apalache-style specs to Rust tests with witness bundles
status: idea
domains: [verification, testing, reliability, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/tla-checker
  - https://users.rust-lang.org/t/tla-checker-tla-model-checker-in-rust/138086
  - https://lib.rs/crates/tla-connect
  - https://github.com/tlaplus-community/tree-sitter-tlaplus
  - https://www.stateright.rs/comparison-with-tlaplus.html
---

## What it should provide others

A practical kit that makes **formal specs produce executable, reproducible test witnesses** for Rust systems.

The crate should provide:

- A **witness bundle format** (`*.formalwitness.zip`) that records:
  - the spec version/hash
  - the model checker config
  - counterexample traces (states + actions)
  - a mapping into Rust domain events
- A **Rust test harness** that can:
  - validate traces against invariants
  - replay counterexamples against an implementation (when an adapter exists)
- **Adapters** for popular tools (start with one):
  - `tla-checker` (Rust model checker)
  - Apalache/TLC integration (via `tla-connect` style workflows)
- **Parsing support** (optional): tree-sitter TLA+ grammar packaged for Rust.

## Why this is still missing

There are promising, but disconnected, building blocks:

- `tla-checker` is an actively developed model checker in Rust.
- `tla-connect` focuses on integrating TLA+/Apalache into Rust test suites.
- Stateright shows how runnable/abstract models can be compared with TLA+ approaches.

What’s missing is a **standard witness artifact** and a **repeatable workflow**: spec → trace → bundle → CI replay.

## Design outline

### 1) Witness IR

- `State { vars: Map<String, Value> }`
- `Step { action: String, params: Map<String, Value> }`
- `Trace { states: Vec<State>, steps: Vec<Step> }`

### 2) Adapter boundary

Provide a trait:

- `SpecTraceSource`: produce `Trace` + metadata from a checker.
- `ImplAdapter`: map `Step` into concrete Rust operations.

### 3) Two usage modes

- **Spec-first**: run checker in CI, bundle counterexamples, attach to PR.
- **Impl-first**: take a witness bundle and replay against implementation.

## Minimum lovable MVP (4–8 weeks)

1. Witness IR + bundle format + CLI (`formalwitness validate|inspect`).
2. One adapter: `tla-checker` import/export.
3. One example integration: a small distributed protocol model + Rust impl adapter.

## De-risk plan

- Start with “trace validation” even without full replay (invariants over traces).
- Keep mapping optional: witness bundles are useful even before adapters mature.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (witness bundles + replay workflow)
