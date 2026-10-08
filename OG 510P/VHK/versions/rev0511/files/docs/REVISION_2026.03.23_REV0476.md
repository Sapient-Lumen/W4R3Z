# Revision 0476 — forced-signoff visibility on the resident X11/i3 lane

This revision tightens the durable runtime-signoff story after rev0475 introduced readiness gating and a `--force` escape hatch.

## What changed

- runtime-acceptance rows now persist:
  - `force_override`
  - `forced_readiness_status_id`
  - `forced_readiness_summary`
- normalized `runtime_signoff` now distinguishes:
  - `accepted` — clean, current, non-forced durable signoff
  - `forced_review` — proof contract matches, but the row was written with `--force` and still needs clean replacement
- acceptance-ledger summary now counts `forced_runtime_acceptance_macro_count` separately
- author/runtime surfaces preserve the same `forced_review` signal so a private LLM can keep that debt visible

## Why this matters

A deliberate operator override is still valid, but it should never silently decay into what looks like normal, current, clean acceptance. On the flagship i3/X11 resident-runtime lane, a forced signoff is a temporary audit marker that says “this was accepted under protest; replace it with a clean signoff once replay proof, target proof, receipt truth, and resident-runtime posture really agree.”

## Local validation

- `python -m py_compile src/vhk/cli.py tests/test_macro_acceptance_ledger_json_cli.py`
- `pytest -q tests/test_macro_acceptance_ledger_json_cli.py`
- `pytest -q tests/test_macro_runtime_board_json_cli.py tests/test_primary_macro_work_ticket_cli.py tests/test_macro_entrypoints_json_cli.py`
