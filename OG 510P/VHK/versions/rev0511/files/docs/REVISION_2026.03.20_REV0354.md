# REV0354 — acceptance ledger for recorder/runtime signoff

This revision adds a durable project acceptance ledger for the flagship i3/X11 warm-runtime lane.

## What changed

- added `vhk macro-acceptance-ledger-json <project>`
- generated `bin/macro_acceptance_ledger_json.sh` in the flagship warm-runtime stack
- added `review/macro_acceptance.yaml` as the checked-in signoff lane for recorder/runtime debt
- taught the author loop, author queue, runtime board, review queue, next-action path, and fused stack state to distinguish active debt from explicitly accepted debt
- extended generated stack metadata and docs so a private LLM can find the signoff lane directly

## Why this cut matters

Before this revision, VHK could infer recorder/runtime posture but could not record that a concern had already been reviewed and intentionally accepted. That forced the resident runtime and a private LLM to keep re-triaging the same stale/exact/runtime concerns as if they were always active.

The acceptance ledger does not hide raw truth. It adds a durable checked-in signoff surface so VHK can say both:

- here is the full recorder/runtime debt
- here is the subset that still counts as active debt on the flagship warm lane

## Validation

Focused tests cover:

- ledger normalization of accepted vs incomplete review/runtime signoff
- suppression of accepted review debt in author queue and runtime board without erasing raw debt
- generated stack exposure of acceptance-ledger helpers and fused state
- stack-state handling of accepted review debt counts
