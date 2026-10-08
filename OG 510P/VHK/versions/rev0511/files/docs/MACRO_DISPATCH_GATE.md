# Macro dispatch gate

The checked dispatch gate is the per-macro companion to the project-wide dispatch catalog.

Use:

- `vhk macro-dispatch-gate-json <project> <macro>`
- `bin/macro_dispatch_gate_json.sh <macro>` in generated i3/X11 warm-runtime stacks
- `bin/dispatch_macro_checked.sh [--force] <macro> [json-payload]` when you want a stable wrapper that refuses to emit unless the resident-runtime posture is currently safe

The gate keeps the raw `dispatch_macro.sh` wrapper available, but makes the preferred resident-runtime path explicit:

- dispatch now when posture is `warm_dispatch_ready`
- fall back to direct-run when the macro is interactive
- review or stabilize first when recorder debt or unhealthy latest-run evidence is still active

`--force` is intentionally noisy. It preserves the raw emit lane without pretending that stale recorder evidence or interactive prompts became safe.

The gate now also carries `dispatch_readiness.desktop_target`, a compact X11/i3 target hint built from recorder stable-selector evidence and any explicit macro-level selector truth that survives into the contract. When the primary blocker class is `desktop_state_mismatch`, that same target hint is copied into `blocker_details[*].desktop_target_hint` so a private LLM can see which class/title/workspace target was expected before deciding whether to re-run, inspect, or revise recorder/cleanup truth. The gate now also carries `dispatch_readiness.live_probe_hint` and mirrors that under the primary blocker detail when the newest matching run already points at a likely failed live X11/i3 probe (for example `window_event_probe` or `window_wait_probe`). Revision 0368 extends that hint with `live_probe_hint.observation`, a bounded snapshot of the actual failed wait/error observation that made the probe look unhealthy, so `desktop_state_mismatch` can stay actionable without reopening raw run history.


Revision 0369 adds `repair_action` as a first-class sibling to the gate decision. Instead of only saying *why* checked dispatch is blocked, the gate now points at the single best next command for the current X11/i3 truth surface: use direct-run, repair recorder debt, inspect the newest failed desktop-state run, refresh matching run proof, or emit now when the lane is already safe.


Revision 0431 tightens the execute side of that contract for the i3/X11 warm lane. When the gate would otherwise be `dispatch_now`, it now also checks whether `latest_dispatch_json.sh` already holds a current clean receipt for the same macro on the same resident-runtime witness. In that case the gate keeps `can_emit_minimal_payload_now=true` but changes the decision/repair route to `inspect_current_dispatch_evidence` and points at `latest_dispatch_json.sh` first. The product decision is simple: a green gate means the lane is ready, not that the right next move is always another emit.

Revision 0435 applies the same receipt-first rule to stale evidence. When the newest receipt for a macro still belongs to the current warm-runtime lane but its runtime/session/contract witness is no longer current, the checked gate now keeps the macro-local readiness truth visible while switching the decision/repair route to `inspect_stale_dispatch_evidence` with `latest_dispatch_json.sh` as the first command. That keeps the per-macro gate aligned with the selected-macro and top-level helpers: inspect the freshest receipt artifact first, then follow the bounded repair command that receipt already names. Revision 0436 tightens the selected-macro side of that contract too: the generated stack now exposes `macro_latest_dispatch_json.sh <macro>` as the macro-scoped companion to the project-wide `latest_dispatch_json.sh`, and the selected-macro fused stack surfaces now use that macro helper instead of borrowing whichever macro emitted most recently.
