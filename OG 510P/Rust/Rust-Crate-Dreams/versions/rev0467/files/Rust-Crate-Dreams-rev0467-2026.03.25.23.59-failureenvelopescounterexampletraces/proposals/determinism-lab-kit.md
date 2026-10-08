---
id: P-0097
title: Determinism Lab Kit — capture/minimize/replay bundles for schedule-sensitive async bugs
status: idea
domains: [async, testing, debugging, devtools, reproducibility]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/loom/latest/loom/
  - https://docs.rs/sturgeon
  - https://docs.rs/asupersync
  - https://crates.io/crates/asupersync
---
# Problem
Many Rust bugs are schedule-sensitive (races, cancellation timing, backpressure) and hard to share:
- “works on my machine” is common for async timing issues
- teams lack a unified workflow to **capture → minimize → replay → share** nondeterministic failures

There are strong point-solutions (`loom`, stream record/replay, experimental runtimes), but no standard bundle format and cargo-native workflow.

# What it provides
A workflow + artifact format for nondeterminism:

## Replay bundle format: `*.repro.zip`
- seed + env + feature flags
- recorded timeline (spans/events) + optional stream recordings
- build metadata (git rev, rustc version, target)
- minimization notes + `repro.md`

## Determinism hooks
- seedable RNG façade + time façade for tests (`now()`, `sleep()`)
- optional executor instrumentation adapters (best-effort)

## Schedule exploration
- randomized yield injection (“schedule fuzzer”) to find failing seeds
- deeper mode: integrate with `loom` where code can be modeled

## Cargo UX
- `cargo repro record -- test_name`
- `cargo repro replay --bundle repro.zip`
- `cargo repro minimize --bundle repro.zip`

# MVP
- define schema + versioned bundle format
- time/RNG façade + yield injection helper
- record/replay driver for tests (single-thread executor first)

# v1 roadmap
- Tokio adapter (best-effort)
- shareable “bug zoo” + conformance scenarios
- optional registry/index for teams to track bundles

# Risks
- executor-level capture is hard; design must remain useful even with shallow hooks.
- bundle format stability matters; version schemas early.
