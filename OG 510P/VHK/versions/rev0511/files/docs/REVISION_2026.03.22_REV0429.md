# Revision 0429 — selected-macro latest-dispatch evidence handoff

This revision threads current latest-dispatch truth back into the selected-macro traffic director instead of leaving it isolated in `latest_dispatch_json.sh`.

## What changed

- `primary_macro_work_ticket` now carries `latest_dispatch_handoff` when the newest project receipt belongs to the selected macro.
- The handoff includes:
  - `status_id`
  - `current`
  - `result`
  - `route`
  - `recorded_at`
  - `summary`
  - `reason`
  - `recommended_command`
  - `followup_commands`
- The selected-macro entrypoint map now also carries `latest_dispatch`.
- The fused stack now lifts the same receipt-evidence status/command into:
  - `primary_macro_latest_dispatch`
  - generated helper metadata for `macro_author_queue_json`, `next_action_json`, `primary_macro_work_ticket_json`, and `primary_macro_work_ticket`
  - `stack_state.sh` summary output
  - `primary_macro_work_ticket.sh` summary output

## Product decision

When the selected macro is otherwise dispatch-ready, has current runtime acceptance, and already has a current clean warm-runtime receipt on the current resident lane, the work ticket no longer defaults to another immediate checked dispatch. It now points to `latest_dispatch_json.sh` first.

That keeps the resident i3/X11 author loop from treating a fresh clean receipt as an instruction to re-emit blindly.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_primary_macro_work_ticket_cli.py`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_execution_ticket_when_latest_receipt_is_for_another_macro tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_helper_extracts_selected_macro_ticket`
