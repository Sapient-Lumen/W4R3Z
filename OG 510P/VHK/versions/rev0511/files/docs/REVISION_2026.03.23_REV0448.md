# Revision 0448 — resident-runtime workbench projection

Revision 0448 finishes the smaller-surface control-plane alignment for the resident i3/X11 lane. The fused stack and `next_action_json.sh` already projected one chosen `primary_macro_llm_workbench`, but the resident-runtime entry surfaces still lagged: `macro_runtime_board_json.sh` only exposed posture and runtime handoff, and `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh` still forced callers back into the full fused stack just to recover the same bounded macro-scoped edit/inspect/execute lane.

## What changed

- `macro_runtime_board_json.sh` now mirrors a per-macro `llm_workbench` copied from `macro_author_loop_json.sh <macro>`.
- Runtime-board workbenches are annotated with:
  - `source_id=macro_author_loop.llm_workbench`
  - `source_command=macro_author_loop_json.sh <macro>`
- `macro_runtime_board_json.sh` now also emits top-level summary fields for the primary macro workbench:
  - `primary_llm_workbench_source_id`
  - `primary_llm_workbench_mode_id`
  - `primary_llm_workbench_command`
  - `primary_llm_workbench_surface`
- `warm_runtime_ticket_json.sh` now extracts and mirrors:
  - `primary_macro_llm_workbench`
  - `primary_macro_runtime_board`
- `warm_runtime_ticket.sh` now prints the chosen workbench source/mode/command/surface in its operator summary.
- `stack_state_json.sh` now mirrors `primary_macro_runtime_board.llm_workbench` and helper-summary fields for both:
  - `macro_runtime_board_json.sh`
  - `warm_runtime_ticket_json.sh` / `warm_runtime_ticket.sh`
- `stack_state.sh` now prints runtime-board LLM mode/command in addition to the already-existing top-level chosen workbench summary.

## Why it matters

This makes the resident-runtime surfaces genuinely one-read for the flagship product loop. A private LLM or operator can now open either the runtime board or the warm-runtime ticket and answer both of the questions that actually matter:

1. what should the warm resident lane do next?
2. which bounded macro-scoped helper should I reopen next to inspect, edit, verify, or execute safely?

That keeps the i3/X11-first user-service architecture fast and practical instead of making the caller re-derive the right author loop from larger sibling surfaces.

## Local validation

- `python -m py_compile src/vhk/cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_projects_primary_llm_workbench_from_author_loop`
- `pytest -q tests/test_primary_macro_work_ticket_cli.py::test_warm_runtime_ticket_helper_projects_primary_macro_llm_workbench`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_runtime_handoff`
