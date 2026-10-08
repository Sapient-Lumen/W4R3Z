# REV0375 — stack state carries primary macro recording

## What changed

- `stack_state_json.sh` now opens `macro_recording_json.sh <primary-macro>` when the author queue already names a primary macro.
- The fused stack payload now carries `primary_macro_recording` with recorder freshness, selector summary, and segment-review truth for the selected macro.
- `sources.helpers.macro_recording_json` now mirrors fast-triage recorder facts including freshness status, exact segment count, transition reason counts, and selector source id.
- `stack_state.sh` now prints `primary_macro_recording_macro`, `primary_macro_recording_freshness`, and `primary_macro_recording_selector_source`.

## Why this matters

The resident i3/X11 lane had already fused the selected macro's checked gate, latest run, contract, and author loop. But recorder freshness and selector/segment truth still required one more helper hop. This revision keeps recorder-side debt and selector evidence in the same one-read handoff that the private LLM or operator already uses to decide whether to revise, re-record, inspect, or dispatch.

## Tests

- `tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_recording`
- `tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_author_loop`
- `tests/test_i3_busd_stack_cli.py::test_generated_stack_state_json_carries_primary_macro_contract`
- `tests/test_i3_busd_stack_cli.py::test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
