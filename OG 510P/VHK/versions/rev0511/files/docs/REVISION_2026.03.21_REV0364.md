# Revision 0364 - 2026-03-21

## Summary

Checked-dispatch receipts and queue pressure now distinguish contract debt from likely live desktop-state mismatch instead of treating every repeated block as the same kind of trouble.

## What changed

- `macro-dispatch-gate-json` now exposes blocker-class detail in `dispatch_readiness`:
  - `blocker_details`
  - `blocker_class_counts`
  - `primary_blocker_id`
  - `primary_blocker_class_id`
- durable dispatch receipts now preserve that blocker-class projection
- `latest-dispatch-json` now returns the normalized gate blocker class for the newest receipt
- `macro-dispatch-history-board-json` now summarizes blocked receipts by dominant class and exposes `attention_id` on repeated blocked posture
- `macro-author-queue-json` now surfaces more specific repeated-block dispatch attention ids:
  - `repeated_contract_debt`
  - `repeated_desktop_state_mismatch`
  - `repeated_run_proof_gap`
- updated docs and focused CLI tests

## Why

Repeated checked-dispatch blocks were visible, but still too vague. The resident runtime and a private LLM could tell that warm dispatch was failing without being able to tell whether the next move should be recorder/cleanup work, a new replay attempt against changed live window state, or simply restoring matching run proof.

This revision makes that distinction explicit while keeping the i3/X11 warm-runtime lane centered on one session-bound service, thin emit/dispatch wrappers, and receipt-backed observability.
