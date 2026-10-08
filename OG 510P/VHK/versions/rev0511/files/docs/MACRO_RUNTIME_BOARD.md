# Macro runtime board

`macro_runtime_board_json.sh` is the project-wide **execution-posture board** for
VHK's flagship i3/X11 warm-runtime lane.

It now answers three related questions in one read:

1. which macros are actually fit for the resident runtime now
2. which receipt/evidence lane should an operator or private LLM inspect next
   before re-emitting on that warm lane
3. what one bounded next action should be preferred for that macro right now

Revision 0442 makes that handoff a real upstream control-plane input, not just board-local commentary: `next_action_json.sh` now reuses the runtime-board handoff when the narrower selected-macro gate/work-ticket helpers are missing or only generic, and `stack_state_json.sh` now mirrors that same selected-macro handoff explicitly.

## What the board is for

Use the runtime board when the goal is to choose or verify a practical execution
path for one macro without reopening the entire per-macro author loop first.

It keeps the X11/i3-first priorities explicit:

- prefer the resident session-bound runtime for cheap non-interactive dispatch
- keep direct-run explicit for prompt-heavy or interactive macros
- keep recorder/review debt visible when stabilization should happen before fast
  warm dispatch
- keep the newest macro-scoped dispatch receipt on the same board so posture and
  receipt evidence do not drift apart

## Key fields

Per macro, the board now carries:

- `runtime_posture`: `warm_dispatch_ready`, `warm_dispatch_candidate`,
  `direct_run_only`, or `stabilize_first`
- `dispatch_history`: the compact dispatch-history summary and posture already
  computed for that macro
- `dispatch_attention`: the shorter current dispatch/receipt handoff extracted
  from dispatch history
- `receipt_observability.macro_latest_dispatch`: the macro-scoped newest receipt
  lane (`macro_latest_dispatch_json.sh <macro>`)
- `receipt_observability.project_latest_dispatch`: the project-global newest
  receipt lane (`latest_dispatch_json.sh`)
- `preferred_entrypoints.latest_dispatch`: the macro-scoped receipt surface to
  inspect before reopening generic repair or re-dispatch work
- `runtime_handoff`: a bounded next-step handoff that collapses posture +
  receipt/attention truth into one action (`checked_dispatch_ready`,
  `inspect_receipt_lane`, `refresh_replay_proof_before_dispatch`,
  `direct_run_required`, or `stabilize_before_runtime_dispatch`)

At project scope, the board also mirrors:

- `receipt_surfaces.project_latest_dispatch`
- `receipt_surfaces.primary_macro_latest_dispatch`
- `receipt_surfaces.macro_latest_dispatch_template`

That gives a private LLM one project-wide execution board that can still point
at the selected macro's own newest receipt even when some other macro emitted
more recently.

## Non-claims

The runtime board is still advisory execution posture, not proof that the next
replay or dispatch will succeed. It keeps the warm lane practical and
observable; it does not replace the checked gate, replay board, or latest-run
proof.

## Why `runtime_handoff` exists

The runtime board already had enough data to let a caller infer the next move,
but a private LLM still had to choose between posture, receipt attention, and
entrypoints. `runtime_handoff` makes that decision explicit without pretending
that the board is stronger than the checked gate or replay proof.

For warm-dispatch-ready macros, the handoff prefers `dispatch_macro_checked.sh`
unless the newest same-macro receipt is already the more useful artifact to read
first. For candidate macros it prefers replay-proof refresh, for prompt-heavy
macros it stays on direct-run, and for unstable macros it stays on the
recorder/cleanup lane.

## Revision 0460: runtime board now mirrors receipt cutover truth

`macro_runtime_board_json.sh` now mirrors selected-macro receipt cutover truth from the lower receipt surfaces. Each macro item can carry `stage_completion` and `execution_cutover`, macro-scoped receipt observability now includes receipt-disposition and redundant-dispatch-risk flags, and `runtime_handoff` echoes the same cutover fields so the resident runtime can prefer inspect-or-signoff over another warm emit when evidence is already sufficient.
