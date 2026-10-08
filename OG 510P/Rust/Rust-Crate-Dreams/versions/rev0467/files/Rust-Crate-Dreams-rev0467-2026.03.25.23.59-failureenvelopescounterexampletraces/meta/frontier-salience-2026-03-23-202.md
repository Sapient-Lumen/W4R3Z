# Frontier salience refresh — 2026-03-23 (202)

## Why this pass went broad again

The archive had accumulated many good narrow deepening passes.
That was valuable.
But after the latest rustdoc-json refresh, it still needed another whole-frontier question:

> across toolchain, docs, async, services, GUI, embedded, safety, debugging, and ecosystem-navigation work, what looks most missing *to other people* rather than merely interesting to crate authors?

## Main ranked takeaway

The strongest new lane added by this pass is **P-0538 Concurrency Contract Kit**.

Not because Rust lacks mutexes, channels, runtimes, or debuggers.
But because Rust still lacks one receiver-facing crate that can say, in a portable and reviewable way:

- whether a surface is re-entrant,
- what progress/fairness class it promises,
- what cancellation does to waiters,
- which execution contexts are legal,
- and where those claims stop.

## Current ranked frontier

### Highest

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**

### Very high

5. **P-0538 Concurrency Contract Kit**
6. **P-0453 Safety Contract Consumer Kit**
7. **P-0011 Crate Health Contract Kit**
8. **P-0121 FFI Boundary Conformance Kit**
9. **P-0532 Async Runtime Assurance Profile Kit**

### High

10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0469 Cargo Rebuild Explanation Kit**
12. **P-0035 cargo-build-insights**
13. **P-0490 Cargo Lock Contention Witness Kit**
14. **P-0486 Debuggability Support Contract Kit**
15. **P-0433 MC/DC Coverage Workbench Kit**

## Why P-0538 now belongs near the top

### 5. P-0538 Concurrency Contract Kit
Why it belongs:
- official March 2026 challenge material still treats async complexity as a top expert-facing problem;
- community demand explicitly names forward-progress guarantees, reentrancy, cancellation safety, and observability gaps;
- current crate/runtime docs expose important guarantees, but in fragmented, primitive-specific language that is hard to compare;
- and this lane can help many adjacent sectors at once: services, GUI, libraries, runtime adapters, data systems, and support tooling.

## What this pass did not decide

This pass did **not** decide that channel, resource, or runtime work is unimportant.
It decided that the archive had room for one additional contract lane above them.

That lane should stay narrow enough to avoid becoming:
- a new lock implementation,
- a new runtime abstraction,
- a generic deadlock detector,
- or a generic async tutorial.

## Freshness anchors

- Rust challenges / March 2026 — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/11/2025-Rust-Debugging-Survey/
- Rust forum discussion on ecosystem gaps — https://users.rust-lang.org/t/what-is-missing-lacking-in-the-rust-ecosystem/117157?page=3
- Tokio `Mutex` docs — https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
- Tokio `RwLock` docs — https://docs.rs/tokio/latest/tokio/sync/struct.RwLock.html
- Tokio `Semaphore` docs — https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
- Tokio `select!` docs — https://docs.rs/tokio/latest/tokio/macro.select.html
- `parking_lot` docs — https://docs.rs/parking_lot/latest/parking_lot/
- `std::sync::Mutex` docs — https://doc.rust-lang.org/std/sync/struct.Mutex.html
