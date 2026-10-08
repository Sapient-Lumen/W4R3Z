# Revision 0435 — checked dispatch becomes receipt-first for stale warm-lane evidence

## What changed

- `macro_dispatch_gate_json.sh <macro>` now detects when the newest same-macro warm-runtime receipt exists but is no longer current resident evidence.
- On that branch the gate now returns:
  - `decision.id = inspect_stale_dispatch_evidence`
  - `repair_action.id = inspect_stale_dispatch_evidence`
  - `decision.command = latest_dispatch_json.sh`
  - `repair_action.command = latest_dispatch_json.sh`
- The gate also now carries fuller latest-receipt observability under `dispatch_readiness`, including:
  - `stale_dispatch_evidence_available`
  - `latest_dispatch_evidence_current`
  - `latest_dispatch_evidence_summary`
  - `latest_dispatch_evidence_reason`
  - `latest_dispatch_followup_commands`
- `build_primary_macro_action(...)` now also knows how to reuse that gate-level stale-receipt recommendation directly when `primary_macro_work_ticket_json.sh` is unavailable, so the top-level helper still stays receipt-first on the fallback path.

## Why

Revision 0434 already made stale receipt evidence first-class on the selected-macro and top-level helper surfaces, but the per-macro checked gate still lagged behind. That left one inconsistency in the resident i3/X11 lane: a macro could already have the newest stale receipt explaining the drift, yet the per-macro gate could still say `dispatch_now` or point at broader repair without first surfacing that receipt artifact.

This revision fixes the remaining drift. The checked gate now treats stale newest receipts the same way it already treated current clean receipts: the lane may still be macro-locally ready, but the next best action is to inspect the newest receipt evidence before another emit or generic repair step.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_dispatch_gate_json_cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_prefers_stale_dispatch_evidence_before_reemit`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_uses_gate_stale_receipt_fallback_when_selected_macro_ticket_is_missing`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_stale_dispatch_receipt_before_generic_execution`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_stale_receipt_handoff_before_dispatch_gate`
