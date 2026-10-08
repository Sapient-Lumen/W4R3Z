# Revision 0410 — resident-daemon-bound durable signoff

Date: 2026-03-22
Revision: 0410

## What changed

- extended `src/vhk/project/runtime_acceptance_contract.py` with
  - `resident_runtime_epoch_id`
  - `resident_runtime_contract_digest`
- `current_runtime_acceptance_contract` now reads the cheap busd-written runtime-state cache
  and includes the resident daemon witness in durable signoff proof
- the acceptance ledger/runtime board/author loop now stale an old runtime signoff when the
  current resident daemon epoch or runtime contract changed underneath it
- added focused tests for runtime-acceptance drift caused by resident-daemon changes
- tightened README/architecture/spec/control-plane docs around this resident-runtime contract

## Why it matters

Warm dispatch receipts were already contract-bound and daemon-epoch-aware, but durable signoff
 could still over-trust an old acceptance row when the daemon itself had reloaded or restarted
 before another emit occurred. This revision closes that remaining stale-success hole without
 expanding scope beyond the i3/X11-first resident runtime.
