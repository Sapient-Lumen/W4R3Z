# Revision 0427 — dispatch receipts now stale on any bounded-probe result drift

This revision tightens resident fast-path observability on the flagship i3/X11 lane.

## Problem

Dispatch receipt currentness already compared the daemon's cached bounded-probe posture, but it only treated probe-result drift as meaningful when the daemon crossed the success/failure boundary. That left one misleading case: a receipt captured while the daemon returned one failure result, such as `ack_timeout`, could still look current after the daemon drifted to a different failure result such as `invalid_ack`.

## Change

- `compare_runtime_instance_witness(...)` now marks `runtime_probe_status_drift` on any comparable `latest_dispatch_probe_status` change, not only when the success/failure family changed.
- The compare payload still exposes `runtime_probe_failure_changed`, but now uses it as extra explanation instead of as the gate for status drift.
- `latest_dispatch_json.sh` and `macro_dispatch_history_board_json.sh` inherit the stricter truth automatically because both surfaces already consume the runtime-witness comparison.

## Result

The newest warm-dispatch receipt now counts as current resident-runtime evidence only when the daemon still reports the same bounded-probe result, not merely the same broad success/failure class.
