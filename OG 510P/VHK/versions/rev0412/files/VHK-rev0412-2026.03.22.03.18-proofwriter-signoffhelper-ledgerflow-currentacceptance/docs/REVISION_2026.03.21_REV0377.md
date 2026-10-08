# REV0377 — fused stack lifts primary-macro board rows

## What changed

- `stack_state_json.sh` now derives direct slices for the author-queue-selected macro from the already-loaded project-wide boards:
  - `primary_macro_replay_board`
  - `primary_macro_runtime_board`
  - `primary_macro_dispatch_history`
  - `primary_macro_dispatch_catalog`
- `sources.helpers.*` metadata now also records the selected macro's board posture/readiness ids, not only the project-wide board primary ids.
- `stack_state.sh` prints the selected macro's replay/runtime/dispatch board posture summary directly.

## Why this matters

The fused stack already carried the selected macro's contract, recorder truth, author loop, latest run, and checked gate. But callers still had to rescan the project-wide replay/runtime/dispatch board arrays to find the selected macro's own row. This revision removes that friction without adding any extra helper processes.

## Tests

Focused stack tests cover a case where the board's own primary macro is **not** the author-queue-selected macro, and verify that the fused stack still exposes the selected macro's replay/runtime/dispatch rows directly.
