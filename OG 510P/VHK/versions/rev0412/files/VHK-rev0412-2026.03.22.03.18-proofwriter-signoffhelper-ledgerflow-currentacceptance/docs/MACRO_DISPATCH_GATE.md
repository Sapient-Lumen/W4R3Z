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
