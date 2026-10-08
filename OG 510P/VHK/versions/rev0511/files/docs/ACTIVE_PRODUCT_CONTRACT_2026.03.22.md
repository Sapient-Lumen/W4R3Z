# Active product contract — 2026.03.22

## What VHK is

VHK is an **i3/X11-first desktop automation runtime** and the execution core for a future **Pulover-style macro studio for Linux**.

## What is tier 1

Only one lane is primary:

- desktop: **i3 on X11**
- runtime: **session-bound long-lived user service**
- dispatch path: **thin emit -> resident busd -> macro execution**
- authoring loop: **record -> cleanup -> replay -> inspect -> refine**
- advanced caller: **private LLM operating against machine-readable control-plane surfaces**

## What must stay true

1. **Resident-runtime honesty beats convenience.**
   The warm path is only healthy when the live daemon is attached to the current X11/i3 session, serving the current project contract, and answering within the fast-path latency budget.

2. **Recorder evidence is product, not scaffolding.**
   Window context, selector shape, relative coordinates, and cleanup hints are first-class review inputs.

3. **Replay proof must stale honestly.**
   Source edits, sidecar drift, desktop-session drift, and resident-runtime drift all invalidate old proof.

4. **The private-LLM path must be one-read.**
   The generated stack should answer: what macro is selected, what file is editable, what stage is blocking, what the next bounded command is, and how to verify the result.

5. **Secondary lanes stay secondary.**
   Wayland, portals, and app-native adapters stay only when they directly strengthen the X11/i3 flagship lane.

## Control-plane surfaces that matter most

Read these first:

- `bin/llm_session_ticket_json.sh`
- `bin/llm_session_ticket.sh`
- `bin/stack_state_json.sh`
- `bin/next_action_json.sh`
- `bin/primary_macro_work_ticket_json.sh`
- `bin/warm_runtime_ticket_json.sh`
- `bin/macro_author_loop_json.sh <macro>`
- `bin/macro_dispatch_gate_json.sh <macro>`
- `bin/macro_latest_dispatch_json.sh <macro>`

`macro_author_loop_json.sh <macro>` is the direct-macro twin of the selected-macro work ticket. It should expose the same bounded edit/review/execute contract when one macro is already in focus: editable source, recorder/cleanup/replay review commands, receipt/runtime handoffs, and a top-level `llm_workbench` object that tells a private LLM exactly what to inspect, edit, execute, and verify next.

`next_action_json.sh` and `stack_state_json.sh` should also project one chosen `primary_macro_llm_workbench`. The control plane should not make the caller rediscover whether the tighter next hop is the selected-macro ticket or the direct per-macro author loop. Prefer the selected-macro ticket while review debt is still active; prefer the direct author loop once the selected macro is already in an execution-stage receipt/runtime lane.

`macro_dispatch_history_board_json.sh` should now do the same for the receipt-history lane: each macro row should expose a bounded `llm_workbench`, and the fused stack / warm-runtime ticket surfaces should mirror `primary_macro_dispatch_history_workbench` so receipt-first inspection can stay explicit even when the caller only opens the smaller resident-runtime helpers.

## Selected-macro work ticket contract

`primary_macro_work_ticket_json.sh` is the smallest flagship control-plane surface for the selected macro.
It should expose:

- the current blocking stage
- the bounded next command
- the editable source path
- the minimum useful author/review/execute entrypoints
- current probe/receipt/runtime handoffs when they are sharper than generic execution advice
- an explicit `llm_workbench` object that tells a private LLM what to inspect first, where to edit, how to execute when clear, and what condition ends the current loop

## Non-goals for the active lane

These may exist in the repo, but they are not the default product story:

- generic Linux parity for every compositor
- portal-first activation as the main trigger model
- app-native adapters as the roadmap center
- broad Wayland-native claims

## Revision 0448 refinement: resident-runtime surfaces must carry the same bounded LLM lane

The runtime board and warm-runtime ticket are not only daemon-health surfaces; they are also top-level private-LLM/operator entrypoints. From this revision onward:

- `macro_runtime_board_json.sh` should mirror one per-macro `llm_workbench` copied from `macro_author_loop_json.sh <macro>` with explicit `source_id` and `source_command`.
- `warm_runtime_ticket_json.sh` should mirror the fused stack's chosen `primary_macro_llm_workbench` instead of forcing the caller to reopen `next_action_json.sh` or `stack_state_json.sh` just to recover the bounded edit/inspect/execute lane.
- Human summaries for runtime surfaces should print the chosen workbench mode/command/surface when available so operators can stay on the resident lane without re-parsing bigger JSON helpers.


## Revision 0450 refinement: small resident helpers must name the sharper selected-macro lane

The resident-runtime entry surfaces now expose an explicit `selected_macro_handoff` instead of forcing the caller to infer whether the next hop is execution, runtime repair, or receipt inspection.

From this revision onward:

- `primary_macro_work_ticket_json.sh` should carry `selected_macro_handoff` and `dispatch_history_workbench` together, so the ticket can say "inspect the newest selected-macro receipt first" when stale resident evidence is the real blocker.
- `warm_runtime_ticket_json.sh` should mirror that same chosen handoff for the selected macro instead of collapsing back to `execution_ticket` whenever the daemon itself is healthy.
- `warm_runtime_ticket_json.sh` should also expose when it had to fall back to the checked-dispatch `execution_ticket_handoff`, because a healthy resident daemon is not enough reason to hide sharper receipt-first truth from the caller.
- `next_action_json.sh` and `stack_state_json.sh` should also project that same choice as `primary_macro_selected_handoff`, so the absolute top-level resident surfaces can reopen the sharper receipt/runtime/author lane without extra inference.
- when the visible selected-macro work ticket is thin or only generic, it should still carry an `execution_ticket_handoff`, and `next_action_json.sh` should prefer that checked-dispatch fallback whenever it points at a sharper receipt/runtime lane than the generic ticket recommendation.
- `next_action.sh` and `stack_state.sh` should print the same selected-handoff source, mode, surface, and command so shell-first operators can see the chosen lane without opening JSON.
- stale selected-macro dispatch evidence should outrank generic runtime-signoff repair in the selected-macro work ticket, because resident-runtime truth is the sharper next decision than ledger cleanup when the newest receipt is already telling us what changed.
- `macro_dispatch_gate_json.sh` and `primary_macro_execution_ticket` should mirror that same receipt-first choice instead of collapsing back to generic checked-dispatch readiness; if the newest selected-macro receipt is still the sharpest truth, the checked-dispatch lane should point at `macro_latest_dispatch_json.sh <macro>` before offering another emit.
