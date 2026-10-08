# Revision 0425 — warm-runtime probe freshness attention

This revision closes the next honesty gap in the resident i3/X11 fast path.

## What changed

- The runtime-state cache now derives bounded-probe freshness from the cached `dispatch_probe_observation` and exposes:
  - `latest_dispatch_probe_freshness_status`
  - `latest_dispatch_probe_age_s`
  - `latest_dispatch_probe_freshness_window_s`
  - `latest_dispatch_probe_is_fresh`
- Durable runtime acceptance now carries `warm_runtime_probe_freshness_attention_id` and stales signoff when the cached successful probe has gone stale.
- `macro_dispatch_gate_json` now blocks checked dispatch with `warm_runtime_probe_refresh_required` / `runtime_probe_refresh` when the cached successful probe is stale, instead of treating old warm-path proof as current readiness.
- `primary_macro_work_ticket` and the helper summaries now carry probe-freshness handoff fields in addition to latency attention.
- `warm_runtime_ticket` now has an explicit `refresh_runtime_probe` route when the current runtime check reports a stale probe witness.

## Why

A resident session service needs recent bounded proof for its fast-path claim. A stale cached `ok` probe is still useful observability, but it is no longer enough to justify `dispatch now` or a current durable runtime signoff.

## Focused validation

- runtime-state cache probe freshness reporting
- dispatch-gate stale-probe blocker and repair route
- runtime-acceptance proof drift on stale probe freshness
- macro-runtime-board durable signoff staleness
- selected-macro work-ticket freshness handoff
