# REV0471 — X11/i3 target-authority witness on checked dispatch

Revision 0471 adds a compact X11/i3 target-authority lane to checked dispatch and selected-macro triage.

## What changed

- `macro_dispatch_gate_json.sh <macro>` now emits `target_authority`
  - selector authority source
  - selector field names
  - observed match/mismatch verdict when a preserved live probe observation exists
  - bounded recommended inspect/verify command
- `build_primary_macro_execution_ticket()` now preserves that target-authority witness and can synthesize it from smaller gate surfaces when the explicit field is absent.
- `primary_macro_work_ticket` now mirrors the same lane as `target_handoff`.
- `primary_macro_work_ticket` now carries `contract.target_handoff_projection`.
- `primary_macro_work_ticket.sh` and `stack_state.sh` now print compact target-handoff lines.
- helper metadata for `next_action_json.sh` and `primary_macro_work_ticket_json.sh` now includes selected-macro target-handoff status/command/match verdict.
- the actual CLI gate now hosts the target-authority helper in live Python code instead of only in generated-stack surfaces, so `macro_dispatch_gate_json` can emit the same witness directly.
- checked dispatch now keeps runtime-probe latency attention explicit even when freshness is also stale, so over-budget resident latency is not masked by refresh logic.

## Why

Warm dispatch should not only say whether dispatch is blocked; it should also say whether the macro's X11/i3 target selector has actual preserved proof behind it. This keeps the resident-runtime lane explicit about focus/workspace/window authority and gives a private LLM a bounded reopen path before replay.

## Focused validation

- `tests/test_macro_dispatch_gate_json_cli.py`
- `tests/test_primary_macro_work_ticket_cli.py`
- `tests/test_i3_busd_stack_cli.py`
- `tests/test_macro_entrypoints_json_cli.py`
