# Revision 0422 — warm-path latency attention

This revision turns resident-runtime probe latency into a first-class control-plane signal on the i3/X11 lane.

## What changed

- `summarize_runtime_dispatch_probe(...)` now carries:
  - `latency_budget_ms`
  - `latency_within_budget`
  - `latency_status`
- `warm_runtime_ticket` now routes `status_id=inspect_runtime_latency` / `route_id=probe_latency_then_dispatch` when the resident daemon answers the bounded probe but exceeds the warm-path latency budget.
- `primary_macro_work_ticket.execution_handoff` now carries the same latency signal plus `latency_attention_required` and `inspect_runtime_latency_command`.
- `warm_runtime_ticket.sh`, `primary_macro_work_ticket.sh`, and `stack_state.sh` now print the latency signal and measurement.

## Why

For VHK's i3/X11-first architecture, `reachable` is not the same as `healthy fast path`. The resident service exists to keep emit/dispatch thin and warm; when the bounded dispatch probe is consistently over budget, the control plane should say so explicitly and steer the operator or private LLM toward inspection before pretending checked dispatch is healthy.

## Focused validation

- `tests/test_runtime_dispatch_probe.py::test_runtime_dispatch_probe_summary_reports_over_budget_latency`
- `tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_runtime_latency_attention_before_checked_dispatch`
- `tests/test_primary_macro_work_ticket_cli.py::test_warm_runtime_ticket_helper_reports_probe_latency_attention`
