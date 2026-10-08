---
id: P-0108
title: Durable Execution Interop & Conformance Kit
status: idea
domains: [distributed-systems, workflows, durability, testing, interop]
last_reviewed: 2026-03-05
evidence:
  - https://temporal.io/blog/what-is-durable-execution
  - https://github.com/temporalio/sdk-core
  - https://crates.io/crates/temporalio-sdk
  - https://github.com/iopsystems/durable
  - https://crates.io/crates/flawless
---

# Problem

“Durable execution” (a.k.a. workflow replay / durable workflows) is a powerful reliability primitive, but in Rust it’s currently **ecosystem-fragmented**:
- multiple engines exist (Temporal Rust SDK, durable, Flawless, others),
- each has its own history/event model,
- testing + determinism practices are inconsistent,
- and switching engines (or sharing workflow logic) is rarely feasible.

# What it provides

A **small, stable interop layer** that other durable-exec engines can target, plus a conformance suite:

1. **A canonical “workflow history” schema** (versioned):
   - event log with deterministic ordering rules
   - timer/sleep representation
   - activity calls (external side effects) as explicit events
   - signals/queries
   - retry policies + backoff metadata
   - workflow task boundaries (replay checkpoints)

2. **A replay harness API**:
   - `ReplayHost` trait that runs workflow code against a provided history and either:
     - produces the same decisions (pass), or
     - emits a minimal failing history slice (`minimized.history.json`).

3. **Interop adapters** (initial targets):
   - Temporal: adapter around `temporalio-sdk` history / commands
   - durable engine: adapter around its internal persisted log
   - Flawless: adapter around its execution log model

4. **Conformance packs**:
   - standard test vectors: timers, cancellation, retries, signals, nondeterminism traps
   - “bug history” corpus (real issues, anonymized)
   - fuzz harnesses for history decoding + minimization

5. **Artifact-first UX**:
   - `*.wf_history.json` + `*.wf_bundle.zip` (history + workflow binary hash + env + failing seed)
   - `cargo wf-replay` runner that can be used in CI and issue reports.

# Users & user stories

- **Engine authors**: “I want to compare my semantics to others and avoid subtle replay traps.”
- **App developers**: “I want deterministic replay locally and a bug bundle I can attach to an issue.”
- **Platform teams**: “I want to validate upgrades (engine/runtime) don’t change semantics.”

# Prior art (and why it’s insufficient)

- Temporal defines durable execution concepts and ships core + SDKs, but interop with non-Temporal engines is not a goal. (See evidence.)
- `durable` and `flawless` prove the space is active in Rust, but there’s no shared replay contract. (See evidence.)

# Design goals

- **Small surface area**: standardize only what enables replay + portability.
- **Deterministic by construction**: explicit “side effect points” and stable event ordering rules.
- **Conformance > ideology**: the test corpus is the real spec.

# Non-goals

- Not a one-size workflow engine.
- Not a distributed runtime or server — this is client/runtime semantics + testing.

# Architecture & API sketch

- Crate: `durable_interop`
  - `HistoryV1` (serde) + validation
  - `Decision` model (timers, activities, complete/fail/cancel)
- Crate: `durable_conformance`
  - vector tests + minimizer (delta-debugging)
- Optional: `cargo-wf-replay`
  - run a workflow crate’s replay tests against bundled histories

# Security / safety model

- Treat histories as untrusted input: strict validation + fuzzing.
- Provide “redaction helpers” for workflow data payloads.

# Maintenance & governance

- Versioned history schema with explicit backwards-compat policy.
- Reference adapters maintained “best effort”; engines can own their adapters.

# References

See evidence links in frontmatter.
