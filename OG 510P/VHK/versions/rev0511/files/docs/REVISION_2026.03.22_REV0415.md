# Revision 0415 — session-honest reload receipts for the warm runtime

This revision tightens one narrow but important control-plane surface on the
flagship i3/X11 lane: `reload_runtime_json.sh` no longer treats “project
contract refreshed” as equivalent to “resident daemon now belongs to the current
desktop session.”

## What changed

- `summarize_runtime_reload_receipt(...)` now compares the post-reload daemon
  `desktop_session_contract` against the current shell's desktop-session
  contract.
- reload receipts now expose:
  - `after_desktop_session_contract_in_sync`
  - `after_daemon_desktop_session_contract_status`
  - `recommended_followup`
- when reload refreshed project state but the daemon still belongs to another
  X11/i3 session, the receipt now returns:
  - `status = reload_observed_but_daemon_desktop_session_drift`
  - `recommended_followup.id = restart_runtime_for_daemon_desktop_session`
  - `recommended_followup.route_id = daemon_desktop_session_then_restart`
- the generated `bin/reload_runtime_json.sh` helper now carries the current
  shell desktop-session witness plus a bounded restart command for the resident
  service.
- updated the top-level docs so the warm-runtime story says reload receipts are
  session-honest, not only contract-honest.

## Why it matters

For VHK's always-available X11/i3 lane, a reload is useful only if the daemon
that survives it is still the right daemon for the current desktop session.
This cut makes the reload helper safe to use in the private-LLM author loop:
“reload observed” no longer silently masks “wrong daemon session.”
