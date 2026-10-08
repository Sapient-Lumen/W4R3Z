# REV0384 — fused stack selected-macro repair recipe

## What changed

- `stack_state_json.sh` now derives `primary_macro_repair_recipe` for the author-queue-selected macro.
- The recipe is built only from already-loaded selected-macro stack truth: review queue, checked gate, latest run, command palette, consistency, and preferred entrypoints.
- The recipe is intentionally bounded to a short sequence instead of an open-ended planner.
- `sources.helpers.macro_author_queue_json` now also mirrors:
  - `selected_macro_repair_recipe_id`
  - `selected_macro_repair_recipe_status_id`
  - `selected_macro_repair_recipe_command`
- `stack_state.sh` now prints the selected macro's repair-recipe status, id, and first command.
- `README.md` and `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md` were tightened so the X11/i3 warm-runtime story is easier to follow.

## Recipe shape

The selected-macro repair recipe can now express:

- review first, then repair
- repair, then replay inspection
- dispatch now through the warm runtime
- direct run now
- fallback to the per-macro author loop when no stronger sequence is derivable

## Why this matters

`primary_macro_command_palette` and `primary_macro_execution_brief` answered *what looks best right now*, but they still left the private-LLM/operator lane to infer the short recovery sequence by hand. This revision keeps that sequence on the same one-read stack surface without adding more helper reads or bloating the resident control plane.

## Tests

- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe_direct_run`
- `test_generated_stack_state_json_carries_primary_macro_execution_brief`
- `test_generated_stack_state_json_carries_primary_macro_consistency`
- `test_generated_stack_state_json_carries_primary_macro_command_palette`
