# Gap: Deterministic Debugging for Async & Concurrency (record/replay + minimization)

## Summary
Async Rust and concurrent Rust are powerful, but hard bugs remain hard:
- production-only heisenbugs, races, and scheduler-dependent failures,
- flaky tests with low repro rates,
- “what happened?” debugging that needs task-level visibility and sometimes *reverse execution*.

Rust has multiple partial solutions:
- exhaustive/concolic-ish concurrency testing (Loom),
- randomized schedulers that scale better (Shuttle),
- runtime introspection (Tokio Console),
- Linux process record/replay debuggers (rr).

What’s missing is an **adoption-ready, end-to-end** workflow that:
1) records nondeterministic behavior at the right layer (tasks/actors/messages),
2) replays deterministically,
3) minimizes the schedule to a small repro,
4) emits portable artifacts so CI and humans can share a “bug cassette”.

## Ecosystem signals
- Loom: concurrency testing by permuting possible executions (exhaustive-ish).  
  https://crates.io/crates/loom
- Shuttle: randomized testing tradeoff (scales beyond Loom).  
  https://docs.rs/shuttle/latest/shuttle/
- Tokio Console: task-level diagnostics and profiling for async Rust.  
  https://crates.io/crates/tokio-console  
  https://github.com/tokio-rs/console
- rr: record and replay deterministic debugging of Linux user-space processes.  
  https://rr-project.org/  
  https://github.com/rr-debugger/rr
- Example of building an async debugger (“lildb”) shows the space is approachable, but not standardized.  
  https://cliffle.com/blog/lildb/
- Emerging crates on lib.rs/crates.io mention deterministic async record/replay and minimization as an explicit goal, indicating demand.  
  https://lib.rs/crates/frankenlab

## What “good” looks like
- A standard artifact for “concurrency cassettes” (events + schedule + metadata).
- Runtime-agnostic instrumentation via `tracing` (so it works on tokio, async-std, smol, custom runtimes).
- A minimizer that shrinks failing schedules (like delta-debugging for async).
- A clear boundary between:
  - unit tests (loom/shuttle style),
  - integration tests (cassette record/replay),
  - production incident capture (opt-in, privacy-aware).
