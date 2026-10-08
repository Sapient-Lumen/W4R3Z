# Design: DST Kit (`cargo dst`, `dst-pack/v0`)

## Goal
Create a Cargo-native deterministic simulation layer for Rust that makes concurrency and distributed-systems testing more reproducible, reviewable, and portable.

The key design decision is **composition over replacement**: Loom, Shuttle, Tokio paused-time tests, Turmoil, MadSim, and newer stacks like Moonpool already each cover part of the territory. The missing contribution is a shared contract and orchestration layer across them.

## References (signals)
- Rust project goals: async work is intended to unblock the next generation of async libraries.
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- State of Rust 2025 survey results: debugging remains a major productivity problem.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Loom: explores concurrent executions under the C11 memory model.
  https://docs.rs/loom/latest/loom/
- Shuttle: deterministic reproduction through controlled scheduling.
  https://docs.rs/shuttle/latest/shuttle/
- Tokio paused time: explicit async time control for tests.
  https://docs.rs/tokio/latest/tokio/time/fn.pause.html
- Turmoil: in-process deterministic distributed-system simulation with host/time/network control.
  https://tokio.rs/blog/2023-01-03-announcing-turmoil
- MadSim: tokio-like deterministic runtime with simulator-specific crate replacements.
  https://github.com/madsim-rs/madsim
- Moonpool: fault-injecting, multi-seed deterministic simulation with exploration support.
  https://docs.rs/moonpool_sim/latest/moonpool_sim/

## Core components

### 1) `dst-seed/v0`
Portable seed manifest:
- root seed
- derived RNG stream identifiers
- backend name + version
- schedule/time exploration knobs
- reproducibility guarantees (`exact`, `best-effort`, `backend-defined`)

### 2) `dst-config/v0`
Declares the test world:
- host/task topology
- workload parameters
- selected backend adapter
- time model (`real`, `paused`, `logical`)
- fault domains enabled

### 3) `dst-net-model/v0`
Optional but first-class:
- latency distributions
- reorder/loss rules
- connect failures
- partitions
- clock drift / deadline skew
- corruption / partial-write toggles where supported

### 4) `dst-history/v0`
Portable execution history:
- task/host lifecycle events
- scheduler decisions when available
- timer advances
- network send/deliver/drop events
- injected-fault events
- invariant-check checkpoints

This should be streamable and reference larger blobs externally when needed.

### 5) `dst-report/v0`
Outcome artifact:
- pass/fail/flaky/inconclusive
- failing seed(s)
- minimized reproduction pointer
- backend caveats
- checker results
- links to logs, traces, fuzz inputs, or replay attachments

### 6) `dst-policy/v0`
CI policy:
- seed counts / exploration budgets
- required backends
- required fault classes
- acceptable flake policy
- shrink budget and attachment policy

### 7) `dst-pack/v0`
Bundle format containing:
- config
- seed manifest(s)
- reports
- optional histories
- optional linked attachments (logs, traces, minimized input packs)

## `cargo dst` reference UX
- `cargo dst run`
- `cargo dst replay --seed ...`
- `cargo dst shrink`
- `cargo dst pack`
- `cargo dst gate`
- `cargo dst doctor`

`cargo dst` should validate schemas, normalize backend outputs, and make CI/reporting ergonomic. It should not require one blessed runtime.

## Adapter model
### Scale A: local concurrency
- **Loom adapter** for exhaustive/small-model concurrent tests.
- **Shuttle adapter** for randomized deterministic schedule exploration.

### Scale B: async timing
- **Tokio test adapter** for paused-time / logical-time-capable tests.

### Scale C: multi-host distributed simulation
- **Turmoil adapter** for host/time/network simulation.
- **MadSim adapter** for runtime-level deterministic simulation.
- **Moonpool adapter** for FDB-style failure exploration and multi-seed search.

Design rule: adapters declare their guarantees and limitations instead of pretending the same semantics exist everywhere.

## What the kit should provide to others
- **Library authors:** a standard way to publish schedule/time/network stress evidence.
- **Service teams:** repeatable seeded tests for timeout, retry, and partition behavior.
- **CI systems:** machine-readable reports instead of brittle log parsing.
- **Debugger/replay tools:** a structured starting point for attaching histories and repro bundles.
- **Fuzz/property-test authors:** a place to combine input-space exploration with execution-space exploration.

## Integration points
- **Replay Kit:** failing DST runs can emit replay attachments or reduced bug cassettes.
- **Async Lifecycle Kit:** lifecycle invariants (graceful shutdown, cancellation, ownership) become reusable DST checkers.
- **FuzzPack Kit:** fuzz-discovered inputs can be replayed across many seeds and fault models.
- **Cargo Report Kit:** reuse report-pack conventions for CI publication and cross-tool ingestion.

## Stack position
Treat DST as the **exploration lane** inside the broader [`design/async-reliability-stack.md`](./async-reliability-stack.md). DST should stay distinct from replay: it explores worlds and seeds, while Replay captures one concrete failure path.

## Hard problems (explicitly scoped)
1. **Semantic mismatch across backends**
   - v0 should expose backend capability descriptors instead of faking universal semantics.
2. **History size explosion**
   - support summaries by default and external blob references for large histories.
3. **Flakiness vs incompleteness**
   - distinguish backend limitations from user-code nondeterminism.
4. **Shrinking complexity**
   - allow seed replay first; make shrinkers pluggable.
5. **Adoption friction**
   - provide narrow starting points: one backend, one seed artifact, one report.

## Evaluation plan
Pilot on:
1. a concurrency-heavy library using Loom/Shuttle,
2. an async service using Tokio paused-time and fault injection,
3. a distributed system using Turmoil or MadSim,
4. one emerging “write once, simulate + deploy” example using Moonpool-style providers.

Success bar:
- seeded failures are easy to replay,
- CI can publish understandable artifacts,
- backends can coexist without semantic confusion,
- and teams get useful reliability evidence without committing to one monolithic simulator.
