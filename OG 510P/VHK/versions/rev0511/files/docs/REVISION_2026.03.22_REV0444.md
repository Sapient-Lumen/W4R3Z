# Revision 0444 — warm-runtime ticket reuses runtime-board handoff

## What changed

- `build_warm_runtime_ticket(...)` now accepts the selected macro's runtime-board item.
- When runtime is healthy but the selected macro's execution ticket is only generic, the warm-runtime ticket now prefers the runtime board's bounded `runtime_handoff`.
- `warm_runtime_ticket.selected_macro_handoff` now carries:
  - `source_kind` (`runtime_handoff` vs `execution_ticket`)
  - `source_id`
  - `runtime_handoff_id` / `runtime_handoff_command`
  - `selected_receipt_scope_id` / `selected_receipt_status_id` / `selected_receipt_command`
- `stack_state_json.sh` helper metadata now mirrors the chosen warm-runtime selected-macro handoff source/command/id.
- `warm_runtime_ticket.sh` and `stack_state.sh` now print the chosen selected-macro handoff source and command.

## Why it matters

`macro_runtime_board_json.sh` already knew the bounded selected-macro next move, and rev0443 already reused that on `primary_macro_work_ticket_json.sh`. Rev0444 closes the remaining smaller-surface gap on the resident lane itself: once runtime is healthy, the warm-runtime ticket no longer falls back to a generic selected-macro execution answer when the runtime board already has a sharper checked-dispatch or receipt-first handoff.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- Focused local test: `tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_prefers_runtime_board_handoff_in_warm_runtime_ticket_when_execution_ticket_is_generic`
