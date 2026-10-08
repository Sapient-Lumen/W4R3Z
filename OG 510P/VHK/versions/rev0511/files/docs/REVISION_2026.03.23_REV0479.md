# Revision 0479 — next-action forced-receipt cutover stays explicit

## What changed

- kept the rev0478 forced-receipt distinction on the top-level resident-control surfaces instead of only macro-scoped ones
- `next_action_json.sh` now projects `clean_replacement_required` and the dedicated `inspect_forced_receipt_before_clean_replacement` cutover on `primary_action`
- `stack_state_json.sh` mirrors those same projected fields in `next_action` and `sources.helpers.next_action_json`
- compact text summaries now print the selected-macro handoff and projected primary-action clean-replacement debt directly
- added a focused render test for the new projection and summary fields

## Why it matters

A current forced checked-dispatch receipt is still useful evidence, but it is not honest clean reuse/signoff proof. The fused resident stack therefore needs to say two things at once:

1. the receipt is current enough to inspect
2. the next honest move is still to replace it with a clean non-forced checked dispatch

Revision 0479 keeps that distinction visible even for callers that only open the top-level next-action or fused stack surfaces.

## Focused verification

- `python -m py_compile src/vhk/cli.py`
- `PYTHONPATH=src pytest -q tests/test_next_action_projection_cli.py`
