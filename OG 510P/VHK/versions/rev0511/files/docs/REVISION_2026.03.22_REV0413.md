# Revision 0413 — daemon session witness in cached warm-runtime proof

Date: 2026-03-22
Revision: 0413

## What changed

- the resident `busd` runtime-state cache now records the daemon's own `desktop_session_contract`
- internal runtime-probe acknowledgments now carry that same daemon-session witness explicitly
- cached runtime-witness comparison now detects resident-daemon session drift, not only epoch/PID/contract/watcher drift
- latest-dispatch inspection now reports `runtime_desktop_session_drift` when an old receipt came from a daemon bound to a different X11/i3 desktop session than the daemon that is live now
- rewrote the top-level README to make the i3/X11-first product lane and active control-plane surfaces easier to read in one pass
- added focused tests for runtime-state-cache session witness round-trip and latest-dispatch session-drift reporting

## Why it matters

Before this revision, the cheap resident-runtime witness could prove that a
receipt belonged to an older daemon epoch, PID, watcher set, or project
contract, but it could not cheaply prove that the daemon itself had crossed onto
another X11/i3 desktop session. The live runtime probe could catch that, but the
cached witness used by dispatch history stayed slightly under-specified.

This revision closes that gap. Warm-dispatch history can now say not just “that
receipt came from another daemon instance,” but also “that receipt came from a
resident daemon attached to another desktop session.” That keeps the fast proof
lane aligned with the repo's session-bound runtime model.
