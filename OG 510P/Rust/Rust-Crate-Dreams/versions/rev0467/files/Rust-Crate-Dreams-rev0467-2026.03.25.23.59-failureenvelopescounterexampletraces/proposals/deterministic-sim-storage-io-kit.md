---
id: P-0127
title: Deterministic Simulation Storage I/O Kit (disk/fs simulator + fault injection)
status: idea
domains: [distributed-systems, testing, determinism, storage, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/turmoil/latest/turmoil/
  - https://github.com/tokio-rs/turmoil
  - https://crates.io/crates/madsim
  - https://docs.rs/madsim
  - https://databases.systems/posts/open-source-antithesis-p1
  - https://www.polarsignals.com/blog/posts/2025/07/08/dst-rust
---

# Problem

Deterministic simulation testing is a superpower for async/distributed systems: it shakes out rare races and lets you reproduce the exact failure. citeturn1search24turn1search8  
Rust has strong simulation-oriented frameworks (e.g., turmoil and madsim) that emphasize deterministic scheduling and failure injection. citeturn0search0turn1search0

But *storage* is often the missing leg of the stool:

- real disk I/O reintroduces nondeterminism (timing, ordering, fs semantics),
- failure injection for durability (partial writes, torn pages, rename semantics) is ad-hoc,
- replayable “durability bug bundles” are rare.

This creates a gap: teams can test network chaos deterministically, but not the durability edge cases that actually page you at 3am.

# What it should provide other people

## 1) A deterministic storage model + adapters

- A simulated block device + filesystem layer with explicit **ordering and latency control**
- Deterministic time + seeded scheduling integration (turmoil/madsim/tokio-test)
- Adapters for common async I/O traits (Tokio, futures, std::fs façade)

## 2) Fault injection profiles (curated and named)

Examples:
- `power_loss_after(n_writes)`
- `rename_not_atomic`
- `fsync_lies(p=0.01)`
- `partial_write(max_bytes=k)`
- `disk_full_at(byte_offset)`

## 3) A standard failure artifact: `*.storagesim.zip`

- model config + seed
- operation trace (logical fs ops)
- injected faults timeline
- minimal reproducer harness
- `report.json` with invariant violations

# MVP (2–4 weeks)

- In-memory deterministic file store with:
  - ordered writes,
  - rename + fsync semantics toggles,
  - seeded latency model
- “trace + replay” harness
- `storagesim.zip` bundle emitter + reader

# v1 (8–12 weeks)

- Block-device model + journaled FS semantics (simplified but principled)
- Integration shims for:
  - `tokio::fs`-like APIs,
  - a “virtual std::fs” facade for libraries
- Compatibility layers for turmoil/madsim runtimes
- Corpus of real-world failure patterns (e.g., crash consistency litmus tests)

# Conformance & testing

- Litmus tests for fs semantics (rename/fsync ordering)
- Differential testing: compare simulated vs real FS behaviors for a subset
- Fuzz the operation trace + fault schedule; minimize failing traces

# Adoption plan

- Provide drop-in test macros: `#[storagesim::test(seed = ...)]`
- Provide “bring your own storage trait” adapters so DBs can opt-in incrementally
- Ship curated profiles so users don’t need to be storage experts on day 1

# Risks / edge cases

- Over-promising realism: keep scope explicit; focus on *reproducible* semantics
- OS/filesystem differences: model profiles per platform; provide “portable baseline”
- API surface sprawl: start with a small “virtual fs” trait + adapters
