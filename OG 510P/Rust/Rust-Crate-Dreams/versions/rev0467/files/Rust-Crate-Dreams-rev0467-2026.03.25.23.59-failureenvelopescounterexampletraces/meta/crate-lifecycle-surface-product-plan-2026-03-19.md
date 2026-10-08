# Crate Lifecycle Surface Pack Kit — product plan (2026-03-19)

This note sharpens **P-0520 Crate Lifecycle Surface Pack Kit** into a more implementation-ready `0.1` shape.

## Main judgment

The missing value is still **not** another graceful-shutdown framework, another structured-concurrency runtime, another generic cancellation helper, or another tracing/debugging package.

The sharper missing layer is a **crate-authored lifecycle contract** that makes five review questions boring:

1. **When does background work actually begin?**
2. **What do the stop verbs really mean?**
3. **Where are stop claims weaker because the work is blocking or externally owned?**
4. **What evidence proves cleanup finished rather than merely started?**
5. **What is the supported graceful, timed, and hard-stop drain recipe?**

That layer sits above real substrate that already exists:

- the Rust vision-doc work says crates need more **supportive interfaces**;
- the 2025 survey still says online docs and code are the main learning surfaces;
- Tokio’s graceful-shutdown guide already frames shutdown as signal + propagate + wait;
- `CancellationToken` and `TaskTracker` already provide signal-and-wait substrate;
- Tokio now documents that `JoinHandle` drop detaches, `JoinSet` drop aborts tracked tasks, and `JoinSet::shutdown()` aborts then waits;
- Tokio’s I/O docs already distinguish cancel-safe `write`/`flush`, restart-hostile `write_all`, and explicit `shutdown` semantics;
- `async_shutdown`, `tokio-graceful-shutdown`, `task_scope`, and `moro` already cover useful adjacent implementation slices.

So the gap is no longer “Rust needs shutdown primitives.”
The gap is that maintainers still do not have **one reviewable lifecycle bundle**.

## Product shape

Keep `0.1` compact, boring, and review-first.

The center of gravity should be five first-class review objects:

- **activation boundary**
- **stop semantics**
- **blocking-work caveat**
- **teardown evidence**
- **drain recipe**

Everything else in `0.1` should help author, check, diff, or summarize those objects.

## What the crate should provide other people

For downstream users, this crate should provide:

1. **Activation honesty** so construction, first-use, explicit-start, subscription-attachment, and runtime-owned work stay distinct.
2. **Stop-verb truth** so `drop`, `abort`, `cancel`, `close`, `shutdown`, `join`, and `detach` stop being blurred together.
3. **Blocking-work honesty** so crates do not overclaim what `abort()` or cancellation can actually stop.
4. **Teardown evidence** so “graceful shutdown supported” is backed by observed completion classes.
5. **Drain recipes** for graceful, timed, and hard-stop paths.
6. **Partial-progress and retry notes** for operations whose cancellation semantics matter to correctness.
7. **Release diffs** so shutdown regressions become reviewable.
8. **A short summary** that another maintainer can paste into docs, support replies, or release notes.

For maintainers, the crate should provide:

1. one compact pack file,
2. conservative discovery/import,
3. check + doctor + diff workflows,
4. explicit `manual_review_required` escape hatches,
5. and one bundle that survives issue-thread/README drift.

## Recommended `0.1` command surface

### `cargo lifecycle-surface init`
Generate a starter `lifecycle-pack.toml` by importing likely public handles, stop verbs, and task groups from declared public APIs and maintainer hints.
Anything uncertain should land as `manual_review_required`, not as fake confidence.

### `cargo lifecycle-surface capture`
Capture normalized lifecycle artifacts for a declared scenario:

- activation boundaries,
- background work,
- stop semantics,
- shutdown obligations,
- teardown evidence,
- and drain recipes.

### `cargo lifecycle-surface check`
Verify that:

- activation classes still match the scenario,
- stop verbs are not overclaimed,
- blocking-work caveats are explicit,
- teardown evidence matches the declared stop path,
- shutdown obligations remain honest,
- and manual-review boundaries are still visible.

### `cargo lifecycle-surface doctor`
Render human-facing warnings such as:

- `drop_detaches_without_summary`
- `abort_claim_exceeds_blocking_work_evidence`
- `background_work_starts_before_declared_boundary`
- `graceful_shutdown_claim_without_teardown_evidence`
- `joinset_detach_path_missing_from_summary`
- `manual_review_required`

### `cargo lifecycle-surface summary`
Render a receiver-facing “how this crate starts and stops” summary.

### `cargo lifecycle-surface diff <old> <new>`
Compare releases and classify:

- `activation_boundary_changed`
- `background_work_added`
- `stop_semantics_changed`
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
  - import logic for handles, stop verbs, and adapter hints
- `lifecycle_surface_check`
  - policy validation, warnings, and drift classification
- `lifecycle_surface_pack`
  - summary rendering, diffs, and zip bundle emission
- `cargo-lifecycle-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `lifecycle_surface_tokio`
- `lifecycle_surface_tokio_util`
- `lifecycle_surface_async_shutdown`
- `lifecycle_surface_io`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `lifecycle-pack.toml`
- `background-work.receipt.json`
- `cancellation-surface.report.json`
- `shutdown-obligation.report.json`
- `drain-recipe.manifest.json`
- `race-retry-safety.report.json`
- `lifecycle-check.report.json`
- `lifecycle-diff.report.json`
- `lifecycle.summary.md`
- `activation-boundary.policy.json`
- `stop-semantics.receipt.json`
- `teardown-evidence.report.json`

This pass keeps the schema footprint disciplined and instead makes the existing vocabulary more concrete with scenario examples.

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
4. **Blocking-work caveats**
   - `spawn_blocking`
   - runtime-owned background threads
   - external processes or drivers
5. **Teardown evidence**
   - join completion
   - tracker closed-and-empty
   - protocol shutdown completion
   - flush + shutdown completion
6. **Race and retry notes**
   - partial progress
   - replay or fencing requirements
7. **Manual review zones**
   - anything runtime-specific, backend-specific, or not directly observed

The importer should prefer visible uncertainty over synthesis.

## Concrete proving scenarios

The first proving set should stay small and brutally clear:

1. **JoinHandle drop detaches**
   - dropping a public handle is weaker than stopping the task
2. **Lazy background worker starts on first request**
   - construction and activation must stay separate
3. **Protocol writer requires shutdown, not just drop**
   - graceful protocol close is stronger than dropping the writer
4. **Streaming writer cancel/retry surface**
   - `write`, `flush`, `write_all`, and retry posture must stay distinct
5. **Watcher/subscription stop path**
   - drop, cancel, and watcher-drain semantics must stay separate
6. **`spawn_blocking` abort caveat**
   - abort requests do not guarantee running blocking work stops
7. **JoinSet shutdown vs detach path**
   - dropping, detaching, and explicit `shutdown()` are not the same contract

## Why this still looks worth building

The adjacent tools are real, which is exactly why this proposal now looks sharper rather than weaker.
Tokio and tokio-util already make many stop-path semantics explicit.
Async shutdown crates already cover orchestration patterns.
Structured-concurrency crates already show continuing demand for safer task lifetimes.
And today’s async I/O docs already expose differences between cancel-safe and restart-hostile operations.

That combination strengthens the case that the missing value is the **crate-authored lifecycle/support contract above them**, not another attempt to replace them.
