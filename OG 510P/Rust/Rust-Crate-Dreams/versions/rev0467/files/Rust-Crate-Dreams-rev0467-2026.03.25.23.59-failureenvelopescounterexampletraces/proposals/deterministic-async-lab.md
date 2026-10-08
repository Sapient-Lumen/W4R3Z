---
id: P-0009
title: Deterministic Async Lab — record/replay + minimization harness for async concurrency bugs
status: idea
domains: [testing, async, determinism, reliability]
last_reviewed: 2026-03-01
evidence:
  - https://docs.rs/crate/frankenlab/
  - https://s2.dev/blog/dst
  - https://crates.io/crates/sturgeon
---

## What it should provide others

A **deterministic testing harness** for async/concurrent Rust that makes heisenbugs reproducible and shrinkable.

The crate should give users:

- **Deterministic scheduler**: control task interleavings and time.
- **Record & replay**: capture nondeterministic events (timers, IO ordering) and replay them.
- **Minimization (shrinking)**: reduce failing schedules to the smallest reproducer.
- **Interop**: run existing async code with minimal changes (Tokio first, `async-std` later).
- **Forensics**: produce “schedule traces” and structured artifacts for CI.

## Why this is still missing

There are emerging crates and techniques, but adoption is scattered and APIs differ.
A “lab” crate can unify:
- a stable conceptual model (schedule, time, IO events),
- a portable artifact format (recordings),
- and best-practice docs (how to write determinism-friendly async code).

## Design outline

### 1) Virtual time + deterministic wakeups
- Replace `sleep`/`interval` with virtual time.
- Ensure waker ordering is stable and configurable.

### 2) Event log format
- A compact, versioned event stream:
  - task spawn/join
  - timer set/fire
  - RNG reads (optional feature)
  - “external inputs” (user-defined events)

### 3) Minimizer
- Delta-debugging over:
  - schedule decisions
  - timing perturbations
  - injected faults

## MVP

1. Tokio-compatible deterministic runtime wrapper for tests.
2. `#[det_test]` macro that runs a test under deterministic scheduling.
3. Record/replay of timers + task ordering.
4. Basic minimization (binary search over schedule decisions).

## Related work and gaps

- Deterministic simulation testing is a known powerful approach.
- Recent crates show feasibility; the gap is a standard artifact + a default harness.

## Adoption plan

- Start as a **test-only** dependency (no production overhead).
- Provide integration recipes for popular stacks: reqwest/hyper, channels, database clients (as far as possible).
