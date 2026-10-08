---
id: P-0090
title: Deterministic Rollback + Replay Kit — snapshots, netcode glue, and shareable bug bundles
status: idea
domains: [networking, determinism, testing, games, distributed-systems]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/ggrs
  - https://docs.rs/ggrs
  - https://johanhelsing.studio/posts/extreme-bevy
---

## Problem
A huge class of “hard bugs” share a root cause: **nondeterminism** under concurrency/networking/time.
Even when the domain is not games (robotics, collaborative tools, simulations, trading, IoT swarms),
teams keep reinventing the same machinery:
- deterministic stepping (time, RNG, ordering)
- state snapshots / deltas
- replay of recorded inputs
- rollback when late inputs arrive
- shareable reproductions (“this exact scenario broke on machine X”)

Rust has strong building blocks (e.g., GGRS for rollback netcode), but there’s no **general-purpose, domain-neutral kit** that standardizes artifact formats and testing workflows across engines/frameworks.

## What it provides
A crate family + reference formats that give other people:

1) **Deterministic core (`detcore`)**
   - `StepClock` abstraction (fixed-tick stepping; pluggable wallclock mapping)
   - `DetRng` wrapper with explicit seeding and version tagging
   - Ordering guards (stable iteration helpers; “nondet detector” features)

2) **Snapshot & diff layer (`detsnap`)**
   - `Snapshot` trait: serialize/deserialize + hash + versioning
   - Optional delta encoding hooks (for large states)
   - Built-in “state hash timeline” instrumentation

3) **Rollback engine (`detrollback`)**
   - Generic rollback loop (late input handling; re-sim to present)
   - Pluggable transport/input source
   - Bounded memory policies (ring buffers; checkpoint intervals)

4) **Replay & bug bundles (`.replay.zip`)**
   - Standard artifact: initial snapshot + input log + version manifest + optional minimized trace
   - `cargo replay run` and `cargo replay minimize`
   - Deterministic verification: “replay should produce identical hashes”

5) **Interop adapters**
   - Optional adapters for popular stacks (e.g., Bevy, macroquad, winit), but keep the core engine-agnostic.

## Users & user stories
- **Game/real-time dev:** “I want rollback netcode without writing my own snapshot/replay format.”
- **Simulation/robotics:** “I want deterministic repro bundles for field failures.”
- **Distributed systems testing:** “I want a deterministic event log + replay harness I can run in CI.”

## Prior art (and why it’s insufficient)
- **GGRS** provides rollback networking and a safer control flow than GGPO-style callbacks, and is used in real projects. The missing piece is a *general* deterministic/snapshot/replay artifact standard and cargo-native tooling that can serve many domains.  
  Evidence: GGRS crate + docs, plus real-world usage writeup.

## Design sketch
### Artifact-first approach
Everything is built around `.replay.zip`:
- `manifest.json` (versions, feature flags, platform info)
- `initial.snapshot` (stable format, versioned)
- `inputs.log` (tick-indexed inputs/events)
- optional `trace/` (logs, span summaries, minimization steps)

### Determinism contracts
- Require the integrator to provide:
  - `apply_input(tick, input)`
  - `step(tick)`
  - `snapshot()` / `restore(snapshot)`
- The kit provides:
  - hash timeline checks
  - “divergence finder” (binary search tick where hashes split)
  - minimizer for inputs (delta-debugging style)

### Conformance & testing
- Provide conformance fixtures:
  - “late input” scenarios
  - checksum divergence detection
  - snapshot compatibility across versions

## MVP scope
- `detcore` + `detsnap` + `.replay.zip` format
- `cargo replay run` for running and verifying a replay
- minimal rollback engine with a toy demo + docs

## v1 scope (epic)
- minimizer + divergence finder
- adapters for 1–2 engines
- CI harness templates
- optional integration with tracing/profilers for time travel debugging

## Risks & tradeoffs
- Determinism is platform-sensitive (float ops, threading): mitigate with “strict mode” features and clear documentation.
- Scope creep: stay artifact-first, keep adapters optional.

## Why this is “epic”
It makes deterministic reproduction *portable* across projects — turning “works on my machine” into “here is a replay bundle that proves the bug.”
