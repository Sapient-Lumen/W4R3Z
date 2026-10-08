# Design: Async Reliability Stack

## Goal
Treat **async lifecycle**, **failure replay**, and **deterministic simulation** as one ranked ecosystem contribution band without flattening them into one fake runtime, one fake test mode, or one fake “async health” score.

The stack should help Rust projects answer three different questions honestly:
1. **What did this async system promise about ownership and shutdown?**
2. **How can we capture and replay a specific failure or hang?**
3. **How do we explore schedules, time, and faults before the bug happens in production?**

Those are adjacent questions, but they are not the same question. The missing contribution is the shared execution discipline that lets these layers compose.

## Why this matters now
Official Rust signals increasingly say async reliability is still a live ecosystem seam, not solved background lore:
- the 2025H1 async flagship says async remains a multi-year parity effort and explicitly calls out cancellation sharp edges, runtime selection/interoperability, and reliability as part of the status quo;
- the 2026 flagship themes keep **Just Add Async** active, with milestones for return type notation, `async fn in dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting;
- the May 2025 goals update says the Async Book gained chapters on concurrency primitives, structured concurrency, and pinning;
- the Async Book’s current “state of async Rust” still says async involves compatibility constraints and a higher maintenance burden;
- Tokio’s official graceful-shutdown guidance now normalizes `CancellationToken` + `TaskTracker` patterns, and the current docs make important semantics explicit: `CancellationToken::child_token` gives one-way cancellation propagation while `TaskTracker::wait` only resolves once the tracker is closed and all tracked tasks have exited and finished destructor work;
- the 2025 State of Rust survey says resource usage and debugging remain notable productivity problems, which matters because async failures often degrade into hard-to-explain hangs, shutdown bugs, and timing-sensitive misbehavior.

## References (signals)
- Async parity flagship:
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- 2026 flagship themes (`Just Add Async`):
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- May 2025 goals update / Async Book progress:
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- Async Book introduction and current state:
  https://rust-lang.github.io/async-book/
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- Tokio graceful shutdown guidance:
  https://tokio.rs/tokio/topics/shutdown
- Tokio cancellation hierarchy primitive:
  https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- Tokio task tracking primitive:
  https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- Loom:
  https://docs.rs/loom/latest/loom/
- Shuttle:
  https://docs.rs/shuttle/latest/shuttle/
- Turmoil:
  https://docs.rs/turmoil/latest/turmoil/
- MadSim:
  https://docs.rs/madsim/latest/madsim/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Stack components and ownership

### 1) Async Lifecycle Kit owns runtime-shaped lifecycle truth
Source: [`design/async-lifecycle-kit.md`](./async-lifecycle-kit.md)

It should keep owning:
- task ownership / scope topology,
- cancellation propagation,
- shutdown budgets and policies,
- runtime capability profiles,
- lifecycle reports and minimal async repro summaries.

Design rule: this layer defines **what the async program promised to do while running and shutting down**.
Its runtime-capability artifacts should import lower-level lane truth from Async Commons instead of re-defining spawn / local / time / I/O / environment portability themselves.

### 2) Replay Kit owns failure capture and re-execution truth
Source: [`design/replay-kit.md`](./replay-kit.md)

It should keep owning:
- captured bug cassettes,
- replayable schedule/event traces when available,
- minimized reproductions,
- exact vs best-effort replay posture,
- replay reports.

Design rule: this layer defines **how one observed failure can be replayed, minimized, or shared**.

### 3) DST Kit owns exploration truth
Source: [`design/dst-kit.md`](./dst-kit.md)

It should keep owning:
- seed manifests,
- simulation world/config,
- scheduler / time / network / fault-model declarations,
- histories,
- CI-facing outcome reports.

Design rule: this layer defines **how we systematically search schedules, timing, and failure worlds**.

Important nuance: the ecosystem already spans materially different exploration families — Loom-style execution permutation, Shuttle-style randomized exploration, and Turmoil/MadSim-style deterministic distributed simulation. The stack should preserve those distinctions rather than flatten them into one fake deterministic-testing story.

### 4) Time Surface Kit remains an attachment lane, not the owner of async reliability
Source: [`design/time-surface-kit.md`](./time-surface-kit.md)

It should stay responsible for clock/fake-time/runtime-time truth where relevant, but it should attach to lifecycle, replay, or DST artifacts instead of becoming a replacement for them.

### 5) Test Run Evidence Kit remains the shared run subject when tests are the host lane
Source: [`design/test-run-evidence-kit.md`](./test-run-evidence-kit.md)

When an async reliability check is exercised through a test runner, `test-pack/v0` should keep owning test inventory/run semantics. Async lifecycle, replay, and DST artifacts should attach to that run subject instead of redefining it.

## Shared design rules
1. **Lifecycle, replay, and simulation must remain distinct truths.**
   A graceful shutdown report is not a replay cassette; a replay cassette is not a simulation campaign.
2. **Runtime truth, lane truth, and cancellation topology must stay explicit.**
   Tokio-first is acceptable. Fake runtime neutrality is not. Child-token trees, flat broadcast cancellation, spawn/local splits, timer assumptions, and environment posture are different facts.
3. **Determinism must be graded honestly.**
   Use labels like `exact`, `best-effort`, `backend-defined`, `seeded-exploration`, or `not-replayable` instead of vague reproducibility claims.
4. **Attachments should widen capability, not erase origin.**
   Time-control data, tracing links, debugger hints, and test-run ids should attach without redefining the primary async subject.
5. **Failure exploration and failure replay are complementary.**
   DST finds bad worlds; Replay makes one concrete failure portable.
6. **The stack should improve teachability and reviewability.**
   It should give maintainers something better than log scraping, screenshots, and “works on my machine” shutdown folklore.

## Reference artifact flow
A realistic composition path should look like this:
- `runtime-capability-profile/v0`
- `shutdown-policy/v0`
- `async-lifecycle-report/v0`
- optional `async-repro/v0`
- optional `replay-pack/v0` / `replay-report/v0`
- optional `dst-config/v0` / `dst-seed/v0` / `dst-report/v0` / `dst-history/v0`
- optional attachment refs into `test-pack/v0`, `time-surface-report/v0`, tracing bundles, debugger artifacts, or incident reports

Design rule: **earlier artifacts declare intended behavior; later artifacts capture observed failure and exploration context.**

## What a worthy contribution would look like
A real contribution here should not be “one async runtime helper crate” or “one magical deterministic scheduler”. It should:
- give Tokio-first projects a portable lifecycle evidence lane immediately;
- hand failures off cleanly to replay and test-run consumers;
- let deterministic-simulation tools share seeds/histories/reports without forcing one backend to win;
- preserve exact-vs-best-effort claims;
- make debugger, incident, and CI consumers better without making them the source of truth.

## Non-goals
- Replacing Tokio, async-std, Smol, Shuttle, Loom, Turmoil, MadSim, or Moonpool.
- Claiming all async bugs can be deterministically replayed.
- Flattening schedule exploration, graceful shutdown, and network-fault simulation into one schema.
- Turning observability tooling into the source of semantic truth.
- Waiting for all of `Just Add Async` to finish before improving present-day reliability workflows.

## Execution order
Treat [`design/async-reliability-pilot-program.md`](./async-reliability-pilot-program.md) as the ranked rollout plan.

The next credible move is not “invent an async super-framework”. It is:
1. lifecycle truth first,
2. replay handoff second,
3. deterministic simulation attachment third,
4. runtime-portable library posture fourth,
5. debugger/incident/support consumers after that.
