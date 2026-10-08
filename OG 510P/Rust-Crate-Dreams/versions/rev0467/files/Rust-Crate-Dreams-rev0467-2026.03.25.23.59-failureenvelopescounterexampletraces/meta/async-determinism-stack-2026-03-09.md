# Async determinism stack boundaries — 2026-03-09

This note exists to stop the archive from collapsing several nearby ideas into one vague “deterministic async crate”.

Rust now has enough substrate that the sharper work is often about **which layer is missing**, not whether determinism matters at all.

## Main judgment

There are at least five different layers here:

1. **shared-memory permutation testing**
2. **async/distributed deterministic simulation**
3. **domain hardship/profile suites**
4. **record/replay debugger workflows**
5. **game rollback / state-hashing determinism**

Future revisions should keep those layers explicit.

## 1. Shared-memory permutation testing
Examples: **Loom**, **Shuttle**.

These tools are about exploring or replaying schedules for concurrent Rust code.
They are especially strong for:

- synchronization primitives,
- lock-free or low-level concurrency,
- schedule-sensitive state transitions,
- and finding failures that only appear under rare interleavings.

They are **not** automatically the same thing as multi-host message/network simulation.

A proposal in this layer should talk about:

- schedules,
- thread/task interleavings,
- memory-model or synchronization semantics,
- replay tokens,
- and intrusive adapter boundaries.

## 2. Async/distributed deterministic simulation
Primary archive home: **P-0104 Deterministic Simulation Kit**.

This layer is about controlling the main ingredients of deterministic async/distributed testing:

- scheduling,
- time,
- randomness,
- fault injection,
- and external-I/O boundaries.

The missing value here is increasingly a **portable profile / receipt / transcript / bundle workflow above substrate** such as Tokio paused time, `tokio-rs/simulation`, Turmoil, or MadSim.

This layer should not quietly become:

- a full replay debugger for live production captures,
- a domain-specific hardship corpus,
- or a game-state rollback verifier.

## 3. Domain hardship/profile suites
Primary archive home: **P-0114 Distributed Systems Hardship Harness Kit** and protocol/domain kits that sit above it.

This layer is about curated scenarios and comparability contracts such as:

- client/server,
- gossip,
- queue/replication,
- protocol-specific packet/message corpora,
- and published “hardship matrices”.

A good hardship kit can depend on the simulation/bundle substrate from **P-0104**, but it should stay distinct from that substrate.

## 4. Record/replay debugger workflows
Primary archive home: **P-0073 Async Replay Debugger Kit**.

This layer is about captured executions and forensic investigation:

- record/replay,
- time-travel style debugging,
- cassettes for external I/O,
- redaction,
- and support bundles derived from actual program runs.

It may use some of the same artifact vocabulary as deterministic simulation, but its truth surface is different.
A replay debugger can begin from **observed execution** rather than from a synthetic scenario/fault plan.

## 5. Game rollback / state-hashing determinism
Primary archive home: **P-0066 Determinism Sim Kit**.

This layer is about:

- frame-by-frame state hashing,
- snapshot/restore,
- rollback/prediction correctness,
- desync repro artifacts,
- and defining what counts as state.

That is adjacent to deterministic simulation, but it is a different product surface and usually a different user set.

## Practical rule for future passes

Before adding or editing a proposal in this family, ask:

1. is the crate mainly about **schedule exploration**,
2. about **scenario-driven deterministic simulation**,
3. about a **domain hardship/profile corpus**,
4. about **observed-execution replay/debugging**,
5. or about **state hashing and rollback determinism**?

If the answer is “some of all of them”, the proposal is probably too blurry.

## Why this matters now

Current Rust substrate is no longer empty.
We now have enough real tools that the likely missing crates are often:

- **artifact contracts**,
- **backend receipts**,
- **comparability rules**,
- **scenario corpora**,
- or **support bundles**,

rather than another undifferentiated runtime experiment.
