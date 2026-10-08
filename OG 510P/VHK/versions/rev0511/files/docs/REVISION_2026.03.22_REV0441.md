# Revision 0441 — runtime-board handoff lane

Revision 0441 tightens the project-wide execution board for the resident i3/X11 lane.

## What changed

- Added `runtime_handoff` to each `macro_runtime_board_json.sh` item.
- Added `summary.primary_handoff_id` and `summary.primary_handoff_command`.
- `runtime_handoff` now prefers:
  - `inspect_receipt_lane` when the newest same-macro receipt is the most useful next artifact
  - `checked_dispatch_ready` when the macro is genuinely ready for checked resident dispatch
  - `refresh_replay_proof_before_dispatch` for warm-runtime candidates
  - `direct_run_required` for prompt-heavy macros
  - `stabilize_before_runtime_dispatch` when recorder or cleanup debt still dominates

## Why it matters

The runtime board already carried enough raw data for a caller to infer the next move, but the private-LLM lane still had to combine posture, dispatch attention, and receipt surfaces manually. `runtime_handoff` keeps the board one-read and action-oriented without pretending it replaces deeper proof surfaces like the checked gate or replay board.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_runtime_board_json_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_reports_execution_posture`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_carries_checked_dispatch_handoff_for_ready_macro`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_prefers_receipt_lane_handoff_when_current_macro_receipt_exists`
- `pytest -q tests/test_macro_runtime_board_json_cli.py::test_macro_runtime_board_json_carries_macro_scoped_receipt_observability`
