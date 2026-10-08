# Revision 0439 — scoped receipt evidence for selected-macro handoffs

Revision 0438 made the receipt surfaces explicit, but one ambiguity remained inside the copied evidence objects. Once `warm_runtime_evidence` was lifted into `primary_macro_work_ticket`, `next_action_json.sh`, or fused stack-state, the payload no longer told a caller whether that evidence came from the project-global newest receipt or the selected macro's newest receipt.

This revision makes the receipt lane explicit inside the evidence itself and threads that scope through the selected-macro handoff surfaces.

## What changed

- `latest_dispatch_json.sh` and `macro_latest_dispatch_json.sh <macro>` now stamp receipt scope directly into the payload:
  - `latest_dispatch.scope_id`
  - `latest_dispatch.scope_command`
  - `latest_dispatch.warm_runtime_evidence.receipt_scope_id`
  - `latest_dispatch.warm_runtime_evidence.receipt_scope_command`
- `warm_runtime_evidence.recommended.source_id` is now scope-correct:
  - project-global receipt evidence keeps `latest_dispatch.*`
  - macro-scoped receipt evidence now uses `macro_latest_dispatch.*`
- `primary_macro_work_ticket.latest_dispatch_handoff` now carries `scope_id` and `scope_command`.
- `next_action_json.sh` now mirrors the chosen receipt lane in `recommendation_trace.selected_receipt_scope_id` and `recommendation_trace.selected_receipt_command`.
- Human/operator summaries now print the selected receipt scope where applicable.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_latest_dispatch_json_cli.py tests/test_macro_latest_dispatch_json_cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_i3_busd_stack_cli.py`
- targeted pytest slices around latest-dispatch, macro-latest-dispatch, selected-macro work-ticket, and next-action receipt-scope behavior
