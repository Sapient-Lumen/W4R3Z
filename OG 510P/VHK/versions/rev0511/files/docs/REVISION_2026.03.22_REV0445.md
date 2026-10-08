# Revision 0445 — selected-macro LLM workbench contract

## What changed

- `build_primary_macro_work_ticket(...)` now emits `llm_workbench`, a compact stage-aware author/edit/execute contract for the selected macro.
- The workbench includes:
  - `mode_id`
  - `recommended_command`
  - `inspect_first`
  - `verify_after_change`
  - `edit_target`
  - `edit_loop`
  - `execute_when_clear`
  - `stop_condition`
- `stack_state.sh` now prints `primary_macro_work_ticket_llm_mode` and `primary_macro_work_ticket_llm_recommended_command`.
- `primary_macro_work_ticket.sh` now prints `llm_mode` and `llm_recommended_command`.
- Added `docs/ACTIVE_PRODUCT_CONTRACT_2026.03.22.md` to make the active X11/i3 product contract explicit and easier to hand to a human or private LLM.

## Why

The repo already had the raw ingredients for private-LLM authoring, but the selected-macro surface still required callers to infer too much from scattered fields. Rev0445 turns that implicit contract into one explicit bounded object so the LLM can stay on the selected-macro lane:

- inspect the right evidence first
- edit the right source file
- execute through the intended warm path when clear
- verify with the right post-change surfaces
- stop when the current stage is actually done

## Local tests

Focused local verification:

- `pytest -vv tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_prefers_recording_before_other_lanes`
- `pytest -vv tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear`
- `pytest -vv tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_helper_extracts_selected_macro_ticket`
