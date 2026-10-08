# Revision 0431 - macro-dispatch gate becomes receipt-first on the warm lane

## What changed

- `macro_dispatch_gate_json.sh <macro>` now checks whether `latest_dispatch_json.sh` already holds a current clean receipt for that same macro on the current resident-runtime witness.
- When the gate is otherwise ready-now and that receipt is still current, the gate now returns:
  - `decision.id = inspect_current_dispatch_evidence`
  - `decision.command = latest_dispatch_json.sh`
  - `repair_action.id = inspect_current_dispatch_evidence`
- `dispatch_readiness` now carries compact receipt-reuse truth:
  - `current_dispatch_evidence_available`
  - `latest_dispatch_evidence_status_id`
  - `latest_dispatch_result`
  - `latest_dispatch_route`
  - `latest_dispatch_recorded_at`
  - `latest_dispatch_recommended_command`
- `dispatch_contract` now includes `latest_dispatch_command` so thin per-macro consumers can jump straight to the receipt surface.

## Why

Before this revision, the repo had already taught `primary_macro_work_ticket` and `next_action_json.sh` not to blindly re-emit when a current clean warm-path receipt already existed. The per-macro checked gate still lagged behind and could recommend `dispatch_now` anyway. That made the most local execution surface less truthful than the higher-level helpers.

This revision aligns the per-macro gate with the rest of the resident control plane: when the warm lane is already proven and the newest receipt is still current, inspect the proof first. Do not spend another emit just because the gate is green.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_dispatch_gate_json_cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_reports_checked_dispatch_for_ready_macro`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_current_dispatch_evidence_before_reemit`
