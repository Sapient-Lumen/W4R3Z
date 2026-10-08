# Revision 0436 — selected-macro latest-dispatch becomes macro-scoped

## What changed

- Added `vhk macro-latest-dispatch-json <project> <macro>` and generated `bin/macro_latest_dispatch_json.sh <macro>` as the explicit selected-macro receipt surface.
- The new helper returns the newest warm-runtime dispatch receipt for the requested macro even when a different macro emitted later.
- Selected-macro control-plane paths now use that macro-scoped receipt surface instead of consulting the project-global newest receipt:
  - `primary_macro_work_ticket`
  - generated `next_action_json.sh` helper state
  - fused `stack_state_json.sh` primary-macro receipt projection
  - dispatch-history board followups and related selected-macro entrypoints
- The generated stack README/control-plane manifest now advertises `bin/macro_latest_dispatch_json.sh <macro>` beside the project-wide `bin/latest_dispatch_json.sh`.

## Why

Revision 0435 made the warm lane receipt-first for stale evidence, but selected-macro correctness was still leaky. Several selected-macro helpers reused `latest_dispatch_json.sh`, which is a project-wide surface. In a busy project that meant the selected macro could lose its freshest receipt handoff as soon as some other macro emitted more recently.

That is the wrong failure mode for the flagship VHK lane. The resident i3/X11 control plane should stay centered on the currently selected macro and only widen to project-global observability when that actually helps. This revision makes that boundary explicit: project-wide receipt truth stays available, but selected-macro author/repair/execute loops now read a selected-macro receipt surface.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_latest_dispatch_json_cli.py tests/test_macro_dispatch_gate_json_cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_macro_latest_dispatch_json_cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_prefers_stale_dispatch_evidence_before_reemit`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py::test_macro_dispatch_gate_json_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_stale_dispatch_receipt_before_generic_execution`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_selected_macro_receipt_when_global_latest_receipt_is_for_another_macro`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_stale_receipt_handoff_before_dispatch_gate`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_uses_gate_stale_receipt_fallback_when_selected_macro_ticket_is_missing`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_latest_dispatch`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
