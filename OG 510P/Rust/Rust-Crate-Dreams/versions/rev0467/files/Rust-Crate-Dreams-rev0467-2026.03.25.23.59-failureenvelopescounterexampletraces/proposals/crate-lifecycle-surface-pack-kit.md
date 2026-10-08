---
id: P-0520
title: Crate Lifecycle Surface Pack Kit — background-work maps, shutdown-barrier receipts, cancel-safety surfaces, and drain diffs for library authors
status: idea
domains: [crates, async, dx, shutdown, cancellation, lifecycle, structured-concurrency, supportiveness]
last_reviewed: 2026-03-20
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://tokio.rs/tokio/topics/shutdown
  - https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
  - https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
  - https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
  - https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
  - https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.Runtime.html
  - https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
  - https://docs.rs/hyper-util/latest/hyper_util/server/graceful/struct.GracefulShutdown.html
  - https://docs.rs/tokio/latest/tokio/macro.select.html
  - https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
  - https://docs.rs/tokio-util/latest/tokio_util/task/index.html
  - https://docs.rs/async-shutdown/latest/async_shutdown/
  - https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
  - https://docs.rs/task_scope/latest/task_scope/
  - https://docs.rs/crate/moro/0.4.0
  - https://github.com/tokio-rs/tokio/discussions/7213
  - https://github.com/tokio-rs/axum/issues/3003
  - https://github.com/tokio-rs/axum/issues/2673
  - https://github.com/hyperium/hyper/issues/2787
  - https://github.com/tokio-rs/axum/blob/main/axum/CHANGELOG.md
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
---

# Problem

The archive now has much better receiver-facing lanes for:

- choosing crates,
- understanding support claims,
- fitting interop profiles,
- getting compile-time guidance,
- handling runtime failure handoff,
- upgrading,
- leaving a crate,
- choosing setup scenarios,
- reasoning about performance posture,
- understanding observability surfaces,
- and reviewing authority / determinism posture.

It still lacks a good answer to a different but very common downstream question:

> “If I use this crate in a real async system, what background work does it start, how do I shut it down, what does shutdown completion actually cover, what is safe to cancel or abort, and what must I flush, drain, join, or await before I drop it?”

That gap matters because current Rust substrate already makes lifecycle behavior important but fragmented.

The December 2025 Rust vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 State of Rust survey says online docs remain the preferred canonical reference, followed by studying code itself.
That makes lifecycle truth a crate-support surface, not merely runtime trivia.

Tokio’s own graceful-shutdown guide says asynchronous applications usually need three things:

1. figure out when to shut down,
2. tell every part of the program to shut down,
3. wait for other parts of the program to shut down.

Tokio and tokio-util now provide meaningful substrate for those tasks:

- `CancellationToken` for signaling cancellation,
- `TaskTracker` for waiting until tracked tasks actually exit,
- `JoinHandle` and `AbortHandle` for task lifecycle control,
- `AbortOnDropHandle` for drop-aborts-task behavior,
- `JoinSet` for tracked task groups with distinct abort/wait/detach behavior,
- `select!` docs that explain cancellation safety,
- and `AsyncWriteExt` docs that distinguish cancel-safe calls like `write` from non-cancel-safe calls like `write_all`, while separately documenting `flush` and `shutdown` obligations.

That substrate is now explicit enough to expose a sharper missing seam:

- `TaskTracker::wait()` completes only when the tracker is **both closed and empty**, but dropping a `TaskTracker` does **not** abort tasks.
- Dropping a `JoinHandle` **detaches** the associated task.
- Dropping a `JoinSet` aborts tracked tasks, `shutdown()` aborts and then waits, while `detach_all()` keeps those tasks running in the background.
- Tokio maintainer guidance now spells out that putting a `JoinHandle` under `timeout` only stops waiting; it does **not** cancel the task unless the caller also aborts it.
- Current axum issue traffic shows that a WebSocket upgrade task can sit outside a server graceful-shutdown future, while a pending SSE upstream stream can keep that graceful-shutdown barrier blocked indefinitely.

But today that substrate still does **not** give maintainers one boring workflow for questions like:

- which public operations start background work,
- whether dropping a handle detaches, aborts, or blocks until cleanup,
- what event actually counts as **shutdown completion**,
- which tasks or upgraded/protocol components are **inside** that barrier versus **outside** it,
- whether a method is cancel-safe, partially-progressing, retry-safe, or manual-review-only,
- what shutdown sequence is required to avoid data loss or leaked work,
- whether `spawn_blocking`, upgraded connections, or external dependencies escape normal abort expectations,
- which named shutdown phase a stop path actually reached before timeout or escalation,
- whether a timeout stopped work, stopped waiting, or merely abandoned the runtime wait barrier,
- which obligations are mandatory (`shutdown`, `flush`, `join`, `close`) versus best-effort,
- and how that lifecycle surface changed across releases.

The worthy crate is therefore **not** another runtime, **not** another structured-concurrency experiment, and **not** another graceful-shutdown helper by itself.
It is a **Crate Lifecycle Surface Pack Kit**: a crate that helps maintainers author, test, diff, and export the receiver-facing lifecycle contract their crate gives other people.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What background work does this crate start or expect?**
2. **What are the supported shutdown paths?**
3. **What event actually counts as the shutdown barrier, and what work is outside it?**
4. **Which operations are cancel-safe, partially-progressing, retry-safe, race-sensitive, or abort-hostile?**
5. **What must a downstream user flush, drain, close, join, or await before dropping?**
6. **How did that lifecycle surface change across releases?**
7. **Which shutdown phase was actually reached before the budget expired, and what still survives after timeout returns?**

That is more valuable than another ad hoc shutdown abstraction.

# What it provides

- `lifecycle-pack.toml` — versioned declaration of components, background-work classes, shutdown phases, and public lifecycle promises.
- `background-work.receipt.json` — observed receipt for spawned tasks, worker threads, subscriptions, timers, or queues started by a scenario.
- `cancellation-surface.report.json` — method-by-method classification such as `cancel_safe`, `partial_progress_preserved`, `drop_detaches`, `drop_aborts`, `abort_unsupported`, `retry_safe`, or `manual_review_required`.
- `shutdown-obligation.report.json` — explicit shutdown / close / flush / join / drain obligations and whether each is mandatory, advisory, or automatic.
- `shutdown-barrier.report.json` — explicit classification of what completion means, such as `signal_sent_only`, `listener_stopped`, `tracked_tasks_closed_and_empty`, `protocol_drains_finished`, or `manual_review_required`.
- `escape-path.receipt.json` — records detached tasks, upgraded connections, pending stream dependencies, blocking workers, or external workers that are outside or only weakly connected to the main barrier.
- `drain-recipe.manifest.json` — the smallest supported sequence for clean stop, timeout stop, and hard abort.
- `shutdown-phase.report.json` — records the farthest named shutdown phase actually reached for a scenario, such as `signal_sent`, `accepting_stopped`, `tracked_tasks_drained`, `protocol_close_attempted`, `protocol_drains_finished`, `runtime_wait_abandoned`, or `manual_review_required`.
- `timeout-aftermath.receipt.json` — records what remains true after a timeout or dropped wait path returns, such as `wait_stopped_only`, `task_still_running`, `blocking_thread_survives`, `resource_handles_invalidated`, `manual_abort_still_required`, or `manual_review_required`.
- `race-retry-safety.report.json` — records operations that are idempotent, replay-safe, at-most-once, close-racy, or require external fencing.
- `lifecycle-check.report.json` — verifies fixtures still match lifecycle promises and cleanup obligations.
- `lifecycle-diff.report.json` — compares two releases and classifies `background_work_added`, `cancel_semantics_changed`, `shutdown_obligation_changed`, `abort_behavior_changed`, `drain_recipe_changed`, and `manual_review_required`.
- `lifecycle.summary.md` — short human-facing explanation of what a downstream integrator must do to use and stop the crate safely.
- `cargo lifecycle-pack check` — run lifecycle fixtures and verify receipts against the pack.
- `cargo lifecycle-pack diff <old> <new>` — show how lifecycle promises changed.
- `cargo lifecycle-pack summary` — render a concise operator/integrator summary.

# What the crate should provide other people

1. **A receiver-facing lifecycle contract** above scattered docs, examples, and issue-thread folklore.
2. **A background-work map** so integrators know what may still be alive after “I dropped the client.”
3. **A shutdown-barrier map** so users know whether completion means a signal was sent, a listener stopped, a tracked set drained, or user-visible protocol work actually finished.
4. **Escape-path receipts** so detached tasks, upgraded connections, blocking workers, and pending upstream dependencies do not disappear from the stop story.
5. **A cancel-safety matrix** that makes partial progress and restart semantics reviewable instead of implicit.
6. **A shutdown-obligations bundle** that says when users must `flush`, `shutdown`, `close`, `join`, or `drain` to avoid loss.
7. **A shutdown-phase ladder** so “how far did stop actually get?” stays reviewable.
8. **A timeout-aftermath receipt** so “timeout returned” does not masquerade as quiescence.
9. **A drain recipe** for common stop paths: graceful, timed, and hard-abort.
10. **A diffable lifecycle surface** so releases can be reviewed for hidden detach/abort/cleanup changes.
11. **Importable lifecycle vocabulary** for docs portals, integration guides, support bots, and pathfinder-style crate selection tools.

# Persona / who it’s for

- async library authors with background tasks, pools, or subscriptions
- client / SDK maintainers whose users need deterministic startup and shutdown behavior
- stream / protocol crate maintainers with close, flush, half-close, or drain semantics
- runtime-agnostic library maintainers who need to document cancellation truth without writing a runtime
- app teams maintaining foundational internal crates with support obligations

# Users & user stories

- **SDK maintainer**: “Prove which handles detach on drop, which ones need explicit `close`, and which background tasks are still alive until `shutdown()` finishes.”
- **Streaming crate maintainer**: “Tell downstream users whether `write_all` can partially progress under cancellation and what recovery sequence is supported.”
- **Service integrator**: “Compare crate versions and see whether graceful shutdown got stricter, looser, more abort-friendly, or merely changed what the shutdown barrier covers.”
- **Support engineer**: “When someone says a task leaked after shutdown, tell me whether the crate promised join-on-drop, detach-on-drop, barrier completion for tracked work only, or manual drain outside the barrier.”
- **Docs/tool author**: “Import machine-readable lifecycle recipes, shutdown-barrier notes, and cancellation notes instead of scraping examples and FAQ prose.”

# Prior art (and why it’s insufficient)

- Tokio’s graceful-shutdown guide explains the general pattern, but it is guidance for building an app, not a portable per-crate contract.
- `CancellationToken` gives a standard cancellation signal.
- `TaskTracker` helps wait for tracked tasks to exit and explicitly distinguishes empty-from-closed state.
- `JoinHandle` documents that dropping the handle detaches the task and loses its output.
- `AbortHandle` documents that abort permission is separate from join permission and that `spawn_blocking` tasks cannot be aborted once running.
- `AbortOnDropHandle` gives one useful drop-aborts-task behavior.
- Tokio’s `select!` docs define cancellation safety and explain why looped selection can lose progress when a future is not cancel-safe.
- `AsyncWriteExt` documents materially different lifecycle behavior for `write`, `write_all`, `flush`, and `shutdown`.
- `async_shutdown` provides runtime-agnostic shutdown building blocks.
- `tokio-graceful-shutdown` provides subsystem-oriented graceful-shutdown orchestration for Tokio services.
- `task_scope` and `moro` show continuing interest in structured concurrency and cancellation propagation.

What remains missing is a **crate-authored lifecycle contract workflow** above those pieces:

- author one lifecycle support contract,
- verify it against fixtures,
- classify cancel / abort / drop / drain semantics,
- classify shutdown-barrier and escape-path truth,
- export stable receipts,
- and diff the lifecycle surface over time.

# Design goals

1. **Receiver-facing lifecycle truth first** — optimize for the integrator or maintainer using the crate, not only for the crate’s internal task orchestration.
2. **Background-work honesty** — make hidden workers, spawned tasks, timers, retries, and subscriptions explicit.
3. **Barrier-scope honesty** — do not let “graceful shutdown completed” outgrow the exact work it covers.
4. **Cancel/abort/drop separation** — do not blur `drop`, cooperative cancellation, and forced abort into one fake stop story.
5. **Obligation clarity** — distinguish advisory cleanup from mandatory `flush`/`shutdown`/`join`/`drain` steps.
6. **Partial-progress honesty** — classify methods whose cancellation may preserve progress, lose progress, or require manual review.
7. **Runtime-adapter friendliness** — work with Tokio first but avoid pretending the vocabulary is Tokio-only.
8. **Timeout honesty** — keep “stop waiting” separate from “stop work” and from “program is quiescent.”
9. **Narrow enough to ship** — start with pack/check/diff/report, not a whole supervisor framework.

# MVP surface

- Minimal types: `LifecyclePack`, `ComponentLifecycle`, `BackgroundWorkReceipt`, `CancellationSurfaceReport`, `ShutdownObligationReport`, `ShutdownBarrierReport`, `EscapePathReceipt`, `ShutdownPhaseReport`, `TimeoutAftermathReceipt`, `DrainRecipeManifest`, `RaceRetrySafetyReport`, `LifecycleCheckReport`, `LifecycleDiffReport`, `LifecycleSummary`
- Minimal functions:
  - `load_lifecycle_pack()`
  - `capture_background_work_receipt()`
  - `capture_shutdown_barrier_report()`
  - `capture_escape_path_receipt()`
  - `capture_shutdown_phase_report()`
  - `capture_timeout_aftermath_receipt()`
  - `check_cancellation_surface()`
  - `check_shutdown_obligations()`
  - `diff_lifecycle_surface()`
  - `render_lifecycle_summary()`
- Minimal CLI:
  - `cargo lifecycle-pack check`
  - `cargo lifecycle-pack diff`
  - `cargo lifecycle-pack summary`

# Example artifact vocabulary

## `lifecycle-pack.toml`

```toml
schema_version = "0.1"
crate = "example-stream-client"

[[components]]
name = "client_handle"
kind = "handle"
background_work = ["connection_reader", "retry_timer"]
drop_semantics = "detaches"
shutdown_recipe = "graceful_close"

[[operations]]
name = "write_all_frame"
kind = "write"
cancel = "partial_progress_possible"
retry = "manual_review_required"
requires = ["connected"]

[[operations]]
name = "close"
kind = "shutdown"
cancel = "manual_review_required"
retry = "idempotent"
```

## `cancellation-surface.report.json`

```json
{
  "crate": "example-stream-client",
  "component": "client_handle",
  "operations": [
    {
      "name": "recv",
      "cancel": "cancel_safe",
      "retry": "safe_to_recreate"
    },
    {
      "name": "write_all_frame",
      "cancel": "partial_progress_possible",
      "retry": "manual_review_required"
    }
  ]
}
```

# First proving scenarios

1. **Connection-pool client crate** — background workers, drop-vs-close semantics, in-flight request cancellation, and shutdown drain ordering.
2. **Streaming writer / framed transport crate** — `write` vs `write_all`, flush/shutdown obligations, partial-progress semantics, and half-close behavior.
3. **Axum-style upgraded WebSocket path** — server graceful-shutdown barrier versus upgraded-task escape.
4. **Axum-style SSE path** — pending upstream dependency blocking graceful-shutdown completion.
5. **Watcher / subscription crate** — spawned tasks, channel/drain semantics, cancellation tokens, and “listener dropped but worker still alive” truth.
6. **Embedded async driver crate** — interrupt/task lifecycle, retry loops, timeout cancellation, and “must quiesce hardware before drop” obligations.

# Adoption path

## Phase 1 — vocabulary + manual packs
- Publish schema crate plus summary renderer.
- Support manually authored `lifecycle-pack.toml` and fixture-checked reports.
- Focus on Tokio-heavy proving grounds first because the substrate is explicit and well documented.

## Phase 2 — adapters + report generation
- Adapters for Tokio task handles, cancellation tokens, tracked task groups, and common I/O surfaces.
- Import cancellation classifications from known method families.
- Generate lifecycle diffs from two pack/report snapshots.

## Phase 3 — ecosystem importers
- Docs portal import.
- Pathfinders and review tools can import lifecycle summaries.
- Integration with guidance/runtime-handoff lanes so docs can link “how to stop it” and “what to hand off when it failed”.

# Non-goals

- Not a new executor or runtime.
- Not a general structured-concurrency language/runtime proposal.
- Not a full tracing or observability platform.
- Not a replacement for graceful-shutdown frameworks.
- Not a whole incident-management or support portal.
- Not a static proof that no background work exists.

# Why this could matter

This is the crate that would let maintainers say:

- “Here is what our crate starts in the background.”
- “Here is what dropping a handle does.”
- “Here is what can be cancelled safely and what can partially progress.”
- “Here is the supported shutdown / drain / flush sequence.”
- “Here is how that lifecycle surface changed since the last release.”

That is the kind of boring runtime supportiveness layer that would make async-heavy Rust crates feel dramatically less magical and less trap-filled.

# Why now

1. Official Rust messaging now names **supportive interfaces from crates** as a real frontier.
2. Docs and code are still the main learning surfaces, which means lifecycle truth hidden in examples and issue comments remains too implicit.
3. Tokio’s docs now make cancellation, shutdown, task tracking, and I/O lifecycle semantics explicit enough that a contract layer is plausible.
4. Existing crates prove there is demand for shutdown, cancellation propagation, and structured concurrency — but they still optimize for implementation, not for a stable downstream contract.
5. The archive already covers setup, performance, observability, authority, guidance, runtime failure handoff, upgrade, and off-ramp support; lifecycle truth is the clean adjacent missing lane.

# Sharp edges / open questions

- How small can the lifecycle vocabulary stay while still expressing drop/detach/abort/join/close/drain truth usefully?
- How should the crate classify methods whose safety depends on external protocol state rather than only the method body?
- How much of the lifecycle surface can be imported mechanically versus requiring maintainer assertions?
- How should runtime-specific behavior (Tokio, async-std, custom executors) be represented without pretending they are identical?
- How should the crate express “safe to cancel for shutdown, unsafe to cancel for retry loop reuse” without confusing readers?
- Which lifecycle promises should count as semver-relevant surface drift?


# Implementation-ready shape now

The archive now has enough evidence and fixture vocabulary to stop treating **P-0520** as just a good idea.

A believable `0.1` should now ship around five review objects:

1. **activation boundary** — when background work really starts,
2. **stop semantics** — what `drop`, `abort`, `cancel`, `close`, `shutdown`, `join`, and `detach` actually do,
3. **blocking-work caveat** — where abort or cancellation claims stop being strong enough,
4. **teardown evidence** — what proves cleanup completed rather than merely started,
5. **drain recipe** — what the supported graceful, timed, and hard-stop paths are.

That is why the crate should be planned as a **joined support contract** rather than as a runtime helper or shutdown framework.
