# Revision 0366 — checked-dispatch receipt stderr truth

This revision tightens the resident i3/X11 dispatch lane instead of broadening scope.

## What changed

- `macro-dispatch-gate-json` now carries a stable `dispatch_readiness.blocked_message` string derived from blocker ids, blocker-class detail, decision reason, and any desktop-target hint.
- `dispatch_macro_checked.sh` now preserves the actual checked-gate refusal text on the blocked path instead of writing a generic `dispatch gate blocked` placeholder into durable receipts.
- blocked checked-dispatch receipts now reach `latest_dispatch_json.sh` with the same refusal text a human or private LLM saw on stderr.
- the blocked-path receipt write was inlined inside the generated checked wrapper to avoid an extra fragile shell hop.

## Why this matters

The resident service is the primary execution lane. When it refuses a dispatch, the caller should be able to answer *why* from one receipt surface, not by reopening shell stderr or reconstructing meaning from blocker ids alone.

## Tests

- `tests/test_macro_dispatch_gate_json_cli.py`
- `tests/test_latest_dispatch_json_cli.py`
- `tests/test_i3_busd_stack_cli.py::test_generated_dispatch_macro_checked_wrapper_blocks_and_forces`
- `tests/test_i3_busd_stack_cli.py::test_generated_dispatch_receipt_tracks_emitted_checked_dispatch`
