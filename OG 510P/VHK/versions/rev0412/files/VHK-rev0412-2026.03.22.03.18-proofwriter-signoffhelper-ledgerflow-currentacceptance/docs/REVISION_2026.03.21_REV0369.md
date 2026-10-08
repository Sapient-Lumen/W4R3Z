# Revision 0369 — gate-level repair actions for the warm i3/X11 lane

This revision makes the resident-runtime control plane more actionable instead of merely more descriptive.

## What changed

- checked-dispatch projection now carries a structured `repair_action`
- `macro_dispatch_gate_json` exposes that action at both top level and under `dispatch_readiness.repair_action`
- `macro_author_loop_json` now embeds the same `repair_action` under `execution.dispatch_gate`
- `latest_dispatch_json` now preserves or derives `gate.repair_action` from durable receipts
- generated checked/raw receipt writers now persist `repair_action` when the gate provides it
- `macro_author_queue_json` now reuses gate-level `repair_action.command` when repeated warm-runtime pressure pulls a macro upward

## Repair-action taxonomy

The resident lane now emits one concrete next move instead of only blocker classes:

- `ready_to_dispatch`
- `use_direct_run`
- `repair_recorder_contract`
- `inspect_live_desktop_target`
- `refresh_matching_run_proof`
- fallback `inspect_dispatch_gate`

## Why it matters

The private-LLM lane already knew:
- whether checked dispatch was safe now
- which blocker class stopped it
- which X11/i3 target was expected
- which live probe most likely failed
- one bounded failed-probe observation sample

But it still had to infer the actual next command from that evidence. Revision 0369 closes that gap: the same per-macro gate/author-loop surface now says which single command best advances the lane next.

That also makes project-wide queue pressure more useful. Repeated blocked dispatch or unresolved forced overrides now surface a repair command instead of only bouncing back to a generic author-loop reread.

## Tests

- `python -m py_compile src/vhk/cli.py`
- `pytest -q tests/test_macro_dispatch_gate_json_cli.py`
- `pytest -q tests/test_latest_dispatch_json_cli.py`
- `pytest -q tests/test_macro_entrypoints_json_cli.py`
- `pytest -q tests/test_macro_author_queue_json_cli.py`
- `pytest -q tests/test_macro_dispatch_history_board_json_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py`
- `pytest -q tests/test_macro_dispatch_catalog_json_cli.py`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_dispatch_macro_checked_wrapper_blocks_and_forces`
- `pytest -q tests/test_i3_busd_stack_cli.py::test_generated_dispatch_receipt_tracks_emitted_checked_dispatch`
