# Revision 0404 — contract-bound dispatch receipts

Date: 2026-03-22
Revision: 0404

## What changed

- added `src/vhk/project/dispatch_receipt_contract.py`
- generated dispatch receipt writers now capture a `dispatch_receipt_contract` alongside each receipt
- `latest-dispatch-json` now compares the newest receipt against the current macro/dispatch contract
- `macro-dispatch-history-board-json` now exposes `latest_receipt_contract_status` and marks drifted receipts as `dispatch_receipt_contract_stale`
- added targeted tests for stale dispatch receipts after macro edits

## Why it matters

Warm dispatch history should be subject to the same contract discipline as replay proof. A clean emit from yesterday should not keep counting as current resident-runtime evidence after the operator or private LLM changes the macro, recorder sidecar, selector, payload contract, or bus event.
