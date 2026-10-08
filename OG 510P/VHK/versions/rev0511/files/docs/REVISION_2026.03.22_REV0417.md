# Revision 0417 — latest runtime repair receipts and inspect-first warm tickets

## Summary

This revision makes the resident i3/X11 control plane remember its own bounded
repair attempts. Reload and restart helpers now persist receipts under
`build/runtime_control_receipts/`, the generated stack exposes
`bin/latest_runtime_repair_json.sh`, and the fused warm-runtime ticket will now
switch to inspect-first after a recent failed reload/restart instead of
repeating the same repair blindly.

## Why this revision

Revision 0416 gave the repo a bounded restart helper, but the outcome of that
helper still disappeared after stdout. For a session-bound always-on desktop
automation runtime, that was too forgetful: a private LLM or operator could
reopen `stack_state_json.sh` and still get told to restart or reload again even
though the latest bounded repair had just failed on the current session.

## What changed

- `reload_runtime_json.sh` and `restart_runtime_json.sh` now persist receipts in
  `build/runtime_control_receipts/<action>/history/` and refresh
  `build/runtime_control_receipts/<action>/latest.json`.
- Added `vhk latest-runtime-repair-json` plus generated
  `bin/latest_runtime_repair_json.sh`.
- `stack_state_json.sh` now carries `latest_runtime_repair` and helper metadata
  for the newest bounded reload/restart outcome.
- `warm_runtime_ticket` now avoids blind repeat loops:
  - recent failed restart + restart-class repair =>
    `inspect_runtime_after_failed_restart_attempt`
  - recent failed reload + reload-class repair =>
    `inspect_runtime_after_failed_reload_attempt`
- Updated flagship/runtime docs so the resident control plane is explicitly
  repair-history-aware, not only repair-capable.

## Tests

- added direct CLI coverage for `latest-runtime-repair-json`
- added stack tests for inspect-first routing after recent failed reload/restart
- refreshed generated-stack handoff coverage for the new helper
