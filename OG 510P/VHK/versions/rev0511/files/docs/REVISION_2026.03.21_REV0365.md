# Revision 0365 - dispatch desktop target hints

Revision 0365 tightens the resident i3/X11 dispatch lane again.

What changed:

- `macro-dispatch-gate-json` now carries `dispatch_readiness.desktop_target`
- blocker details can now carry `desktop_target_hint`
- durable dispatch receipts preserve that target hint under `gate.desktop_target`
- `latest-dispatch-json` normalizes and exposes the same target hint
- `macro-dispatch-history-board-json` preserves the latest blocked receipt's target hint instead of collapsing all desktop-state mismatch receipts into one abstract class
- `macro-contract-json` now carries `macro.desktop_target` so the private-LLM lane can see the expected X11/i3 target before it decides how to revise or execute the macro

Why it matters:

- `desktop_state_mismatch` now points at a concrete X11/i3 target hint instead of only saying that some live state was wrong
- the private-LLM lane can stay on one fused control plane when deciding whether to re-run, inspect, or revise recorder/cleanup truth
- the resident runtime keeps a better paper trail without broadening into generic Linux target abstraction work
