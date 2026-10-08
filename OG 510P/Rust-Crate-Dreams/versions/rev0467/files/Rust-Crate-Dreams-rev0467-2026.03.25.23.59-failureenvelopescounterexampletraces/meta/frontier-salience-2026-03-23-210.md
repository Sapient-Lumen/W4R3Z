# Frontier salience 210 — concurrency contracts now need locality/affinity and driver-liveness honesty

## Main judgment

The next worthwhile deepening for **P-0538 Concurrency Contract Kit** is not another primitive, wrapper, or executor abstraction.
It is a receiver-facing contract for **where work is allowed to live** and **what must keep running for that work to make progress**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies async complexity as a major expert-facing pain and ties it to fragmentation and lock-in.
- Community discussion still names forward progress guarantees and reentrancy as missing documentation.
- Tokio now documents several different truths that are easy to over-flatten:
  - `spawn_local` keeps execution on the calling thread and panics outside a `LocalSet` or `LocalRuntime`;
  - a `LocalSet` only executes local tasks while it is being awaited or otherwise driven;
  - a current-thread runtime only executes tasks while some thread is calling `Runtime::block_on`;
  - `Handle::block_on` on a `current_thread` runtime does not drive I/O or timers;
  - `LocalRuntime` is thread-bound, unstable, and incompatible with `LocalSet`.
- Other executor ecosystems (`async-executor`, glommio, futures local executors) expose similar thread-local or explicitly-driven behavior.
- Executor abstraction crates already exist, which means the sharper missing lane is **support-contract truth**, not another abstraction facade.

## What the sharper crate should provide

A stronger **P-0538** should now publish:

- `mobility-affinity.report.json`
- `driver-liveness.report.json`
- bundle inventory that keeps locality truth distinct from fairness, cancellation, and recovery posture
- doctor rules that reject fake “local spawn support implies progress” stories

## Boundary reminder

This is still **not** a generic executor abstraction layer, not a scheduler benchmark suite, and not a new runtime-comparison blog in crate form.
It is the support-contract layer that lets another engineer review:

- whether work is `Send`-movable or thread-affine,
- whether a local context is required,
- whether a handle can spawn but not drive,
- whether explicit `run`, `tick`, `run_until`, or `Runtime::block_on` is required,
- and when manual review is still required.
