# REV0304 — startup handoff ownership and duplicate-start guards

This revision tightens another Linux-native service seam: **who actually owns
startup** for a VHK-managed session-service lane.

## What changed

- Added `src/vhk/project/startup_handoff_policy.py`
- `gen-service-compose-pack` now emits `startup_handoff_policy` in plan JSON
- Generated service handoffs now include:
  - `docs/VHK_STARTUP_HANDOFF.md`
  - `verify_startup_handoff.sh`
- Generated install helpers now prefer one startup owner by default:
  - graphical-session-bound user units stay primary when present
  - the XDG autostart bridge remains generated, but installs only as an
    explicit fallback
- Removed redundant `add-wants graphical-session.target ...` wiring from the
  generated install helpers; the unit install metadata already owns that path

## Why it matters

Linux session startup is not only about environment variables or target
lifetime. It also matters whether the same lane gets installed behind multiple
startup hooks at once.

This revision makes one more truth explicit in code and shipped artifacts:

- which startup owner is primary
- which startup owner is only fallback
- how to verify the lane is not duplicated across both paths by default
