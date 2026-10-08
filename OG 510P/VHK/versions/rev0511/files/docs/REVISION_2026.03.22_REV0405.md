# Revision 0405 — dispatch runtime witness via cached daemon epoch

Date: 2026-03-22
Revision: 0405

## What changed

- added `src/vhk/project/runtime_state_cache.py`
- the resident `vhk busd` now writes a lightweight runtime-state cache on
  startup and reload
- generated dispatch receipts now capture `dispatch_runtime_witness` from that
  cache
- `latest-dispatch-json` now compares the newest receipt against the current
  cached daemon epoch/PID/runtime-contract witness
- `macro-dispatch-history-board-json` now surfaces resident-runtime drift
  beside contract drift
- tightened README/architecture/control-plane docs to explain the split between
  live probe truth and cached receipt-epoch truth

## Why it matters

The warm lane already knew whether the resident daemon was reachable and whether
its loaded project state matched disk. But dispatch history still had one blind
spot: a clean receipt from an older daemon instance could look current after a
reload or restart.

This revision keeps the emit path thin while tightening observability. The live
probe still proves current reachability. The runtime-state cache now gives
receipts a cheap resident-daemon fingerprint, so history can say whether a
receipt belongs to the currently loaded busd epoch or only to a previous one.
