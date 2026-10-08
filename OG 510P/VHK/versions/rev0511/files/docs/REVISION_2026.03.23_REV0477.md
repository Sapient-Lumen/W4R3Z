# Revision 0477 — forced checked-dispatch receipts stay visibly provisional

This revision tightens the checked-dispatch receipt lane after rev0476 made forced runtime signoff stay visibly provisional.

## What changed

- latest dispatch surfaces can now classify a current-but-forced receipt as:
  - `current_forced_dispatch_evidence`
- that receipt now preserves:
  - `force_override`
  - `clean_replacement_required`
- runtime-signoff readiness now distinguishes:
  - `blocked_by_forced_dispatch_receipt` — the newest receipt is current enough to inspect, but still depends on a forced checked-dispatch emit and needs a clean replacement before durable signoff is honest
- selected-macro author/runtime/work-ticket surfaces now thread the same receipt debt instead of flattening it into generic current receipt truth

## Why this matters

The flagship i3/X11 resident-runtime lane needs two separate truths:

- a forced receipt can still be useful current evidence to inspect
- a forced receipt is not the same thing as clean reusable proof for durable signoff

Rev0477 keeps those truths separate so a private LLM or operator can see that the warm lane is currently understandable without mistakenly treating it as fully cleared.

## Local validation

- `python -m py_compile src/vhk/cli.py tests/test_latest_dispatch_json_cli.py tests/test_macro_acceptance_ledger_json_cli.py tests/test_primary_macro_work_ticket_cli.py`
- `pytest -q tests/test_latest_dispatch_json_cli.py::test_latest_dispatch_json_classifies_current_forced_dispatch_evidence tests/test_macro_acceptance_ledger_json_cli.py::test_runtime_acceptance_signoff_readiness_blocks_forced_dispatch_receipt tests/test_primary_macro_work_ticket_cli.py::test_primary_macro_work_ticket_threads_forced_dispatch_receipt_handoff`
- `pytest -q tests/test_latest_dispatch_json_cli.py tests/test_macro_acceptance_ledger_json_cli.py tests/test_macro_entrypoints_json_cli.py tests/test_primary_macro_work_ticket_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py tests/test_macro_replay_board_json_cli.py tests/test_i3_busd_stack_cli.py -q`
