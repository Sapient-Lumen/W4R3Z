# Revision 0397 — session attachment truth and activation-env repair

This revision makes the warm i3/X11 runtime stricter about what “ready” means.

## What changed

- added `src/vhk/project/session_attachment.py`
- upgraded generated `check_runtime_json.sh` to emit a first-class `session_attachment` witness
- compared the live shell against the systemd/D-Bus activation environment for the bridge variables that matter to the X11/i3 lane
- taught `warm_runtime_ticket` to recommend one bounded repair when the activation environment drifted
- fused `session_attachment` into `stack_state_json.sh` and into helper summary metadata
- added tests for activation-environment drift and session-attachment summarization

## Why this matters

The resident runtime is only truly reliable when:

- the shell is attached to the live X11/i3 desktop
- the warm socket/service are active
- socket-activated restarts will inherit the same desktop session instead of stale login-time variables

This revision makes that contract machine-readable instead of implicit.
