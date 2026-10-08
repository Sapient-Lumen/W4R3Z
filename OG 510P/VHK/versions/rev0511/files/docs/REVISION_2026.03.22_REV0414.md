# Revision 0414 — live daemon desktop-session truth in the warm-runtime probe

This revision tightens the i3/X11-first warm-runtime control plane around one
specific honesty gap: the live dispatch probe could already prove that the
resident daemon answered, but it still mostly reduced daemon/session truth to
bridge-variable sync. That was not strong enough for a session-bound desktop
automation service.

## What changed

- `summarize_runtime_dispatch_probe(...)` now compares the daemon's own
  `desktop_session_contract` against the current shell's X11/i3 session
  contract.
- `check_runtime_json.sh` now raises `dispatch daemon desktop session drift` as
  a first-class blocker instead of folding that case into generic dispatch-path
  health.
- `warm_runtime_ticket` and the fused `stack_state_json.sh` surface now expose a
  specific repair lane:
  - `status_id = restart_runtime_for_daemon_desktop_session`
  - `route_id = daemon_desktop_session_then_restart`
- Stack helper metadata and `stack_state.sh` now print the daemon desktop-session
  witness result directly (`dispatch_desktop_session_contract_in_sync`,
  `dispatch_daemon_desktop_session_status`,
  `dispatch_daemon_desktop_session_reasons`).
- Added focused tests for both the runtime-probe summary and the generated fused
  stack.

## Why it matters

For the flagship VHK lane, "daemon answered" is not enough. The daemon must be
the right long-lived daemon for the current X11/i3 desktop session. This cut
makes that distinction explicit in the one-read warm-runtime handoff used by
operators, wrappers, and a private LLM.
