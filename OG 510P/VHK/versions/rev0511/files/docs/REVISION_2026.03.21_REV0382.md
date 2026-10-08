# REV0382 — fused selected-macro execution brief

## What changed

- Added `primary_macro_execution_brief` to the fused `stack_state_json.sh` payload.
- The brief is derived entirely from already-loaded selected-macro slices:
  - review queue
  - acceptance ledger
  - checked dispatch gate
  - latest matching run
  - replay/runtime board posture
  - dispatch history
  - command palette
- Added mirrored helper facts so the stack can surface the selected macro's action bias and recommended command without re-reading deeper helpers.
- Updated `stack_state.sh` to print the selected macro's execution-brief summary.

## Why this matters

The fused stack snapshot already carried most of the raw truth for the selected macro, but the caller still had to mentally reconcile that truth to decide what to do next. This revision turns those existing surfaces into one explicit execution brief without adding any new helper hops.

## Decision

Prefer denser one-read control-plane summaries over more helper fan-out. The warm i3/X11 lane should get easier to act on, not broader.

## Tests

- Added focused stack-state coverage for `primary_macro_execution_brief`.
- Kept verification on targeted generated-stack tests because longer pytest runs still intermittently hit sandbox EOFs unrelated to repo assertions.
