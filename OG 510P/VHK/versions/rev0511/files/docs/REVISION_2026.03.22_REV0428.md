# Revision 0428 — latest-dispatch warm-runtime evidence handoff

This revision makes `latest_dispatch_json.sh` actionable for the resident i3/X11 fast path instead of merely descriptive.

## What changed

- Added `latest_dispatch.warm_runtime_evidence` to classify whether the newest dispatch receipt is still current resident-runtime evidence.
- The new verdict carries:
  - `status_id`
  - `current`
  - `summary`
  - `reason`
  - `recommended`
  - `followup`
- Contract-only drift now routes back to the current per-macro checked-dispatch gate.
- Runtime/session/probe drift now routes back to the warm-runtime ticket instead of forcing callers to infer the repair surface by hand.
- The fused stack helper summary now lifts the latest-dispatch evidence status and command into the generated helper metadata and `stack_state.sh` summary output.

## Why it matters

A private LLM should be able to inspect the newest dispatch receipt and immediately know whether that receipt is still valid fast-path evidence for the resident daemon. If it is stale, the receipt should also say whether the next move is `warm_runtime_ticket.sh` or `macro_dispatch_gate_json.sh <macro>`.

## Validation

- `python -m py_compile src/vhk/cli.py tests/test_latest_dispatch_json_cli.py tests/test_i3_busd_stack_cli.py`
- `pytest -q tests/test_latest_dispatch_json_cli.py tests/test_macro_dispatch_history_board_json_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_dispatch_receipt_tracks_emitted_checked_dispatch`
