# Revision 0406 — acceptance contracts for durable signoff

Date: 2026-03-22
Revision: 0406

## What changed

- added `src/vhk/project/runtime_acceptance_contract.py`
- runtime acceptance entries can now carry `proof_contract`
- acceptance ledger now computes a current runtime-acceptance contract and compares durable signoff against it
- runtime board and author loop now expose `current_runtime_acceptance_contract` plus a richer `runtime_signoff` comparison
- legacy posture-only signoffs now remain visible but are marked stale until the ledger stores matching proof state
- `primary_macro_acceptance_ticket` now carries the current proof contract in its ledger-update handoff
- added targeted tests for stale vs current runtime acceptance

## Why it matters

Replay proof and warm dispatch receipts were already contract-bound. Durable signoff needed the same honesty so the resident i3/X11 lane and the private-LLM control loop would stop over-trusting old accepted posture after macro, replay, or dispatch proof drift.
