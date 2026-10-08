# Revision 0356 — checked dispatch gate for the warm runtime

This revision closes the next resident-runtime control-plane gap after the dispatch catalog.

## What changed

- added `vhk macro-dispatch-gate-json <project> <macro>`
- generated `bin/macro_dispatch_gate_json.sh <macro>`
- generated `bin/dispatch_macro_checked.sh [--force] <macro> [json-payload]`
- extended macro contracts, entrypoints, runtime board, and dispatch catalog with checked-dispatch wrapper metadata
- tightened docs so the flagship private-LLM/runtime flow is now:
  1. author queue for project triage
  2. runtime board for posture
  3. dispatch catalog for project-wide thin-dispatch discovery
  4. dispatch gate for one macro right before emit
  5. checked dispatch wrapper for the default resident-runtime actuation lane

## Why it matters

VHK already knew which macros were probably dispatchable. This revision turns that into a real fail-fast runtime contract so the warm lane can say *do not emit yet* with an explicit reason instead of silently depending on the raw bus wrapper.
