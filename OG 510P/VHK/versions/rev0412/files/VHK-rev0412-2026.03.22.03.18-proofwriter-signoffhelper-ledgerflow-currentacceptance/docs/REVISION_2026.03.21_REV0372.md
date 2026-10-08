# REV0372 — fused stack state now carries the primary macro latest run

## What changed

- Updated the generated `stack_state_json.sh` helper so that when `macro_author_queue_json.sh` names a primary macro, it also opens `macro_latest_run_json.sh <macro>`.
- Added a new fused payload section, `primary_macro_latest_run`, carrying:
  - `macro_name`
  - `latest_run`
  - `latest_run_health`
  - `replay_posture`
  - `next_step`
  - `preferred_entrypoints`
- Added helper diagnostics under `sources.helpers.macro_latest_run_json`, including the selected macro name, verdict, replay posture id, and next-step id.
- Updated `stack_state.sh` so operators can see:
  - `primary_macro_latest_run_macro`
  - `primary_macro_latest_run_verdict`
  - `primary_macro_replay_posture`
  - `primary_macro_latest_run_next_step`

## Why this matters

The fused warm-runtime state had already grown into a strong one-read control plane: readiness, latest run/dispatch, author queue, replay board, runtime board, dispatch history, dispatch catalog, next action, and the primary macro's checked gate.

But the selected macro's own newest matching run still lived behind one more helper. This revision closes that gap so the private-LLM lane can read one fused stack snapshot and see both:

- whether the primary macro should emit through the resident runtime now
- what the primary macro's freshest replay evidence says

That keeps the i3/X11 resident service honest and keeps the LLM lane closer to a true one-read inspect-decide-execute loop.

## Tests

Focused stack tests now cover:

- fused runtime board + primary macro latest-run fields
- fused primary dispatch gate + primary macro latest-run fields
- a dedicated primary-macro-latest-run stack-state scenario
- stack-state helper survival when another helper fails
