# Revision 0367 — live probe hints in checked-dispatch receipts

This revision keeps the resident i3/X11 execution lane one read more actionable.

## What changed

- latest-run health now derives a `probe_hint` when the newest matching run already points at a likely live desktop-state probe mismatch
- `macro_dispatch_gate_json` now carries that as `dispatch_readiness.live_probe_hint`
- blocker details now preserve the same `live_probe_hint`
- durable dispatch receipts and `latest_dispatch_json.sh` now preserve and normalize that same hint
- blocked checked-dispatch text can now mention the likely failed live probe as part of the refusal context

## Why it matters

The private-LLM and operator lanes can now tell not just that warm dispatch was blocked, and not just which X11/i3 target selector was expected, but also which live probe most likely failed on the newest matching run. That is a better fit for the flagship resident-runtime lane than reopening project-wide history or broadening into generic Linux abstraction.

## Tested

- `tests/test_latest_run_health_json_cli.py`
- `tests/test_macro_dispatch_gate_json_cli.py`
- `tests/test_latest_dispatch_json_cli.py`
- `tests/test_i3_busd_stack_cli.py`
- `tests/test_macro_dispatch_history_board_json_cli.py`
- `tests/test_macro_dispatch_catalog_json_cli.py`
- `tests/test_macro_entrypoints_json_cli.py`
- `tests/test_macro_author_queue_json_cli.py`
- `tests/test_macro_runtime_board_json_cli.py`
