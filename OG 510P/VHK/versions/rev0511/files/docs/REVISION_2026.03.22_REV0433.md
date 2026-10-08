# Revision 0433 — next-action helper now reuses selected-macro probe handoff

This revision closes the next top-level control-plane drift on the i3/X11-first resident lane.

## What changed

- `next_action_json.sh` now reads `primary_macro_work_ticket_json.sh` in addition to the author queue, checked gate, latest-run health, and latest-dispatch helpers.
- When the selected macro work ticket is already in `stage_id = probe` with route `inspect_live_probe_before_execution`, the top-level helper now returns that probe-inspection action directly instead of flattening the same macro back into a generic gate/execution recommendation.
- The next-action payload now carries a compact `primary_macro_work_ticket` slice plus `sources.primary_macro_work_ticket_json` metadata so thin callers can see which bounded selected-macro handoff shaped the recommendation.

## Why it matters

The resident stack already knew when a bounded live X11/i3 sample had captured the current desktop mismatch for the selected macro. Before this revision, that truth stopped at `primary_macro_work_ticket`; the first helper a private LLM or operator opened could still recommend a more generic next step. Now the top-level helper stays aligned with the one-read selected-macro handoff and remains probe-first when the warm lane is blocked on current live desktop state.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_uses_dispatch_gate_for_ready_primary_macro`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_probe_handoff_before_dispatch_gate`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_consumes_macro_review_queue`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_probe_observation_before_generic_execution`
