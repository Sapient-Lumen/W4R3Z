# Revision 0453 — top-level selected-macro fallback now reuses the checked-dispatch handoff

Date: 2026-03-23
Revision: 0453

## What changed

- `primary_macro_work_ticket` now carries `execution_ticket_handoff` alongside the already-chosen `selected_macro_handoff`
- `next_action_json.sh` and `next_action.sh` now fall back to that checked-dispatch handoff when the visible selected-macro ticket only offers a generic dispatch/LLM answer
- helper metadata and text summaries now mirror the execution-ticket fallback handoff fields so the resident control plane can expose both the chosen surface and the sharper checked-dispatch fallback
- added focused tests for a generic work-ticket handoff that now correctly falls back to the execution ticket's receipt-first lane

## Why it matters

Revision 0452 made the checked-dispatch lane itself honest about receipt-first truth, but the smallest selected-macro ticket could still flatten that back into a generic `dispatch_selected_macro` answer. Revision 0453 keeps the warm control plane aligned: when the checked-dispatch ticket already knows the sharper receipt/runtime lane, the top-level helpers reuse that truth instead of making a private LLM rediscover it from sibling surfaces.
