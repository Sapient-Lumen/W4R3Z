# REV0395 — startup-owner repair ticket and bounded owner fixes

## What changed

- `stack_state_json.sh` now derives `startup_handoff_repair_ticket` beside `startup_handoff_witness`
- that new startup-owner ticket carries:
  - `status_id`
  - `route_id`
  - `target_owner_id`
  - one bounded recommended owner-fix command
  - compact `evidence_commands`
  - compact `verify_commands`
  - startup-owner status/drift signals explaining the route
- the ticket now chooses bounded owner fixes for the warm i3/X11 lane:
  - hide a duplicate autostart bridge so the user unit becomes the single owner again
  - unmask and enable the user-unit owner when startup units are masked
  - enable the user-unit owner when the lane drifted into autostart-only or no-owner startup
  - follow the live runtime handoff directly when startup ownership is already correct
- `sources.helpers.startup_handoff_status_json` and `sources.helpers.startup_handoff_drift_json` now mirror repair-ticket status/route/command next to the existing startup-owner witness metadata
- `stack_state.sh` now prints startup-owner repair-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around bounded startup-owner repair as part of the resident i3/X11 control plane

## Why this matters

The fused stack could already tell a private LLM whether startup ownership was duplicated, missing, autostart-only, or drifting. The remaining gap was actionability: the one-read lane still made callers reopen install docs or improvise the repair.

This revision closes that gap without broadening scope. The resident control plane now keeps one compact startup-owner repair handoff beside the witness, so the same fused stack can say not just *what startup ownership looks like*, but also *which bounded owner fix belongs next* for the warm i3/X11 lane.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_startup_handoff_witness_duplicate_risk`
- `test_generated_stack_state_json_carries_startup_handoff_witness_primary_owner_ready`
- `test_generated_stack_state_json_carries_startup_handoff_repair_ticket_duplicate_risk`
- `test_generated_stack_state_json_carries_startup_handoff_repair_ticket_promote_user_unit_owner`
- `test_generated_stack_state_json_carries_warm_runtime_ticket_activate_socket`
