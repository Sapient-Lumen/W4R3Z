# Gap: deterministic simulation testing is still fragmented across concurrency scales

## Summary
Rust has strong building blocks for concurrency and distributed-systems testing, but they still live at different scales with different ergonomics:
- **Loom** exhaustively explores concurrent executions for small concurrent components.
  https://docs.rs/loom/latest/loom/
- **Shuttle** randomizes schedules and reproduces failures deterministically for threaded/concurrent Rust tests.
  https://docs.rs/shuttle/latest/shuttle/
- **Tokio** offers paused time and auto-advance controls that help make async tests more deterministic.
  https://docs.rs/tokio/latest/tokio/time/fn.pause.html
- **Turmoil** simulates hosts, time, and the network in-process for distributed systems.
  https://tokio.rs/blog/2023-01-03-announcing-turmoil
- **MadSim** provides a tokio-like deterministic simulator, but often requires swapping in simulator-specific crates and patches.
  https://github.com/madsim-rs/madsim
- **Moonpool** is pushing an FDB-style simulation stack with multi-seed exploration and explicit fault injection.
  https://docs.rs/moonpool_sim/latest/moonpool_sim/

That is a promising toolbox, but not yet a **shared Cargo-native workflow** for seeds, fault models, histories, minimization, and CI artifacts.

## Why now
- The Rust project is still investing in async as a flagship ergonomics area and explicitly says current work is meant to unblock the **next generation of async libraries**.
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- The newest State of Rust survey still names **debugging** and **resource usage** among the main productivity problems. Reproducible failure-finding and replayable test evidence are one practical way to improve both.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The ecosystem now has enough serious partial solutions that the missing contribution is better framed as **interoperability and artifacts**, not “invent yet another simulator”.

## Concrete missing pieces
1. **Versioned seed and fault-model artifacts**
   - seed derivation
   - scheduler knobs
   - paused/logical time settings
   - network hardship and partition models
   - entropy / clock / corruption controls
2. **Portable execution histories**
   - task and host events
   - message deliveries and drops
   - timer advances
   - failure injection points
3. **A standard failure/report layer**
   - invariant/checker results
   - minimized reproduction metadata
   - machine-readable links to attached traces/corpora/logs
4. **Cargo-native orchestration**
   - run many seeds
   - reproduce one seed exactly
   - shrink failing runs
   - publish CI-friendly artifacts
5. **Backend interop by scale**
   - local concurrency exploration (`loom`, `shuttle`)
   - async time control (`tokio::time`)
   - in-process multi-host simulation (`turmoil`, `madsim`, `moonpool`)

## Desired properties
- Compose existing backends instead of replacing them.
- Be explicit about **what kind of nondeterminism** is being controlled.
- Make “same seed, same failure” a first-class promise whenever a backend can support it.
- Distinguish **local concurrency**, **async timing**, and **distributed/network** simulation instead of flattening them into one vague story.
- Emit artifacts that other kits can consume.

## Distinction from nearby archive entries
- **Replay Kit** is about post-failure bug cassettes and debugging workflows; this kit is about **finding and systematically exploring failures before production**.
- **Async Lifecycle Kit** is about shutdown, ownership, cancellation, and portability; this kit is about **test-time schedule/time/network exploration**.
- **FuzzPack Kit** standardizes fuzz corpus/crash packs; this kit should integrate with fuzz/property inputs, but focuses on **nondeterministic execution control** rather than input mutation alone.
