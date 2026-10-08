# Revision 0430 — next-action receipt-first warm-path handoff

Revision 0430 fixes the remaining top-level helper drift in the i3/X11 flagship lane.

## What changed

- `next_action_json.sh` now reads `latest_dispatch_json.sh` as part of selected-macro execute triage.
- When the selected macro already has a **current clean** warm-runtime receipt, `next_action_json.sh` now returns:
  - `primary_action.id = inspect_current_dispatch_evidence`
  - `primary_action.command = ./bin/latest_dispatch_json.sh`
- The helper still falls back to `macro_dispatch_gate_json.sh <macro>` when the newest receipt is stale, belongs to another macro, or cannot be proved current.
- The machine-readable next-action payload now also includes a compact `latest_dispatch` slice and helper-source metadata for `latest_dispatch_json`.

## Why it matters

The selected-macro work ticket already stopped treating a current clean receipt as an excuse to emit again. The global `next_action_json.sh` helper was still lagging behind that product decision, which meant the fastest operator/LLM surface could recommend unnecessary warm-path emits.

This revision makes the top-level helper agree with the selected-macro ticket: inspect current receipt truth first, emit second.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_uses_dispatch_gate_for_ready_primary_macro`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
