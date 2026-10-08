# Revision 0442 — 2026-03-22

## Summary

Revision 0442 threads the bounded `runtime_handoff` from `macro_runtime_board_json.sh` back into the top-level control plane. `next_action_json.sh` now reuses that selected-macro handoff when the narrower gate/work-ticket path is unavailable or only generic, and `stack_state_json.sh` now mirrors the same selected-macro runtime handoff explicitly.

## Why

Revision 0441 made the runtime board action-aware, but the resident i3/X11 control plane still had one fallback gap: `next_action_json.sh` could still collapse back to a vague `dispatch_or_run` answer even when the runtime board already carried a bounded selected-macro handoff such as `checked_dispatch_ready`.

That was bad for the private-LLM/operator loop because the project already had the answer, but the top-level handoff still forced local recombination or another board hop.

## What changed

- `next_action_json.sh` now reads `macro_runtime_board_json.sh` directly.
- `build_primary_macro_action(...)` now accepts the selected macro's runtime-board item.
- When the selected-macro gate/work-ticket path is missing, empty, or only a generic execution step, `next_action_json.sh` now reuses the bounded `runtime_handoff` from the runtime board.
- `next_action_json.sh` now exposes `primary_macro_runtime_board.runtime_handoff`.
- `recommendation_trace` now carries `selected_runtime_handoff_id` and `selected_runtime_handoff_command`.
- `next_action.sh` now prints the selected runtime handoff when present.
- `stack_state_json.sh` now mirrors `primary_macro_runtime_board.runtime_handoff`.
- `stack_state.sh` now prints `primary_macro_runtime_board_handoff` and `primary_macro_runtime_board_handoff_command`.
- `sources.helpers.macro_runtime_board_json` now mirrors the selected macro's runtime handoff id/command.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_uses_runtime_board_handoff_when_gate_is_generic`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_runtime_handoff`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_current_dispatch_evidence_before_reemit`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_next_action_helper_prefers_selected_macro_stale_receipt_handoff_before_dispatch_gate`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_runtime_board`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_carries_checked_dispatch_handoff_for_ready_macro`

## Result

The resident i3/X11 control plane now keeps a bounded selected-macro action alive at the top level even when one narrower helper surface is missing or too generic.
