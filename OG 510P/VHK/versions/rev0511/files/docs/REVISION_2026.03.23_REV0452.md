# Revision 0452 — checked dispatch and execution ticket now honor the receipt-first selected handoff

Date: 2026-03-23
Revision: 0452

## What changed

- taught the generated-stack `primary_macro_execution_ticket` to read `macro_latest_dispatch_json.sh <macro>` directly instead of depending only on dispatch-history-board summaries
- kept `dispatch_history_workbench` on the execution ticket, but let actual selected-macro receipt evidence decide whether the ticket is `current_dispatch_evidence_available`, `stale_dispatch_evidence_available`, or truly `dispatch_ready`
- mirrored the execution ticket's chosen `selected_handoff` back into the fused `macro_dispatch_gate` payload inside `stack_state_json.sh` whenever the per-macro gate helper is thin or older
- extended the checked-dispatch gate tests so receipt-bearing states now assert a `dispatch_history_workbench`-backed handoff instead of only gate-local readiness bits

## Why it matters

The repo already had honest selected-macro receipt lanes on the work ticket, warm-runtime ticket, next-action helper, and top-level stack state. But the checked-dispatch sibling still drifted: the execution ticket could fall back to `dispatch_ready`, and the fused gate snapshot could hide the chosen receipt-first handoff whenever the helper payload was lightweight.

Revision 0452 makes the checked-dispatch lane tell the same truth as the rest of the resident runtime: when the newest receipt is the sharpest evidence, inspect that receipt first.
