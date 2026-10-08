# REV0390 — selected-macro replay ticket and replay-proof handoff

## What changed

- `stack_state_json.sh` now derives `primary_macro_replay_ticket` for the author-queue-selected macro
- that new selected-macro replay handoff carries:
  - `status_id`
  - `route_id`
  - one bounded recommended replay command
  - compact `evidence_commands`
  - compact `verify_commands`
  - the selected macro's replay posture and latest-run health
- the replay ticket is intentionally recorder-aware:
  - recorder freshness debt can now force `record_before_replay`
  - recorder review debt can now force `review_recording_before_replay`
  - missing replay proof can now force `run_for_replay_proof`
  - warned or failed matching runs now stay on bounded inspect-first replay routes
  - healthy replay proof can now hand off directly to the selected macro's execute ticket
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro replay-ticket status, route, and command
- `sources.helpers.macro_latest_run_json` now mirrors selected-macro replay-ticket status, route, and command
- `sources.helpers.macro_replay_board_json` now mirrors selected-macro replay-ticket status, route, and command
- `sources.helpers.macro_dispatch_gate_json` now also mirrors replay-ticket status, route, and command so execute-lane surfaces stay aligned
- `stack_state.sh` now prints selected-macro replay-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around the recorder → replay → execute one-read lane

## Why this matters

The fused stack already had a recorder ticket and an execute ticket, but it still under-compressed the replay question that sits between them: should the selected macro trust its current replay proof, inspect the newest warned or failed run, mint fresh proof with a direct run, or go back to recorder evidence first?

This revision closes that gap without widening into a planner. The warm i3/X11 control plane now keeps one compact replay-proof handoff beside the existing recorder and execute tickets, which is a better fit for a private LLM working from one fused stack snapshot.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_record_first`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_verified_recent`
- `test_generated_stack_state_json_carries_primary_macro_recording_ticket`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
- `test_generated_stack_state_json_carries_primary_macro_probe_observation`
- `test_macro_recording_json_selector_summary_prefers_macro_when`
