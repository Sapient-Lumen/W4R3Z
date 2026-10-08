# Revision 0432 - selected-macro work ticket becomes probe-first on desktop mismatch

## What changed

- `primary_macro_work_ticket` now carries a compact `probe_handoff` built from `primary_macro_probe_observation`.
- That handoff includes:
  - `status_id`
  - `source_id`
  - `probe_id`
  - `step_type`
  - `wait_kind`
  - `wait_count`
  - `summary` / `observation_summary`
  - bounded `observed` X11/i3 facts
  - `blocker_class_id`
  - `recommended_command`
  - `inspect_commands`
- When recorder/cleanup/replay/acceptance/runtime are otherwise clear, and the checked gate is blocked on `desktop_state_mismatch` with bounded live probe evidence already available, the work ticket now switches to:
  - `stage_id = probe`
  - `source_ticket_id = primary_macro_probe_observation`
  - `route_id = inspect_live_probe_before_execution`
- `stack_state.sh` and `primary_macro_work_ticket.sh` now print the selected-macro probe status/id/command.
- Helper metadata now also exposes the selected-macro work-ticket probe status/command for `macro_author_queue_json`, `next_action_json`, and `primary_macro_work_ticket_json`.

## Why

Before this revision, the fused stack already knew what the freshest bounded live wait had observed, but the selected-macro one-read surface still dropped to a generic execution ticket. That forced the private LLM or operator to reopen sibling surfaces just to reach the most relevant X11/i3 evidence.

This revision keeps the warm resident lane one-read on the blocked side too: when the problem is a live desktop-target mismatch and a bounded sample already exists, inspect that sample first.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_primary_macro_work_ticket_cli.py`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_probe_observation_before_generic_execution`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_execution_ticket_when_latest_receipt_is_for_another_macro`

Manual local repro also confirmed both generated helpers still run after the patch:
- `bin/primary_macro_work_ticket_json.sh`
- `bin/primary_macro_work_ticket.sh`
