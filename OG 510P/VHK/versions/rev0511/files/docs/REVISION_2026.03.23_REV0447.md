# Revision 0447 — top-level LLM workbench projection

Revision 0447 lifts the bounded macro-scoped LLM contract into the resident control plane itself. The selected-macro work ticket and direct per-macro author loop already had explicit `llm_workbench` objects; now `next_action_json.sh` and `stack_state_json.sh` project one chosen `primary_macro_llm_workbench` so a private LLM can tell which helper to reopen next without reconstructing that choice from stage ids and handoff fragments.

## What changed

- `next_action_json.sh` now runs `macro_author_loop_json.sh <selected-macro>` alongside the existing selected-macro helpers.
- `next_action_json.sh` now emits:
  - `primary_macro_author_loop`
  - `primary_macro_llm_workbench`
  - `recommendation_trace.selected_llm_workbench_source_id`
  - `recommendation_trace.selected_llm_workbench_mode_id`
  - `recommendation_trace.selected_llm_workbench_command`
- The workbench-selection policy is explicit:
  - prefer `primary_macro_work_ticket.llm_workbench` during recorder/review/acceptance-style stages
  - prefer `primary_macro_author_loop.llm_workbench` during execution-stage work
  - fall back to whichever lane is available
- `stack_state_json.sh` now mirrors:
  - `primary_macro_author_loop.llm_workbench`
  - `primary_macro_llm_workbench`
  - helper-summary fields for the chosen top-level workbench
- `stack_state.sh` and `next_action.sh` now print the chosen workbench source/mode/command in their human summaries.
- The generated stack README now explicitly lists `macro_latest_dispatch_json.sh <macro>` and describes the new top-level workbench projection.

## Why it matters

This makes the warm resident runtime more practical for a private LLM. A top-level control-plane read can now answer both of the questions that actually matter in day-to-day authoring:

1. what should happen next?
2. which bounded macro-scoped helper should I open to do that safely?

That keeps the i3/X11 resident lane fast and one-hop readable instead of forcing extra helper arbitration above the already-bounded per-macro surfaces.

## Local validation

- `python -m py_compile src/vhk/cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_json_projects_primary_llm_workbench_from_author_loop_execution`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_json_prefers_selected_work_ticket_workbench_for_review_stage`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_llm_workbench_projection`
- `pytest -q tests/test_macro_entrypoints_json_cli.py::test_macro_author_loop_json_adds_llm_workbench_for_recording_first_pass tests/test_macro_entrypoints_json_cli.py::test_macro_author_loop_json_adds_receipt_handoff_and_workbench_for_current_warm_receipt`
