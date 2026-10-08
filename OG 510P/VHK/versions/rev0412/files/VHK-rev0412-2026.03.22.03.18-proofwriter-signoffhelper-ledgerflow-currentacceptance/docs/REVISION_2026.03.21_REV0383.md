# REV0383 — fused stack selected-macro consistency surface

## What changed

- `stack_state_json.sh` now derives `primary_macro_consistency` for the author-queue-selected macro.
- The new slice adds a contradiction-focused view over already-loaded selected-macro truth with no extra helper hops.
- `sources.helpers.macro_author_queue_json` now also mirrors:
  - `selected_macro_consistency_status_id`
  - `selected_macro_consistency_issue_ids`
- `stack_state.sh` now prints the selected macro's consistency status, primary issue, and recommended command.

## What it flags

- review debt still present while the selected macro also looks ready to execute
- stale acceptance vs warning/failing latest run
- runtime acceptance vs blocked latest dispatch receipt
- unresolved force overrides
- optimistic runtime posture vs weaker replay posture

## Why this matters

The fused stack already carried enough selected-macro truth for a private LLM or operator to notice contradictions, but it still required manual reconciliation. This revision turns those contradictions into explicit stack state so the warm i3/X11 lane stays one-read and less error-prone.

## Tests

- `test_generated_stack_state_json_carries_primary_macro_consistency`
- `test_generated_stack_state_json_carries_primary_macro_execution_brief`
- `test_generated_stack_state_json_carries_primary_macro_command_palette`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
