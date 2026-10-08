# REV0393 — warm-runtime ticket and selected-macro service handoff

## What changed

- `stack_state_json.sh` now derives `warm_runtime_ticket` from already-fused runtime status, prerequisite checks, next-action truth, helper failures, and the selected macro's execute handoff
- that new runtime-service handoff carries:
  - `status_id`
  - `route_id`
  - one bounded recommended runtime or selected-macro handoff command
  - compact `evidence_commands`
  - compact `verify_commands`
  - bounded runtime identity (`socket_unit`, `service_unit`, `bus_event`, `bus_socket`)
  - bounded `selected_macro_handoff` when the resident lane is already usable
- the runtime ticket is intentionally resident-runtime-first:
  - helper failures now surface as `inspect_runtime_helpers`
  - missing session attachment now surfaces as `enter_graphical_session`
  - socket/service activation debt now surfaces as `activate_runtime_socket`
  - remaining prerequisites now surface as `clear_runtime_blockers`
  - degraded-but-usable stacks now surface as `inspect_runtime_warnings`
  - ready stacks now surface as `runtime_ready` or `runtime_ready_for_selected_macro`
- `sources.helpers.status_runtime_json`, `sources.helpers.check_runtime_json`, and `sources.helpers.next_action_json` now mirror warm-runtime-ticket status, route, and command so runtime-focused helpers stay aligned with the fused stack
- `stack_state.sh` now prints warm-runtime-ticket status, route, and command alongside the existing selected-macro ticket lines
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around the session-bound runtime-first one-read lane

## Why this matters

The fused stack already answered selected-macro recorder, cleanup, replay, execute, repair, probe, and signoff questions, but it still made a private LLM reopen runtime-focused helpers to recover one more basic truth: is the resident i3/X11 service lane itself broken, degraded, or honestly ready to hand off to the selected macro?

This revision closes that gap without adding a planner or broadening scope. The one-read stack now keeps one compact runtime-service handoff beside the selected-macro tickets, so the same control-plane read can say whether to re-enter the graphical session, reactivate the socket/service, clear remaining blockers, inspect degraded warnings, or proceed straight to the selected macro's bounded execute handoff.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_warm_runtime_ticket_activate_socket`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
- `test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_review_diff`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_verified_recent`
- `test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_ready_for_signoff`
