# Revision 0409 — dispatch-bound runtime signoff

Date: 2026-03-22
Revision: 0409

## What changed

- durable runtime acceptance now binds to warm-dispatch evidence as well as replay/runtime posture
- `runtime_acceptance_contract` now carries `dispatch_history_posture_id` and `dispatch_history_attention_id`
- `macro_acceptance_ledger_json`, `macro_runtime_board_json`, and `macro_author_loop_json` now stale an old runtime signoff when the current warm-dispatch lane has changed underneath it
- added focused tests for dispatch-history-driven signoff drift

## Why it matters

A private LLM or operator should not treat an old "accepted" runtime posture as evergreen when the resident warm-dispatch lane has since gone session-stale, runtime-stale, contract-stale, or newly blocked. This revision makes durable signoff follow the current warm bus lane instead of only replay posture and static macro contract truth.
