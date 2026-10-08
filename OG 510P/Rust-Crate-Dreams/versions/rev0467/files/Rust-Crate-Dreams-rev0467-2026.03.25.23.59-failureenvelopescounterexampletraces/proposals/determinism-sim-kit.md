---
id: P-0066
title: Determinism Sim Kit — state hashing, snapshots, and desync repro for rollback/prediction games
status: idea
domains: [gamedev, networking, testing, determinism, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/bevyengine/bevy/discussions/1176
  - https://github.com/cBournhonesque/lightyear
  - https://crates.io/crates/bevy_ggrs
  - https://crates.io/crates/fortress-rollback
---

# Problem
Rollback / prediction networking stacks exist in Rust, but **deterministic simulation plumbing** is still repeatedly rebuilt per project:
- canonical state hashing and “what counts as state”
- snapshot/restore (including ECS state) without accidental nondeterminism
- reproducible desync artifacts (inputs, RNG seeds, timing) suitable for CI triage

The result is high friction for game teams and many “almost deterministic” bugs.

# Users & user stories
- Bevy / ECS game teams: “I need a drop-in way to snapshot and hash state so rollback can detect/describe desyncs.”
- Networking crate authors: “I want a shared conformance harness for ‘determinism contracts’ without owning a whole engine.”
- CI owners: “When a desync happens, I want an artifact I can replay deterministically to reproduce it.”

# Prior art (and why it’s insufficient)
- Rollback stacks (`bevy_ggrs`, `fortress-rollback`, `backroll`) provide transport and integration, but typically assume the simulation is deterministic and leave hashing/snapshot standards to users.
- Engine/networking discussions highlight the need for serialization/minimal state capture for rollback, but there is no shared, reusable kit.

# Design goals
- **State hashing toolkit**:
  - pluggable hashers and canonicalization helpers (stable ordering, byte representation)
  - “state boundary” helpers (derive macros / traits to define what is included)
- **Snapshot/restore toolkit**:
  - pure-Rust snapshot format with versioning
  - adapters for common data models (ECS, component sets, dense arrays)
- **Desync repro artifacts**:
  - standard container: inputs stream, RNG seed(s), frame boundaries, build metadata
  - replay runner API and CLI
- **Conformance and fuzz support**:
  - property tests for snapshot round-trip
  - “two-run equivalence” harness (same inputs => same hashes)
- Minimal dependencies and optional `no_std + alloc` core where feasible.

# Non-goals
- A full networking library.
- A full game engine.
- “Deterministic floats everywhere” (provide helpers, don’t dictate).

# Architecture & API sketch
- `determinism-core` (library):
  - `DeterministicState` trait: `snapshot()`, `restore()`, `hash_state()`
  - `HashSink` abstraction (so projects can choose blake3, xxhash, etc.)
  - `Snapshot` versioning + codec
- `determinism-bevy` (optional adapter):
  - component filters, stable archetype ordering, resource capture
- CLI (optional): `determinism replay <artifact>` and `determinism verify <cmd>`

Pseudo-API:
```rust
trait DeterministicState {
    type Snapshot;
    fn snapshot(&self) -> Self::Snapshot;
    fn restore(&mut self, snap: &Self::Snapshot);
    fn hash_state(&self, sink: &mut dyn HashSink);
}

fn verify_equivalence<R: Replayable>(run: R, frames: u64) -> VerificationReport;
```

# MVP plan (0.1 → 0.2)
## 0.1
- Core crate: hash helpers + snapshot container format + replay artifact schema
- Harness: run command twice, compare per-frame hashes, emit repro artifact on mismatch

## 0.2
- Bevy adapter for snapshot + stable hashing
- Fuzz/minimization tooling for smaller repro artifacts

# Adoption plan
- Start as a “kit” used by one reference sample:
  - minimal Bevy game with rollback integration + determinism checks
- Provide CI recipes: “run determinism verify on PRs”
- Keep core stable; adapters evolve independently.
