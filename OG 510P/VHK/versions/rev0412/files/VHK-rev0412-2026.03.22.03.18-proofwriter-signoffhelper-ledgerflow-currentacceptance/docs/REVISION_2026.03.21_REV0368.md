# Revision 0368 — bounded live-probe observations on the warm i3/X11 lane

This revision tightens the resident-runtime truth surfaces again instead of widening Linux scope.

## What changed

- latest-run health now carries `probe_hint.observation` when the newest matching run preserves a cheap failed live wait/error sample
- `macro_dispatch_gate_json` now carries that same sample under `dispatch_readiness.live_probe_hint.observation`
- blocker details preserve the same observation under `blocker_details[*].live_probe_hint.observation`
- durable checked-dispatch receipts and `latest_dispatch_json` preserve the same observation snapshot
- the observation is intentionally bounded: it keeps the likely failed wait/error sample, not a full raw event log or heavyweight window-tree dump

## Why it matters

The warm i3/X11 lane can now distinguish:
- which blocker class stopped checked dispatch
- which desktop target the macro expected
- which live probe most likely failed
- one bounded sample of what that failed probe actually observed

That keeps the private-LLM execution lane closer to a one-read triage surface without reopening raw run history just to see whether the last miss looked like a workspace mismatch, unmatched window event, or selector miss.

## Tests

- `python -m py_compile src/vhk/cli.py`
- `pytest -q tests/test_latest_run_health_json_cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py`
- `pytest -q tests/test_latest_dispatch_json_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_dispatch_macro_checked_wrapper_blocks_and_forces`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py tests/test_macro_dispatch_catalog_json_cli.py tests/test_macro_entrypoints_json_cli.py tests/test_macro_author_queue_json_cli.py tests/test_macro_runtime_board_json_cli.py`
