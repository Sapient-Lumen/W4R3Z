# Revision 0426 — dispatch receipt runtime probe posture drift

Revision 0426 tightens resident-runtime observability around durable warm-dispatch receipts.

## What changed

- `compare_runtime_instance_witness(...)` now treats these as first-class receipt/runtime drift states when the newest receipt no longer matches the current daemon cache:
  - `runtime_probe_freshness_drift`
  - `runtime_probe_latency_drift`
  - `runtime_probe_status_drift`
- The comparison payload now exposes the current vs observed probe status, freshness, latency posture, and whether freshness/latency attention changed.
- `latest_dispatch_json.sh` now surfaces those new drift states through `latest_dispatch.dispatch_runtime_witness`.
- `macro_dispatch_history_board_json.sh` now maps probe-posture drift into more specific postures:
  - `dispatch_receipt_runtime_probe_refresh_stale`
  - `dispatch_receipt_runtime_latency_stale`
  - `dispatch_receipt_runtime_probe_status_stale`

## Why it matters

The flagship i3/X11 warm path is not just `daemon epoch still matches`. It is also `the resident fast-path proof posture is still current enough to trust`.

Before this revision, a receipt emitted against a fresh, in-budget probe could continue to look current in history even after the daemon's cached probe had gone stale or crossed the latency budget. That was too optimistic for a private-LLM control plane that is supposed to author, revise, and execute macros without reopening raw helper output.

Revision 0426 makes the receipt side honest: the control plane can now say whether the newest receipt is still current warm-path evidence or whether it needs a fresh bounded resident probe before being trusted again.
