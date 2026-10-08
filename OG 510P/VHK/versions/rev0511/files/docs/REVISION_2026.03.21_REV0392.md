# REV0392 — selected-macro acceptance ticket and durable signoff handoff

## What changed

- `stack_state_json.sh` now derives `primary_macro_acceptance_ticket` for the author-queue-selected macro
- that new selected-macro signoff handoff carries:
  - `status_id`
  - `route_id`
  - one bounded recommended repair/cleanup/replay/signoff command
  - compact `evidence_commands`
  - compact `verify_commands`
  - `runtime_signoff`
  - `ledger_update_handoff`
- the acceptance ticket is intentionally lifecycle-aware:
  - stack contradictions can now force `repair_before_signoff`
  - active cleanup debt can now force `cleanup_before_signoff`
  - stale or missing replay proof can now force `replay_before_signoff`
  - aligned selected-macro proof now yields `ready_for_signoff`
  - current runtime signoff now yields `acceptance_current`
- `ledger_update_handoff` now gives the private-LLM lane a bounded durable-ledger edit target:
  - ledger path / relative path / format
  - current selected-macro accepted + incomplete review issue codes
  - current runtime posture
  - a suggested runtime-acceptance entry skeleton
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro acceptance-ticket status, route, and command
- `sources.helpers.macro_acceptance_ledger_json` now mirrors selected-macro acceptance-ticket status, route, and command
- `sources.helpers.macro_replay_board_json` and `sources.helpers.macro_runtime_board_json` now also mirror acceptance-ticket status, route, and command so proof/signoff surfaces stay aligned
- `stack_state.sh` now prints selected-macro acceptance-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, `docs/I3_X11_RUNTIME_STACK.md`, and `docs/ISSUES_2026Q1.md` around the recorder -> cleanup -> replay -> execute -> signoff one-read lane

## Why this matters

The fused stack already knew recorder truth, cleanup debt, replay proof, execute route, and raw acceptance rows, but it still hid the final durable-signoff question inside separate surfaces. A private LLM could see whether a macro was close to done, yet still had to infer whether the honest next move was to repair contradictions, settle cleanup debt, mint fresh replay proof, or review/update the acceptance ledger.

This revision closes that gap without adding a mutation helper or widening into a planner. The warm i3/X11 control plane now keeps one compact signoff handoff beside the raw acceptance row, and that handoff includes a bounded ledger-update target so a private LLM can revise the durable signoff lane intentionally instead of scraping the ledger format back out of other helpers.

## Tests

- `python -m py_compile src/vhk/cli.py tests/test_i3_busd_stack_cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_acceptance`
- `test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_ready_for_signoff`
- `test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_repair_before_signoff`
- `test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_clear`
- `test_generated_stack_state_json_carries_primary_macro_replay_ticket_verified_recent`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
- `test_macro_acceptance_ledger_json_normalizes_review_and_runtime_signoff`
