## Revision 0398 — runtime-side session proof for the warm i3/X11 daemon

This revision closes the next warm-runtime truth gap on the i3/X11 lane.
`check_runtime_json.sh` no longer stops at shell-side session evidence plus
systemd activation-environment drift. It now also inspects the running busd
service's `MainPID`, reads `/proc/<pid>/environ`, and compares that startup
process environment against the live shell.

Concrete changes:

- added `summarize_runtime_service_environment()` in `src/vhk/project/session_attachment.py`
- extended `summarize_session_attachment()` so a running service started in the
  wrong desktop session becomes an explicit `service_session_drift` blocker
- generated `check_runtime_json.sh` now captures:
  - service `MainPID`
  - a `service_environment_probe`
  - `runtime_service_environment` inside `session_attachment`
- `warm_runtime_ticket` now has a bounded repair for that case:
  `restart_runtime_in_live_session`
- fused helper metadata and `stack_state.sh` now surface
  `runtime_service_environment_status`
- added tests for service-session drift and the new warm-runtime repair route

Concrete win:

The resident control plane can now distinguish three different states that used
to blur together:

1. the live shell is graphical
2. the activation environment is now aligned for future socket activations
3. the *currently running* resident daemon is still attached to the wrong
   X11/i3 session and needs a restart there

That makes the i3/X11 warm-runtime lane more honest for both operators and a
private LLM.
