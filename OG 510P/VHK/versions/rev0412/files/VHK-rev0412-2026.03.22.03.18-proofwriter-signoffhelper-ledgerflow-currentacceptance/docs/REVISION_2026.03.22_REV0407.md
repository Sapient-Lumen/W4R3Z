# Revision 0407 — session-bound replay proof

Date: 2026-03-22
Revision: 0407

## What changed

- added `src/vhk/project/desktop_session_contract.py`
- `run_start` now records `desktop_session_contract` in the event log
- latest-run health now compares the current shell against the stored X11/i3 session witness
- replay proof now goes stale when a healthy run was proven on a different desktop session
- legacy runs without the new witness remain readable instead of being blanket-downgraded
- added focused tests for session-aware replay staleness and runner event logging

## Why it matters

The flagship product is explicitly session-bound: a healthy run on one i3/X11 session is not automatically current proof for a later shell attached to a different `DISPLAY` or `I3SOCK`. This revision makes the replay lane honest about that without bloating the hot resident-dispatch path or forcing a broad compatibility break on older logs.
