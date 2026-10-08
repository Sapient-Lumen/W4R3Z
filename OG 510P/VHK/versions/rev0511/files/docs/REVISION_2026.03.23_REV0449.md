# Revision 0449 — dispatch-history workbench parity

This revision carries the bounded LLM/operator contract into the receipt-history lane.

## What changed

- `macro_dispatch_history_board_json.sh` now emits a per-macro `llm_workbench`.
- The board root now mirrors `primary_macro_llm_workbench` plus summary fields for source/mode/command/surface.
- `stack_state_json.sh` now mirrors `primary_macro_dispatch_history.llm_workbench` and top-level `primary_macro_dispatch_history_workbench`.
- `stack_state.sh` now prints the selected macro dispatch-history workbench source/mode/command.
- `warm_runtime_ticket_json.sh` now extracts `primary_macro_dispatch_history` and `primary_macro_dispatch_history_workbench`.
- `warm_runtime_ticket.sh` now prints the selected macro dispatch-history workbench source/mode/command/surface.

## Why it matters

The receipt-history lane is now a first-class bounded loop instead of a posture-only observability board. A private LLM can open the warm-runtime ticket or fused stack and recover both:

- the chosen runtime/author-loop handoff
- the sharper receipt-history inspection loop for the selected macro

That keeps the resident i3/X11 service, checked-dispatch receipts, recorder cleanup, and source editing on one coherent control-plane story.
