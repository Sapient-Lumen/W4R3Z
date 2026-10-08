# REV0305 — session readiness guards and live-session proof

This revision adds one more Linux-native operational truth to the VHK
session-service handoff: **a unit can be installed correctly and still be
started in the wrong session context**.

## What changed

- Added `src/vhk/project/session_readiness_policy.py`
- `gen-service-compose-pack` now emits `session_readiness_policy` in plan JSON
- Generated service handoffs now include:
  - `docs/VHK_SESSION_READINESS.md`
  - `verify_session_readiness.sh`
- Generated VHK-owned user units now use `ExecCondition=` to gate startup on
  live session prerequisites instead of assuming every login path is ready
- The XDG autostart bridge now checks readiness before it asks `systemctl --user`
  to start the owned unit/socket

## Why it matters

Linux-native automation lives at the boundary between installed artifacts and
live sessions. This revision keeps VHK honest about that boundary by making the
readiness contract reviewable in docs, JSON, probes, and generated unit files.
