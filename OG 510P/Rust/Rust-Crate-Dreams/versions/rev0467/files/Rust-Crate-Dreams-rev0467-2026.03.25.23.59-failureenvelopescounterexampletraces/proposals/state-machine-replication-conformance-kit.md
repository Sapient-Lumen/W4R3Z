---
id: P-0158
title: State Machine Replication Conformance Kit
status: idea
domains: [distributed-systems, testing, conformance, networking, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/openraft
  - https://github.com/tikv/raft-rs
  - https://docs.rs/raft
  - https://databendlabs.github.io/openraft/
---
# Problem

Rust has excellent Raft engines, but teams repeatedly re-invent the same “product layer” and repeatedly ship subtle correctness bugs:

- Incomplete or inconsistent **membership-change** and **reconfiguration** semantics across products.
- Weak/absent **adversarial testing** (partitions, reorder, duplication, disk faults) until production.
- No shared way to publish and compare **correctness claims**, invariants, and “what passed”.

Today, openraft explicitly warns about pre-1.0 instability, and raft-rs documents that it provides the *core consensus module only* (you still provide log/storage/state-machine/transport). That’s the right modularity—but it leaves a big integration/testing gap.

# What it should provide

A crate suite that makes “SMR correctness” *measurable, repeatable, and comparable* across implementations and products.

## 1) A standard test surface (traits + invariants)

- A minimal **SMR harness trait** that can wrap:
  - openraft-based apps,
  - raft-rs-based apps (and any other Raft-like engines),
  - “not-Raft” SMR protocols later (e.g., EPaxos variants).
- Standardized invariants and oracles:
  - linearizability checks (configurable),
  - log matching + commit monotonicity,
  - membership safety properties,
  - snapshot/install-snapshot correctness,
  - “no phantom reads” / “no lost updates” for common KV patterns.

## 2) A conformance corpus + scenario library

- Curated scenario packs:
  - partitions, split brain attempts, flapping links,
  - leader churn, slow followers, clock skew models,
  - disk stalls, partial writes, fsync lies (profiled),
  - restarts during snapshot and compaction windows.
- “Interop mode” that runs *the same scenarios* across multiple backends and reports diffs.

## 3) Artifact-first failure bundles

A portable `smrbundle.zip` that contains:
- seed, scenario config, topology,
- event log and message trace (redacted option),
- timeline summary, invariants evaluated,
- minimal replay script.

These bundles are the unit of collaboration: maintainers can reproduce and triage without reconstructing bespoke environments.

# MVP plan (0.1 → 0.3)

1. **Harness core**: scenario runner + event model + invariant evaluation API.
2. **First adapters**:
   - openraft sample KV (`openraft-memstore`-style) adapter,
   - raft-rs `RawNode` adapter with MemStorage baseline.
3. **Top 12 scenarios** (small but vicious).
4. `cargo smr test` and `cargo smr bundle` (thin CLI wrapper).

# v1 plan

- Differential harness (run A vs B on same seeds; diff results and traces).
- Stable “claims file” for projects: `smr-claims.toml` (what you promise; what you tested).
- CI profiles: quick PR mode + nightly chaos mode.
- Loom/Miri-friendly “small model” for parts of the harness (as feasible).

# Design constraints & sharp edges

- Make determinism *opt-in but first-class*: every run should be seedable and serializable.
- Keep the harness protocol-agnostic: Raft-first is fine; don’t bake Raft terms into every trait.
- Avoid “one true transport”: support simulation transports and real transports.

# Why this is epic

It upgrades Rust’s distributed-systems story from “we have strong engines” to “we have portable correctness evidence”. That’s a force multiplier for every storage system, coordinator, and control-plane written in Rust.
