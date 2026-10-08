# REV0388 — selected-macro execution ticket for one-read warm dispatch handoff

## What changed

- `stack_state_json.sh` now derives `primary_macro_execution_ticket` for the author-queue-selected macro
- the new selected-macro execute surface carries:
  - `status_id`
  - `execution_mode_id`
  - `route_id`
  - one bounded recommended execute-or-inspect command
  - compact `preflight_commands`
  - compact `verify_commands`
  - warm-lane route contract details when checked dispatch is the honest path
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro execution-ticket status, route, and command
- `sources.helpers.macro_dispatch_gate_json` now mirrors selected-macro execution-ticket status, route, and command
- `stack_state.sh` now prints selected-macro execution-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, and `docs/I3_X11_RUNTIME_STACK.md` around the new execute handoff lane

## Why this matters

The fused stack already named blocker class, repair recipe, and bounded live probe observations, but it still under-specified the actual execute handoff for the selected macro.

This revision closes that gap without widening into a planner. A private LLM or operator can now read one fused stack snapshot and see whether the honest next move is checked warm dispatch, direct run, inspect first, or repair first, along with the compact preflight and verification commands that keep the resident i3/X11 lane observable.

## Tests

- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_execution_brief`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe`
- `test_generated_stack_state_json_carries_blocker_aware_desktop_target_recipe`
- `test_generated_stack_state_json_carries_primary_macro_probe_observation`
