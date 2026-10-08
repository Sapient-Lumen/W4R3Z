# Revision 0478 — forced current receipts get their own disposition lane

This revision sharpens the resident i3/X11 checked-dispatch lane one step further.

## What changed

- `current_forced_dispatch_evidence` no longer reuses the same receipt-stage completion/cutover as a clean current receipt.
- Added a dedicated receipt-stage completion:
  - `forced_receipt_disposition_and_clean_replacement_explicit`
- Added a dedicated receipt-stage cutover / handoff:
  - `inspect_forced_receipt_before_clean_replacement`
- Threaded that distinction through:
  - `macro_latest_dispatch_json.sh <macro>`
  - `macro_author_loop_json.sh <macro>`
  - selected-macro handoff / work-ticket projections
  - dispatch-history workbench fallback synthesis

## Why it matters

Revision 0477 already made forced checked-dispatch receipts visibly provisional. Revision 0478 makes the *next step* equally explicit: a current forced receipt is current enough to inspect, but still not clean enough to look like ordinary receipt reuse or durable signoff readiness.

## Focused validation

- `python -m py_compile src/vhk/cli.py tests/test_latest_dispatch_json_cli.py tests/test_macro_acceptance_ledger_json_cli.py tests/test_primary_macro_work_ticket_cli.py`
- `pytest -q tests/test_latest_dispatch_json_cli.py tests/test_macro_acceptance_ledger_json_cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_macro_entrypoints_json_cli.py -x`
