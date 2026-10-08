# Crate Lifecycle Surface Pack Kit — product plan (2026-03-20)

This note sharpens **P-0520 Crate Lifecycle Surface Pack Kit** into a more implementation-ready shape after the archive’s latest lifecycle pass.

## Main judgment

The missing value is still **not** another graceful-shutdown framework, another task supervisor, another websocket helper, or another structured-concurrency runtime experiment.

The sharper missing layer is a **crate-authored lifecycle contract** that now makes nine review questions boring:

1. **When does background work actually begin?**
2. **What do the stop verbs really mean?**
3. **What event actually counts as the shutdown barrier?**
4. **Which work is outside that barrier or needs a different stop route?**
5. **Which shutdown phase was actually reached before a budget expired?**
6. **What remains true after timeout or dropped waiting returns?**
7. **Where are stop claims weaker because the work is blocking, upgraded, detached, or externally owned?**
8. **What evidence proves cleanup finished rather than merely started?**
9. **What is the supported graceful, timed, and hard-stop drain recipe?**

That layer sits above real substrate that already exists:

- the Rust vision-doc work says crates need more **supportive interfaces**;
- Tokio’s graceful-shutdown guide already frames shutdown as signal + propagate + wait;
- `CancellationToken` and `TaskTracker` already provide signal-and-wait substrate;
- `TaskTracker::wait()` now explicitly waits for the tracked set to be both **closed and empty**;
- Tokio `JoinHandle` documents detach-on-drop behavior;
- Tokio `JoinSet` explicitly distinguishes drop-abort, `shutdown()` abort-and-wait, and `detach_all()` keep-running behavior;
- Tokio maintainer guidance now states explicitly that timing out a `JoinHandle` only stops waiting unless the task is also aborted;
- axum issue traffic shows that upgraded WebSocket work can escape server graceful shutdown while SSE work can block it indefinitely.

So the gap is no longer “Rust needs shutdown primitives.”
The gap is that maintainers still do not have **one reviewable lifecycle bundle that says what shutdown completion actually covers, how far shutdown progressed, and what remains true after timeout returns**.

## Product shape

Keep `0.1` compact, boring, and review-first.

The center of gravity should now be nine first-class review objects:

- **activation boundary**
- **stop semantics**
- **shutdown barrier**
- **escape path**
- **shutdown phase**
- **timeout aftermath**
- **blocking-work caveat**
- **teardown evidence**
- **drain recipe**

Everything else in `0.1` should help author, check, diff, or summarize those objects.

## What the crate should provide other people

For downstream users, this crate should provide:

1. **Activation honesty** so construction, first-use, explicit-start, subscription-attachment, and runtime-owned work stay distinct.
2. **Stop-verb truth** so `drop`, `abort`, `cancel`, `close`, `shutdown`, `join`, and `detach` stop being blurred together.
3. **Barrier truth** so `graceful shutdown completed` has a typed meaning instead of sounding like universal completion.
4. **Escape-path receipts** so upgraded connections, detached tasks, blocking workers, external workers, or pending upstream streams do not disappear from the support story.
5. **Shutdown-phase truth** so integrators can see how far the supported stop path actually progressed.
6. **Timeout-aftermath truth** so “timeout returned” does not sound like “the system is now quiescent.”
7. **Blocking-work honesty** so crates do not overclaim what `abort()` or cancellation can actually stop.
8. **Teardown evidence** so “graceful shutdown supported” is backed by observed completion classes.
9. **Drain recipes** for graceful, timed, and hard-stop paths.
10. **Release diffs** so shutdown regressions become reviewable.
11. **A short summary** that another maintainer can paste into docs, support replies, or release notes.

For maintainers, the crate should provide:

1. one compact pack file,
2. conservative discovery/import,
3. check + doctor + diff workflows,
4. explicit `manual_review_required` escape hatches,
5. explicit barrier-scope warnings,
6. and one bundle that survives issue-thread/README drift.

## Recommended `0.1` command surface

### `cargo lifecycle-surface init`
Generate a starter `lifecycle-pack.toml` by importing likely public handles, stop verbs, task groups, and barrier boundaries from declared public APIs and maintainer hints.
Anything uncertain should land as `manual_review_required`, not as fake confidence.

### `cargo lifecycle-surface capture`
Capture normalized lifecycle artifacts for a declared scenario:

- activation boundaries,
- background work,
- stop semantics,
- shutdown barriers,
- escape paths,
- shutdown obligations,
- teardown evidence,
- and drain recipes.

### `cargo lifecycle-surface check`
Verify that:

- activation classes still match the scenario,
- stop verbs are not overclaimed,
- shutdown barriers stay scoped honestly,
- escape paths are visible,
- blocking-work caveats are explicit,
- teardown evidence matches the declared stop path,
- shutdown obligations remain honest,
- and manual-review boundaries are still visible.

### `cargo lifecycle-surface doctor`
Render human-facing warnings such as:

- `graceful_shutdown_claim_without_barrier_scope`
- `tasktracker_closed_empty_excludes_untracked_work`
- `timeout_dropped_handle_without_abort`
- `upgrade_task_escape_untracked`
- `pending_stream_blocks_barrier`
- `timeout_returns_but_task_survives`
- `runtime_wait_abandoned_without_aftermath_receipt`
- `background_work_starts_before_declared_boundary`
- `abort_claim_exceeds_blocking_work_evidence`
- `manual_review_required`

### `cargo lifecycle-surface summary`
Render a receiver-facing “how this crate starts, stops, and what shutdown completion covers” summary.

### `cargo lifecycle-surface diff <old> <new>`
Compare releases and classify:

- `activation_boundary_changed`
- `background_work_added`
- `stop_semantics_changed`
- `shutdown_barrier_changed`
- `escape_path_changed`
- `blocking_work_caveat_changed`
- `shutdown_obligation_changed`
- `teardown_evidence_changed`
- `drain_recipe_changed`
- `manual_review_required`

### `cargo lifecycle-surface pack`
Emit one compact support bundle for CI artifacts, release review, downstream evaluation, or support threads.

## Recommended crate/workspace split

A good first workspace shape would be:

- `lifecycle_surface_model`
  - shared Rust types for packs, receipts, reports, summaries, and diffs
- `lifecycle_surface_import`
  - import logic for handles, stop verbs, task groups, barrier boundaries, and adapter hints
- `lifecycle_surface_check`
  - policy validation, warnings, and drift classification
- `lifecycle_surface_pack`
  - summary rendering, diffs, and zip bundle emission
- `cargo-lifecycle-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `lifecycle_surface_tokio`
- `lifecycle_surface_tokio_util`
- `lifecycle_surface_axum`
- `lifecycle_surface_io`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should now revolve around:

- `lifecycle-pack.toml`
- `background-work.receipt.json`
- `cancellation-surface.report.json`
- `shutdown-obligation.report.json`
- `shutdown-barrier.report.json`
- `escape-path.receipt.json`
- `drain-recipe.manifest.json`
- `race-retry-safety.report.json`
- `lifecycle-check.report.json`
- `lifecycle-diff.report.json`
- `lifecycle.summary.md`
- `activation-boundary.policy.json`
- `stop-semantics.receipt.json`
- `teardown-evidence.report.json`

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared public surface**
   - maintainer-declared handles, components, and stop paths
2. **Activation boundaries**
   - eager construction
   - explicit start/connect/subscribe
   - first-use lazy initialization
3. **Stop semantics**
   - drop / abort / cancel / close / shutdown / join / detach behavior
4. **Shutdown barriers**
   - signal sent
   - listener stopped
   - tracked set closed-and-empty
   - protocol drains completed
   - manual review zones
5. **Escape paths**
   - detached tasks
   - upgraded connections
   - pending upstream dependencies
   - blocking or externally owned work
6. **Blocking-work caveats**
   - `spawn_blocking`
   - runtime-owned background threads
   - external processes or drivers
7. **Teardown evidence**
   - join completion
   - tracker closed-and-empty
   - protocol shutdown completion
   - flush + shutdown completion
8. **Race and retry notes**
   - partial progress
   - replay or fencing requirements
9. **Manual review zones**
   - anything runtime-specific, backend-specific, or not directly observed

The importer should prefer visible uncertainty over synthesis.

## Concrete proving scenarios

The first proving set should stay small and brutally clear:

1. **JoinHandle drop detaches**
   - dropping a public handle is weaker than stopping the task
2. **JoinSet shutdown versus detach-all**
   - barrier scope, keep-running escapes, and explicit wait behavior must stay separate
3. **Timeout on JoinHandle without abort**
   - timed waiting is not task cancellation
4. **Axum WebSocket upgrade task escapes server barrier**
   - framework shutdown completion is weaker than upgraded-task completion
5. **Axum SSE pending stream blocks barrier**
   - a graceful-shutdown barrier can still stall behind an upstream wakeup dependency
6. **JoinHandle timeout stops waiting but task survives**
   - timed waiting is weaker than task cancellation and should emit aftermath truth
7. **Tokio runtime shutdown timeout returns while blocking work survives**
   - runtime-level budget exhaustion is weaker than quiescence and should emit both phase and aftermath truth
8. **Protocol writer requires shutdown, not drop**
   - graceful protocol close is stronger than dropping the writer
9. **`spawn_blocking` abort caveat**
   - abort requests do not guarantee running blocking work stops

## Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.
Tokio and tokio-util already make many stop-path semantics explicit.
Framework issue traffic now makes barrier-scope failures public and concrete.
Async shutdown crates already cover orchestration patterns.
And today’s async I/O docs already expose differences between cancel-safe and restart-hostile operations.

That combination strengthens the case that the missing value is the **crate-authored lifecycle/support contract above them**, not another attempt to replace them.
