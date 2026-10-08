# Crate Lifecycle Surface Pack Kit fixtures

These fixtures exist to keep **P-0520** concrete.

The point is not to prove that Rust lacks shutdown substrate.
The point is to keep a sharper question reviewable:

> what background work does this crate really start, what do its stop verbs really mean, and what evidence proves cleanup completed?

## Schema families

- `lifecycle-pack.schema.json` — declared lifecycle support contract
- `background-work.receipt.schema.json` — observed spawned tasks / workers / subscriptions
- `cancellation-surface.report.schema.json` — per-operation cancel/retry posture
- `shutdown-obligation.report.schema.json` — explicit cleanup obligations
- `shutdown-barrier.report.schema.json` — what shutdown completion actually means
- `escape-path.receipt.schema.json` — which work escapes or weakly connects to the main barrier
- `shutdown-phase.report.schema.json` — which named stop phase was actually reached
- `timeout-aftermath.receipt.schema.json` — what remains true after timeout or dropped waiting returns
- `drain-recipe.manifest.schema.json` — graceful / timed / hard-stop paths
- `race-retry-safety.report.schema.json` — replay/fencing posture after cancellation or partial progress
- `lifecycle-check.report.schema.json` — joined local verdict
- `lifecycle-diff.report.schema.json` — release-to-release drift
- `activation-boundary.policy.schema.json` — when work really starts
- `stop-semantics.receipt.schema.json` — what stop verbs actually do
- `teardown-evidence.report.schema.json` — what proves cleanup completed

## Scenario families with concrete example artifacts

- `join_handle_drop_detaches_background_task/`
  - `stop-semantics.receipt.example.json`
  - `teardown-evidence.report.example.json`
- `lazy_background_worker_starts_on_first_request/`
  - `activation-boundary.policy.example.json`
  - `background-work.receipt.example.json`
- `protocol_writer_requires_shutdown_not_drop/`
  - `shutdown-obligation.report.example.json`
  - `teardown-evidence.report.example.json`
- `streaming_writer/`
  - `cancellation-surface.report.example.json`
  - `race-retry-safety.report.example.json`
- `watcher_subscription/`
  - `stop-semantics.receipt.example.json`
- `connection_pool_client/`
  - `drain-recipe.manifest.example.json`
  - `lifecycle-check.report.example.json`
- `spawn_blocking_abort_not_guaranteed/`
  - `README.md`
  - `stop-semantics.receipt.example.json`
  - `teardown-evidence.report.example.json`
- `joinset_shutdown_vs_detach_all/`
  - `README.md`
  - `stop-semantics.receipt.example.json`
  - `drain-recipe.manifest.example.json`
- `axum_websocket_upgrade_task_escapes_server_shutdown_barrier/`
  - `README.md`
  - `shutdown-barrier.report.example.json`
  - `escape-path.receipt.example.json`
- `axum_sse_pending_stream_blocks_shutdown_barrier/`
  - `README.md`
  - `shutdown-barrier.report.example.json`
  - `escape-path.receipt.example.json`
- `joinhandle_timeout_drops_wait_but_task_keeps_running_until_abort/`
  - `README.md`
  - `timeout-aftermath.receipt.example.json`
- `tokio_runtime_shutdown_timeout_unblocks_caller_but_blocking_work_survives/`
  - `README.md`
  - `shutdown-phase.report.example.json`
  - `timeout-aftermath.receipt.example.json`

## Working rule

Do **not** let these fixtures collapse into another generic shutdown/runtime bucket.

They are here to keep these review objects separate:

1. activation boundary,
2. stop semantics,
3. shutdown barrier,
4. escape path,
5. blocking-work caveat,
6. teardown evidence,
7. shutdown phase,
8. timeout aftermath,
9. drain recipe.
