# Frontier salience snapshot — 2026-03-20 (113)

This pass did **not** open another shutdown helper, another supervisor, or another “graceful server” lane.
It deepened **P-0520 Crate Lifecycle Surface Pack Kit** one more step by making another product-critical truth explicit:

- **a named shutdown barrier is still not enough unless the crate can say which shutdown phase was reached before a budget expired, and what remains true after timeout returns.**

## Main judgment

The sharper missing layer is no longer merely “a crate-authored map of tasks, stop verbs, barriers, and escape paths.”
The sharper missing layer is a **crate-authored lifecycle bundle plus shutdown-phase and timeout-aftermath receipts**.

The current Rust async/server substrate now makes that specific:

1. Tokio’s graceful-shutdown guide still frames shutdown as tell + propagate + wait, which already implies real phases instead of one magic completion bit.
2. `TaskTracker` says `wait()` completes only once the tracked set is both closed and empty.
3. Tokio maintainer guidance explicitly says timing out a `JoinHandle` only stops waiting unless the task is also aborted.
4. Tokio `spawn_blocking` docs say running blocking tasks cannot be aborted and runtime shutdown will wait indefinitely for them unless `shutdown_timeout` is used.
5. Tokio runtime docs say `shutdown_timeout` can unblock the caller while outstanding work and threads are leaked and continue running.
6. `hyper-util` graceful-shutdown docs say completion covers watched connections, which is useful but still narrower than total service quiescence.
7. Current axum / hyper issue traffic still shows both sides of the confusion: graceful-shutdown futures can either resolve too early for upgraded work or never resolve because long-lived streams keep the barrier alive.

That means the next worthy move is not “another timeout helper.”
It is one conservative crate family that can publish:

- **activation-boundary truth**,
- **stop-semantics truth**,
- **shutdown-barrier truth**,
- **escape-path truth**,
- **shutdown-phase truth**,
- **timeout-aftermath truth**,
- **blocking-work caveats**,
- **teardown-evidence truth**,
- and **drain-recipe truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- runtime failure handoff,
- observability surfaces,
- authority surfaces,
- resource surfaces,
- and general async/shutdown substrate.

What it still lacked was one compact way to say:

- “the barrier completed, but only the watched connection set was covered,”
- “the timeout unblocked the caller, but blocking work is still alive,”
- “the wait path ended, but a manual abort is still owed,”
- and “this stop path reached `accepting_stopped` but not `protocol_drains_finished`."

That is a real receiver-facing product boundary, not just more async folklore.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still strongest among release-support lanes because release-to-release truth remains broadly under-specified.
3. **P-0017 Trust Lens** — still rising because 2026 registry/advisory substrate makes reviewable trust posture more buildable.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — stronger again after this pass because phase/budget/aftermath truth makes the lane feel more like a serious cross-framework support substrate and less like “good shutdown docs.”
5. **P-0027 text-input-kit** — still unusually strong because edit-path, geometry, and a11y-mirror truth cut across toolkits.
6. **P-0011 Crate Health Contract Kit** — still very strong because maintainer/support posture remains distinct from trust/risk posture.
7. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
8. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.

## What changed in the archive

Added:
- `entries/2026-03-20-293.md`
- `meta/frontier-salience-2026-03-20-113.md`
- `meta/crate-lifecycle-surface-time-budget-boundaries-2026-03-20.md`
- `fixtures/crate-lifecycle-surface-pack-kit/shutdown-phase.report.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/timeout-aftermath.receipt.schema.json`
- `fixtures/crate-lifecycle-surface-pack-kit/tokio_runtime_shutdown_timeout_unblocks_caller_but_blocking_work_survives/`
- `fixtures/crate-lifecycle-surface-pack-kit/joinhandle_timeout_drops_wait_but_task_keeps_running_until_abort/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-lifecycle-surface-pack-kit.md`
- `meta/crate-lifecycle-surface-product-plan-2026-03-20.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-lifecycle-surface-pack-kit/README.md`
