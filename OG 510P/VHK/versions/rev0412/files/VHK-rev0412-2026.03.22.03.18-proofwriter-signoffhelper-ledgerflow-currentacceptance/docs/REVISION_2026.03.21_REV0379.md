# Revision 0379 — stack state carries selected macro latest dispatch

## What changed

- `bin/stack_state_json.sh` now lifts the author-queue-selected macro's latest dispatch receipt directly out of the already-loaded dispatch-history board.
- Added fused payload slice `primary_macro_latest_dispatch`.
- Added selected-macro dispatch receipt facts under `sources.helpers.macro_dispatch_history_board_json`:
  - `selected_macro_latest_result`
  - `selected_macro_primary_blocked_class_id`
  - `selected_macro_unresolved_force_override`
- `bin/stack_state.sh` now prints the selected macro's latest dispatch summary when present.

## Why this matters

The fused warm-runtime stack already carried the selected macro's gate, latest run, contract, author loop, recorder truth, entrypoints, acceptance, and board slices. But callers still had to inspect the dispatch-history row manually to answer whether that selected macro's most recent checked/raw dispatch was blocked, emitted, or still living behind an unresolved forced override.

This revision keeps the i3/X11 resident-runtime handoff closer to a true one-read control plane without adding another helper hop.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_latest_dispatch`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_board_slices`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_acceptance`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
