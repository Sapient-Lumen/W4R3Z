# Revision REV0399 — dispatch-path witness and resident round-trip honesty

## Summary

REV0399 adds a first-class resident dispatch witness for the i3/X11 warm-runtime lane.

Before this change, the fused stack could prove that the shell, activation
environment, and running service environment were aligned. It could not yet prove
that the actual `vhk-emit -> socket -> resident busd` path was alive right now.

This revision adds that proof.

## What changed

- added `src/vhk/project/runtime_dispatch_probe.py`
- reserved internal runtime probe event: `vhk.runtime.probe`
- taught `vhk busd` to answer that probe with a bounded JSON acknowledgment
- bounded probe ack writes to approved probe roots only
- upgraded generated `check_runtime_json.sh` to emit:
  - `dispatch_path_probe`
  - `dispatch_path_summary`
- upgraded fused stack summaries/helper metadata with dispatch-probe status, latency, and ack pid
- upgraded `warm_runtime_ticket` with a new repair lane:
  - `status_id: repair_runtime_dispatch_path`
  - `route_id: dispatch_probe_then_restart`
