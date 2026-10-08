# REV0385 — blocker-aware repair focus and richer author-queue entrypoints

## What changed

- `macro_author_queue_json.sh` now exposes fuller action-ready entrypoints per macro, including checked warm dispatch, dispatch gate, direct run, latest-run report, and latest trace commands.
- `stack_state_json.sh` now upgrades `primary_macro_repair_recipe` with:
  - `focus_id`
  - `focus_reason`
  - `source_blocker_class_id`
  - `evidence_commands`
  - a bounded `step_budget` of 4 when the blocker class honestly needs one more inspect hop
- contract-debt recipes now keep contract rereads explicit
- desktop-target mismatch recipes now keep report/trace/contract inspection explicit
- direct-run recipes now expose their evidence commands instead of only the first execute command
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro repair focus and blocker-class ids
- `stack_state.sh` now prints selected-macro repair focus and blocker class

## Why this matters

The resident i3/X11 lane already knew *which* blocker class was stopping warm dispatch, but the fused repair recipe still flattened those cases into one generic short sequence. This revision keeps the lane one-read while making the next bounded sequence more honest to the actual failure class.

The project-wide author queue also becomes more executable: once a private LLM picks a macro, it already has the likely run/inspect/gate commands without immediately reopening another entrypoint map.

## Tests

- `test_macro_author_queue_json_ranks_macros_for_llm_triage`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe_direct_run`
- `test_generated_stack_state_json_carries_blocker_aware_desktop_target_recipe`
