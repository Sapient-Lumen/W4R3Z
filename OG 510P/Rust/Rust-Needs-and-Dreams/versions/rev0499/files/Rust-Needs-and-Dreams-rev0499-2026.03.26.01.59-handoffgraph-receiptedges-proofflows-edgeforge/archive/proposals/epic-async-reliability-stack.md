# Epic Proposal: Async Reliability Stack (`cargo asyncdoctor` + `async-reliability-pack/v0`)

## One-sentence pitch
Make async failure review boring by standardizing a portable boundary that keeps **lifecycle policy, replay evidence, and deterministic exploration** distinct instead of forcing every service, library, and test stack to reconstruct async truth from runtime glue, simulator-specific logs, and issue folklore.

## Deliverables
- reference command:
  - `cargo asyncdoctor`
- schemas:
  - `async-reliability-brief/v0`
  - `async-reliability-pack/v0`
  - `async-reliability-diff/v0`
  - `async-reliability-handoff/v0`
- adapters/importers for:
  - `runtime-capability-profile/v0`
  - `shutdown-policy/v0`
  - `async-lifecycle-report/v0`
  - `async-repro/v0`
  - `replay-pack/v0`
  - `replay-report/v0`
  - `dst-config/v0`
  - `dst-seed/v0`
  - `dst-report/v0`
  - optional `dst-history/v0`
  - optional `test-pack/v0`, time-control, tracing, debugger, and incident attachments
- docs:
  - Tokio shutdown / cancellation-tree guide
  - exact-vs-best-effort replay guide
  - local-concurrency vs distributed-simulation comparability guide
  - runtime-portability / approximation guide
  - debugger / incident / support consumer-lossiness guide

## Why now (signals)
- The 2025H1 async flagship says async Rust remains a multi-year parity effort and explicitly calls out runtime choice, interoperability, cancellation sharp edges, and reliability as part of the current status quo.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- Rust’s 2026 flagships keep **Just Add Async** active, with milestones for return type notation, `async fn in dyn trait`, immobile types / guaranteed destructors, and ergonomic ref-counting. That is a strong signal that async ergonomics and semantics are still live ecosystem work, not finished plumbing.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The May 2025 project-goals update says the official Async Book recently added chapters on concurrency primitives, structured concurrency, and pinning. That strengthens the case for structured lifecycle vocabulary instead of log-driven folklore.
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- The current Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than synchronous Rust. That strongly argues against flattening runtime identity into a fake universal async story.
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- Tokio’s shutdown guidance explicitly teaches `CancellationToken` and `TaskTracker`; `CancellationToken::child_token` documents one-way cancellation propagation for child tokens, and `TaskTracker::wait` guarantees both that tracked tasks have exited and that their future destructors have finished once the tracker is closed and empty. That is enough concrete substrate to justify a portable lifecycle-evidence lane above ad hoc shutdown code.
  https://tokio.rs/tokio/topics/shutdown
  https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
  https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- The ecosystem already has serious but non-equivalent exploration tools: Loom permutes valid concurrent executions, Shuttle uses randomized testing rather than exhaustive exploration, Turmoil provides deterministic distributed execution with seeded network hardship, and MadSim is a deterministic simulator for distributed systems. That is exactly the kind of point-tool diversity that calls for a shared contract layer rather than another would-be winner.
  https://docs.rs/loom/latest/loom/
  https://docs.rs/shuttle/latest/shuttle/
  https://docs.rs/turmoil/latest/turmoil/
  https://docs.rs/madsim/latest/madsim/
- The 2025 State of Rust survey still lists resource usage and debugging among the main productivity problems, which matters because async failures often show up as costly hangs, shutdown leaks, and timing-sensitive bugs that are hard to explain after the fact.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Non-goals
- replacing Tokio, async-std, Smol, Loom, Shuttle, Turmoil, MadSim, Moonpool, or future runtime/simulation tools;
- inventing one universal runtime facade or one universal deterministic scheduler;
- claiming every async failure is exactly replayable;
- collapsing tracing, logs, test output, debugger state, and simulator histories into one mega-format;
- turning observability or incident tooling into the canonical source of async semantics.

## Strategic value
This deserves promotion because it gives the archive a missing **service-reliability composition point**.
With it:
- maintainers can review what shutdown and cancellation structure the program actually promised;
- failures can be handed off from lifecycle reports into replay bundles without pretending replay is always exact;
- simulation tools can attach seeds, worlds, and histories without being forced into one semantic model;
- runtime-portable libraries can state which lifecycle guarantees are required versus approximated;
- debugger, incident, support, and testing consumers can import async-reliability evidence without silently redefining it.

The prize is not another runtime helper.
The prize is a durable record of **what lifecycle policy was declared, what failure was observed, what replay was possible, what exploration semantics were exercised, and what downstream consumers may honestly conclude**.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. make `async-reliability-brief/v0` the canonical declaration of subject, runtime/backend family, and intended consumers;
2. import `runtime-capability-profile/v0`, `shutdown-policy/v0`, and `async-lifecycle-report/v0` as the canonical lifecycle lane;
3. import `async-repro/v0`, `replay-pack/v0`, and `replay-report/v0` as the canonical failure-capture lane;
4. import `dst-config/v0`, `dst-seed/v0`, `dst-report/v0`, and optional `dst-history/v0` as the canonical exploration lane;
5. attach `test-pack/v0`, time-control, tracing, debugger, and incident artifacts as imports instead of redefining async semantics through them;
6. emit `async-reliability-pack/v0`, `async-reliability-diff/v0`, and `async-reliability-handoff/v0` so service, debugging, support, and testing stacks can consume async reliability without re-scraping local tooling.

## Critical design bet
The critical bet is that **async reliability becomes useful before the ecosystem converges on one runtime, one replay engine, or one simulation backend**.
That means:
- Tokio-first lifecycle evidence is already enough to anchor the first portable packs;
- cancellation-tree and drain semantics are already concrete enough to export;
- best-effort replay is already worth preserving as best-effort instead of waiting for universal exact replay;
- simulator diversity is a reason to preserve capability matrices, not a reason to postpone all composition;
- downstream consumers can already benefit from bounded handoffs without waiting for a one-true async platform.

Without that boundary, the stack either stays too weak to matter or bloats into a fake universal runtime/testing framework.

## Milestones
1. **v0 lifecycle lane**
   - `async-reliability-brief/v0`
   - imports from lifecycle artifacts
   - Tokio shutdown / cancellation-tree guide
2. **v0.2 replay handoff lane**
   - imports from `async-repro/v0`, `replay-pack/v0`, `replay-report/v0`
   - explicit exact / best-effort markers
3. **v0.3 simulation attachment lane**
   - imports from DST artifacts
   - local-concurrency vs distributed/fault comparability notes
4. **v0.4 portability / approximation lane**
   - runtime-capability profiles across more than one adapter/backend
   - explicit unsupported or approximated semantics
5. **v1 consumer handoffs**
   - `async-reliability-pack/v0`, `async-reliability-diff/v0`, `async-reliability-handoff/v0`
   - debugger / incident / support / testing / service-product consumers

## Execution order
Use [`design/async-reliability-pilot-program.md`](../design/async-reliability-pilot-program.md) as the stack-level rollout:
1. Tokio shutdown truth,
2. failure handoff to replay,
3. deterministic simulation attachment,
4. runtime-portable library posture,
5. debugger / incident / support consumers.

Use [`design/async-lifecycle-kit.md`](../design/async-lifecycle-kit.md), [`design/replay-kit.md`](../design/replay-kit.md), and [`design/dst-kit.md`](../design/dst-kit.md) as the leaf-level execution guides beneath it.

## Success metrics
- reviewers can distinguish lifecycle policy, observed failures, replay posture, and exploration semantics without reading bespoke runtime glue;
- cancellation hierarchy and drain guarantees remain reviewable instead of hidden inside helper crates;
- at least two distinct exploration/replay tools can attach to the same async subject without pretending they are equivalent;
- debugger, incident, or support consumers can import the same async-reliability pack without bespoke scraping;
- the ecosystem gets one explainable async-reliability seam instead of scattered shutdown code, flaky test notes, simulator seeds, and issue folklore.
