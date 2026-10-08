# REV0378 — stack state carries selected macro acceptance

## What changed

- `stack_state_json.sh` now extracts the author-queue-selected macro's acceptance/signoff row from the already-loaded project acceptance ledger.
- Added `primary_macro_acceptance` to the fused stack payload.
- Added selected-macro acceptance facts to `sources.helpers.macro_acceptance_ledger_json`.
- `stack_state.sh` now prints the selected macro's acceptance posture and review acceptance counts.

## Why this matters

The fused warm-runtime state already carried the selected macro's gate, latest run, contract, author loop, recorder slice, entrypoints, and board slices. But it still forced callers to rescan the acceptance ledger to answer whether the selected macro had explicit review/runtime signoff. This revision makes acceptance truth part of the one-read stack handoff.

## Focused tests

- selected macro acceptance slice appears in `stack_state_json.sh`
- selected macro acceptance summary appears in `stack_state.sh`
