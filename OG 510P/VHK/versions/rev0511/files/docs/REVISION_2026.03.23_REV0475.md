# Revision 0475 — runtime-signoff readiness and guarded acceptance

This revision tightens durable runtime acceptance for the i3/X11-first resident lane.

## What changed

- added `acceptance.runtime_signoff_readiness` to `macro_author_loop_json.sh <macro>`
- mirrored `runtime_signoff_readiness` into `macro_runtime_board_json.sh`
- signoff readiness now blocks on:
  - active review debt or incomplete acceptance entries
  - non-`warm_dispatch_ready` runtime posture
  - missing/currently stale checked-dispatch receipt evidence
  - replay proof that is not `verified_recent`
  - replay-time X11/i3 target proof that is still partial for selector-bound macros
- `macro-runtime-accept` now refuses to write by default when signoff readiness is blocked
- added `--force` to preserve an explicit override path

## Why

Healthy replay is not enough when the macro claims an explicit X11/i3 selector contract. Durable signoff should freeze a proof state that is current, target-aware, and resident-runtime honest.

## Tests

- acceptance-ledger/runtime-accept tests now cover the new readiness surface
- new coverage blocks default signoff on healthy-but-target-unproven replay
- explicit `--force` coverage preserves intentional operator override
