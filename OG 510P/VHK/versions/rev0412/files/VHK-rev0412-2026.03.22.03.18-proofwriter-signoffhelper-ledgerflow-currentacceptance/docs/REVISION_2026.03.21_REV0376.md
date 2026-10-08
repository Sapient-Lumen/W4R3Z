# REV0376 — stack state now carries primary macro entrypoints

## What changed

- `stack_state_json.sh` now mirrors the author queue's selected macro entrypoints under `primary_macro_entrypoints`.
- `sources.helpers.macro_entrypoints_json` now includes the selected macro name plus the key direct-run, author-loop, and warm-runtime entrypoints for fast triage.
- `stack_state.sh` now prints the selected macro's entrypoint mode and the top author-loop / warm-runtime / direct-run commands.

## Why this matters

The fused stack snapshot already carried the selected macro's checked gate, latest run, contract, author loop, and recorder truth. But actually acting on that diagnosis still required reopening the project-wide `macro_entrypoints_json.sh` map or reconstructing commands by hand. This revision keeps the resident i3/X11 lane one step tighter by letting the same stack snapshot answer both *what is true now* and *what exact command should I use next* for the selected macro.

## Tests

- added `test_generated_stack_state_json_carries_primary_macro_entrypoints`
- updated the end-to-end generated stack execution test to assert that the fused stack payload carries the selected macro's preferred warm-runtime entrypoint
