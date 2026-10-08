# Revision 0454 — warm-runtime ticket execution fallback

This revision closes the last smaller-surface divergence between the resident-runtime ticket and the checked-dispatch lane.

## What changed

- `warm_runtime_ticket` now mirrors `execution_ticket_handoff` from the checked-dispatch lane.
- When the warm-runtime ticket's directly visible selected-macro handoff is only generic, it now falls back to that checked-dispatch handoff instead of flattening back into a generic execute answer.
- The warm-runtime ticket now records `selected_macro_handoff.selection_basis` so callers can see whether the current lane came from runtime posture directly or from the checked-dispatch fallback.
- `warm_runtime_ticket_json.sh`, `warm_runtime_ticket.sh`, `stack_state_json.sh`, and `stack_state.sh` now surface that basis and the mirrored execution-ticket handoff for observability.

## Why it matters

A healthy resident daemon does not automatically mean the sharper next move is `dispatch now`. When the checked-dispatch lane already knows that the newest receipt should be inspected first, the warm-runtime ticket should say that explicitly instead of making a private LLM or operator rediscover it from a broader stack surface.
