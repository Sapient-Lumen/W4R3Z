# REV0374 — stack state now carries the primary macro author loop

## What changed

- `stack_state_json.sh` now opens `macro_author_loop_json.sh <primary-macro>` whenever the author queue already names a primary macro.
- The fused stack payload now includes `primary_macro_author_loop` with the selected macro's:
  - source lane
  - recording lane
  - review lane
  - latest-run lane
  - execution lane
  - next step
- `sources.helpers.macro_author_loop_json` now mirrors fast-triage ids:
  - `primary_macro_name`
  - `next_step_id`
  - `runtime_posture_id`
  - `dispatch_gate_decision_id`
  - `dispatch_history_posture_id`
- `stack_state.sh` now prints the selected macro's author-loop macro, next step, runtime posture, and dispatch decision.

## Why this matters

`stack_state_json.sh` already fused the selected macro's checked gate, latest run, and contract, but callers still had to reopen `macro_author_loop_json.sh <macro>` to get the actual per-macro authoring/execution handoff. This revision removes that extra hop so the resident i3/X11 stack snapshot can hand a private LLM one fused selected-macro contract.

## Tests

Focused generated-stack tests cover the new fused author-loop payload and shell summary output.
