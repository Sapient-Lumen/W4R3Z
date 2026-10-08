# REV0391 — selected-macro cleanup ticket and cleanup-proof handoff

## What changed

- `stack_state_json.sh` now derives `primary_macro_cleanup_ticket` for the author-queue-selected macro
- that new selected-macro cleanup handoff carries:
  - `status_id`
  - `route_id`
  - one bounded recommended cleanup-or-proceed command
  - compact `evidence_commands`
  - compact `verify_commands`
  - the selected macro's selector summary plus cleanup-relevant signals
- the cleanup ticket is intentionally recorder-aware:
  - missing or stale recorder truth can now force `record_before_cleanup`
  - recorder newer-than-source drift can now force `reconcile_recording_before_cleanup`
  - exact/title/workspace selector pressure can now force `review_cleanup_diff`
  - cleanup-clear macros can now hand off straight to replay/execute instead of reopening recorder helpers
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro cleanup-ticket status, route, and command
- `sources.helpers.macro_recording_json` now mirrors selected-macro cleanup-ticket status, route, and command
- `sources.helpers.macro_dispatch_gate_json` now also mirrors cleanup-ticket status, route, and command so execute-lane surfaces stay aligned
- `stack_state.sh` now prints selected-macro cleanup-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around the recorder → cleanup → replay → execute one-read lane

## Why this matters

The fused stack already had recorder, replay, and execute tickets, but it still hid the source-mutation question inside broader recorder advice. A private LLM could see recorder truth and replay truth, yet still had to infer whether the honest next move was to re-record before cleanup, reconcile recorder/source drift, inspect the cleanup diff, or skip cleanup and move on.

This revision closes that gap without widening into a planner. The warm i3/X11 control plane now keeps one compact cleanup handoff between the recorder and replay tickets, which is a better fit for a private LLM working from one fused stack snapshot.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_review_diff`
- `test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_clear`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_record_first`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_verified_recent`
- `test_generated_stack_state_json_carries_primary_macro_recording_ticket`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
