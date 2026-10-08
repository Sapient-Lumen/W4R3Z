# REV0389 — selected-macro recording ticket and recorder selector summary

## What changed

- `macro_recording_json` now emits `recording.selector_summary`
- that selector summary keeps one bounded X11/i3 target view for recorder review:
  - `selector_source_id`
  - selected selector fields
  - recorder-stable selector fallback
  - exact/title/workspace pressure counts
- `stack_state_json.sh` now derives `primary_macro_recording_ticket` for the author-queue-selected macro
- the new selected-macro recorder handoff carries:
  - `status_id`
  - `route_id`
  - one bounded recommended recorder command
  - compact `evidence_commands`
  - compact `followup_commands`
  - the selected macro's recorder selector summary
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro recording-ticket status, route, and command
- `sources.helpers.macro_recording_json` now mirrors selected-macro recording-ticket status, route, and command
- `stack_state.sh` now prints selected-macro recording-ticket status, route, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, and `docs/I3_X11_RUNTIME_STACK.md` around the recorder-heavy one-read lane

## Why this matters

The fused stack already had an execute ticket, repair recipe, and live probe observation, but it still under-compressed recorder truth. The repo could show raw recorder payloads, yet a private LLM still had to reopen them to answer a simpler question: should this selected macro be recorded, re-recorded, inspected for drift, or reviewed for exact/title/workspace brittleness before another warm dispatch claim?

This revision closes that gap without broadening scope. The recorder helper now emits the selector summary the fused stack was already implicitly depending on, and the warm i3/X11 handoff now keeps a compact selected-macro recording ticket next to the execute ticket.

## Tests

- `test_macro_recording_json_reports_sidecar_summary`
- `test_macro_recording_json_selector_summary_prefers_macro_when`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_recording_ticket`
- `test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready`
