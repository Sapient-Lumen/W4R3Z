# Frontier salience snapshot — 2026-03-20 (112)

This pass did **not** add another graceful-shutdown helper, another task supervisor, or another framework-specific websocket patch.
It deepened **P-0520 Crate Lifecycle Surface Pack Kit** by making one more product-critical truth explicit:

- **“graceful shutdown completed” is not reviewable unless the shutdown barrier and its escape paths are named explicitly.**

## Main judgment

The sharper missing layer is no longer merely “a crate-authored map of tasks and stop verbs.”
The sharper missing layer is a **crate-authored lifecycle bundle plus barrier-scope and escape-path receipts**.

The current Rust async/server substrate has changed enough to make that specific:

1. Tokio’s graceful-shutdown guide still frames shutdown as signal + propagate + wait, which means the wait boundary is part of the contract.
2. `TaskTracker` now spells out that `wait()` completes only when the tracked set is both closed and empty, but dropping the tracker itself does not abort tasks.
3. Tokio `JoinHandle` still detaches on drop, while `JoinSet` distinguishes drop-abort, `shutdown()` abort-and-wait, and `detach_all()` keep-running semantics.
4. Tokio maintainer guidance now states explicitly that timing out a `JoinHandle` does not cancel the task unless the caller also aborts it.
5. Current axum issue traffic shows both sides of the barrier problem: upgraded WebSocket work can escape the server shutdown future, and pending SSE streams can block it indefinitely.
6. axum’s own changelog still records nearby task-ownership leaks/fixes, reinforcing that “server shutdown support” is not one clean primitive.

That means the next worthy move is not “another cancellation primitive.”
It is one conservative crate family that can publish:

- **activation-boundary truth**,
- **stop-semantics truth**,
- **shutdown-barrier truth**,
- **escape-path truth**,
- **blocking-work caveats**,
- **teardown-evidence truth**,
- and **drain-recipe truth**.

## Why this beat nearby work

The archive already has adjacent lanes for:

- runtime failure handoff,
- observability surfaces,
- authority surfaces,
- resource surfaces,
- and general async/shutdown substrate.

What it still lacked was one compact way to say:

- “this graceful-shutdown future only means the listener stopped,”
- “this task group finished, but upgraded connection work is still outside the barrier,”
- “this timeout stopped waiting but did not stop work,”
- and “this barrier can stall behind a pending upstream dependency.”

That is a real receiver-facing product boundary, not just more async folklore.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still rising because 2026 registry/advisory substrate makes reviewable trust posture more buildable.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — materially stronger after this pass because shutdown-barrier scope and escape-path truth make the lane feel like a real cross-framework product instead of a vague “shutdown docs” wish.
5. **P-0027 text-input-kit** — still unusually strong because edit-path, geometry, and a11y-mirror truth cut across toolkits.
6. **P-0011 Crate Health Contract Kit** — still very strong because maintainer/support posture remains distinct from trust/risk posture.
7. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
8. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.

## What changed in the archive

Added:
- `entries/2026-03-20-292.md`
- `meta/frontier-salience-2026-03-20-112.md`
- `meta/crate-lifecycle-surface-product-plan-2026-03-20.md`
- `meta/crate-lifecycle-surface-barrier-boundaries-2026-03-20.md`
- `fixtures/crate-lifecycle-surface-pack-kit/shutdown-barrier.report.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/escape-path.receipt.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/axum_websocket_upgrade_task_escapes_server_shutdown_barrier/`
- `fixtures/crate-lifecycle-surface-pack-kit/axum_sse_pending_stream_blocks_shutdown_barrier/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-lifecycle-surface-pack-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-lifecycle-surface-pack-kit/README.md`
