# Crate lifecycle-surface product plan — 2026-03-17

This note exists to keep **P-0520 Crate Lifecycle Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing background-work / cancel-semantics / shutdown-obligation contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0520** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- what components or handles can start background work,
- whether that work starts eagerly, lazily, or only after an explicit `start` / `connect` / `subscribe` step,
- what happens when users drop, abort, close, cancel, or await those handles,
- which stop paths are graceful, timed, or hard-stop only,
- what evidence exists that cleanup actually finished,
- and what changed between releases.

It should **not** try to become a new runtime, a new structured-concurrency framework, a new graceful-shutdown orchestrator, or a static proof system for async cancellation.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, operators, and release reviewers, the crate should provide:

1. **One compact lifecycle contract** instead of folklore scattered across README prose, examples, trait docs, runtime notes, and issue threads.
2. **An activation map** so users know whether background work starts at construction time, on first use, or only after an explicit start step.
3. **A stop-semantics receipt** so `drop`, `abort`, `close`, `shutdown`, and `join` stop being blurred together.
4. **A shutdown-obligations bundle** so users know when they must `flush`, `shutdown`, `close`, `join`, or `drain` to avoid loss or leaks.
5. **A teardown-evidence report** so maintainers can distinguish “we asked it to stop” from “we observed cleanup complete”.
6. **A short human summary** that can be pasted into integration docs, support templates, or release notes.
7. **A release diff** that makes hidden detach / abort / shutdown regressions loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. adapters for common Tokio / async shutdown substrate instead of bespoke reimplementation,
4. one place to record lazy-start and blocking-work caveats,
5. and a CI gate for “this release changed lifecycle promises”.

## Recommended `0.1` command surface

### `cargo lifecycle-surface init`
Create a starter `lifecycle-pack.toml` by importing obvious candidates from:

- maintainer-declared public handles and components,
- known spawn sites or task groups when explicitly listed by the maintainer,
- declared shutdown / close methods,
- selected Tokio / tokio-util adapters,
- and known I/O teardown points.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo lifecycle-surface capture`
Emit one normalized receipt bundle from a declared lifecycle scenario.
This should capture:

- activation boundaries,
- background-work components,
- stop semantics,
- shutdown obligations,
- teardown evidence,
- and imported evidence sources.

`capture` should work on imported artifacts too.
It must not require that every scenario runs inside one blessed runtime framework.

### `cargo lifecycle-surface check`
Run the local validation pass:

- do declared handles and components parse,
- do activation classes and stop classes parse,
- do shutdown obligations align with observed fixtures,
- are blocking-work caveats explicit,
- are teardown-complete claims backed by evidence,
- and which parts remain manual-review-only?

### `cargo lifecycle-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `background_work_starts_before_user_opt_in`
- `drop_detaches_without_explicit_summary`
- `abort_requested_but_blocking_work_continues`
- `graceful_shutdown_claim_without_teardown_evidence`
- `close_method_present_but_not_required_in_summary`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo lifecycle-surface summary`
Render a short receiver-facing note for integration docs or operator runbooks.
A good summary answers:

- what starts background work,
- how to stop it cleanly,
- what happens on drop or abort,
- what cleanup evidence exists,
- and where the caveats are.

### `cargo lifecycle-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `activation_boundary_changed`
- `background_work_added`
- `background_work_removed`
- `drop_behavior_changed`
- `abort_behavior_changed`
- `shutdown_obligation_changed`
- `teardown_evidence_changed`
- `manual_review_required`

### `cargo lifecycle-surface pack`
Emit one compact `.lifecyclesurface.zip` bundle for CI artifacts, release review, downstream support, or integration handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `lifecycle_surface_model`
  - shared Rust types for packs, receipts, reports, manifests, evidence classes, and diffs
- `lifecycle_surface_discovery`
  - import logic for public handles, activation boundaries, stop semantics, and adapter hints
- `lifecycle_surface_check`
  - policy validation, drift checks, and doctor warnings
- `lifecycle_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
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

This pass adds three more important artifacts:

- `activation-boundary.policy.json` — what `constructor_eager`, `explicit_start`, `first_use_lazy`, `subscription_attached`, `external_runtime_owned`, and `manual_review_required` mean for lifecycle support.
- `stop-semantics.receipt.json` — the declared or observed stop behavior for a handle or component, including `drop_detaches`, `drop_aborts`, `close_then_join`, `cancel_then_wait`, `abort_best_effort`, or `manual_review_required`.
- `teardown-evidence.report.json` — what evidence exists that cleanup actually completed, such as join completion, tracker-drained state, explicit `shutdown` success, or only cancellation requested.

Those files matter because lifecycle support gets vague again if the archive only records “there is background work” without making clear:

- what triggers that work,
- what the stop verbs really do,
- and what counts as evidence that shutdown completed rather than merely started.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared public surface**
   - `lifecycle-pack.toml`
   - maintainer-declared components, handles, and stop paths
2. **Activation boundaries**
   - eager construction
   - explicit start/connect/subscribe
   - first-use lazy initialization
3. **Stop semantics**
   - drop / abort / cancel / close / shutdown / join behavior
4. **Teardown evidence**
   - join completion
   - tracker closed-and-empty
   - shutdown handshake completed
   - flush / close / drain receipts
5. **Race and retry notes**
   - partial progress
   - idempotence
   - replay or fencing requirements
6. **Manual review zones**
   - anything runtime-specific, backend-specific, or not directly observed

The importer should prefer visible uncertainty over synthesis.

## Activation-boundary policy

The first implementation should treat **activation boundaries as first-class review objects** and keep them separate from generic background-work inventory.

### What should count as activation classes in `0.1`

- `constructor_eager`
- `explicit_start`
- `first_use_lazy`
- `subscription_attached`
- `external_runtime_owned`
- `manual_review_required`

### What should *not* be encoded as activation classes in `0.1`

- “the crate probably starts tasks somewhere internally”
- “the first API call looked cheap, so background work probably had not started yet”
- “construction is sync, therefore no lifecycle obligations exist”

The activation policy should be versioned and diffable.
If a maintainer cannot explain when background work begins, the activation class should fall back to `manual_review_required`.

## Stop-semantics policy

The first implementation should treat **stop verbs as explicit review material**.
A good `0.1` should model:

- `drop_detaches`
- `drop_aborts`
- `cancel_then_wait`
- `close_then_join`
- `abort_best_effort`
- `blocking_work_not_abortable`
- `manual_review_required`

with optional evidence hints such as:

- `join_completed`
- `abort_called`
- `close_called`
- `shutdown_called`
- `tracker_closed`
- `tracker_wait_completed`
- `cancellation_requested`
- `blocking_task_returned`

The crate should not pretend that a visible `abort()` method proves work actually stopped.
That distinction is exactly why the stop-semantics receipt needs to exist.

## Teardown-evidence policy

The first implementation should treat **cleanup completion** as explicit evidence, not as a wish.

A good `0.1` should model:

- `no_teardown_required`
- `shutdown_requested_only`
- `join_completion_observed`
- `tracker_drained_observed`
- `protocol_shutdown_observed`
- `flush_then_shutdown_observed`
- `blocking_task_returned`
- `manual_review_required`

The crate should allow a maintainer to say “we requested cancellation but do not prove drain completion” or “we observed `shutdown` finish on the writer, but not peer acknowledgement”.
That is more honest than one flat “graceful shutdown supported” badge.

## Preferred proving grounds

The first proving grounds should be crates whose lifecycle behavior is already important and easy to misunderstand:

1. **Connection / client crates** — lazy background workers, reconnect loops, and explicit close paths.
2. **Streaming writer crates** — `write` vs `write_all`, flush/shutdown obligations, and close-handshake truth.
3. **Watcher / subscription crates** — attach-time background work, drop behavior, and channel drain semantics.
4. **Blocking bridge crates** — `spawn_blocking` work that ignores async abort once running and must stop cooperatively.

## Phase plan

### Phase 1 — vocabulary + manual packs
- Publish schema crate plus summary renderer.
- Support manually authored `lifecycle-pack.toml` and fixture-checked reports.
- Focus on Tokio-heavy proving grounds first because the substrate is explicit and well documented.

### Phase 2 — adapters + receipt generation
- Adapters for Tokio task handles, cancellation tokens, task trackers, and common I/O shutdown surfaces.
- Import stop-semantics and teardown hints from known method families.
- Generate lifecycle diffs from two pack/report snapshots.

### Phase 3 — ecosystem importers
- Docs portal import.
- Pathfinder / review tools import lifecycle summaries.
- Integration with diagnosis, runtime-handoff, persistence, and resource lanes where lifecycles overlap.

## Non-goals

- Not a new executor or runtime.
- Not a general structured-concurrency language/runtime proposal.
- Not a replacement for graceful-shutdown frameworks.
- Not a hosted incident or operations platform.
- Not a static proof that no background work exists.
- Not a magical verifier that can infer safe shutdown from arbitrary async code.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://tokio.rs/tokio/topics/shutdown
- https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
- https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
- https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- https://docs.rs/tokio/latest/tokio/macro.select.html
- https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- https://docs.rs/tokio/latest/tokio/io/trait.AsyncWrite.html
- https://docs.rs/async-shutdown/latest/async_shutdown/
- https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
- https://docs.rs/task_scope/latest/task_scope/
- https://docs.rs/crate/moro/0.4.0
