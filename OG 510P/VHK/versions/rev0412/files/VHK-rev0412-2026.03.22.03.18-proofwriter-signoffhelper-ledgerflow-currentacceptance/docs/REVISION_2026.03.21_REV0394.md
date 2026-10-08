# REV0394 — startup-handoff witness and bounded owner drift

## What changed

- generated two new runtime-side helper surfaces for the flagship i3/X11 stack:
  - `bin/startup_handoff_status_json.sh`
  - `bin/startup_handoff_drift_json.sh`
- those helpers now summarize, for the generated socket/service pair:
  - current startup-owner verdict
  - observed user-unit file states
  - autostart bridge presence / Hidden / TryExec effectiveness
  - small coalesced startup-owner history for drift classification
- `stack_state_json.sh` now derives `startup_handoff_witness` from those helpers plus `warm_runtime_ticket`
- that new witness carries:
  - `status_id`
  - `route_id`
  - one bounded recommended command
  - compact `evidence_commands`
  - compact `verify_commands`
  - startup-owner status/drift signals
- `sources.helpers.startup_handoff_status_json` and `sources.helpers.startup_handoff_drift_json` now mirror witness status/route/command so the startup-owner helpers stay aligned with the fused stack
- `stack_state.sh` now prints startup-handoff witness status, route, command, current startup verdict, and drift verdict
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around startup ownership as a bounded resident-runtime concern, not a planner surface

## Why this matters

The fused stack already answered live runtime readiness and selected-macro recorder/cleanup/replay/execute/signoff questions, but it still left one practical ambiguity open: *will this same warm lane come back cleanly on the next login, or is startup ownership duplicated, missing, or drifting?*

This revision closes that gap without broadening scope. The resident control plane now keeps one compact startup-owner witness beside the live runtime ticket, so a private LLM or operator can see duplicate-start risk and startup-owner drift from the same one-read X11/i3 stack snapshot.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_startup_handoff_witness_duplicate_risk`
- `test_generated_stack_state_json_carries_startup_handoff_witness_primary_owner_ready`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
- `test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_ready_for_signoff`
- `test_generated_stack_state_json_carries_warm_runtime_ticket_activate_socket`
