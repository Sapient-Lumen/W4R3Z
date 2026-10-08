# REV0371 — fused stack state now carries primary checked-dispatch gate

## What changed

- Updated the generated `stack_state_json.sh` helper to open `macro_dispatch_gate_json.sh <primary-macro>` when the author queue already names a primary macro.
- Added a top-level `macro_dispatch_gate` section to the fused stack payload.
- Added `sources.helpers.macro_dispatch_gate_json` helper diagnostics, including:
  - `primary_macro_name`
  - `decision_id`
  - `repair_action_id`
  - `primary_blocker_class_id`
- Updated `stack_state.sh` so the shell summary prints:
  - `dispatch_gate_primary_macro`
  - `dispatch_gate_decision`
  - `dispatch_gate_repair_action`
  - `dispatch_gate_primary_blocker_class`

## Why this matters

Revision 0370 made the stack-level next-action helper follow the author queue and the selected macro's checked gate. But the fused stack snapshot still forced an extra read whenever a private LLM or operator wanted the actual warm-lane decision for the selected macro.

Revision 0371 removes that extra read. A single `stack_state_json.sh` call now carries project readiness, author-queue triage, replay/runtime/history posture, latest run/dispatch truth, and the selected macro's checked-dispatch gate.

## Tests

Focused stack tests cover:
- generated stack state carrying the primary checked-dispatch gate
- shell summary lines for gate decision / repair action / blocker class
- existing runtime-board, dispatch-catalog, latest-dispatch, and next-action stack behavior
