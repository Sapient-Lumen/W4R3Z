# Revision 0434 — stale selected-macro receipts become first-class handoff evidence

## What changed

- `primary_macro_work_ticket` now detects when the selected macro already has a newest warm-runtime dispatch receipt for this lane, but that receipt is stale rather than current.
- In that case the work ticket now returns:
  - `stage_id = receipt`
  - `source_ticket_id = primary_macro_latest_dispatch`
  - `status_id = stale_dispatch_evidence_available`
  - `route_id = inspect_stale_dispatch_evidence_before_repair`
  - `recommended.command = latest_dispatch_json.sh`
- The work ticket still carries the compact `latest_dispatch_handoff`, so callers can see the stale-evidence status id and the receipt’s own bounded follow-up command on the same read.
- `next_action_json.sh` now reuses that selected-macro stale-receipt handoff directly, just as it already does for the selected-macro probe handoff.

## Why

The resident i3/X11 lane was already good at one specific receipt-first case: current clean receipts. It was also good at one specific blocked-side case: bounded live probe evidence. But it still flattened another important state back into generic execution: the selected macro already had the newest receipt, and that receipt already explained why current warm-lane proof had gone stale.

This revision keeps the control plane one-read on that adjacent branch too. When the newest receipt is still the most relevant artifact but no longer current, inspect it first before reopening a broader repair or emit path.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_stale_dispatch_receipt_before_generic_execution`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_stale_receipt_handoff_before_dispatch_gate`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_probe_handoff_before_dispatch_gate`
