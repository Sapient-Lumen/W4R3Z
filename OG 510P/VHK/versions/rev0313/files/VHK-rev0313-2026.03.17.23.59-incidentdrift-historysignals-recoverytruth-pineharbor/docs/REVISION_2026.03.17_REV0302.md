# REV0302 — session activation sync and explicit user-bus/session wiring

This revision extends the Linux-native service handoff story by adding an explicit
session-activation policy and generated sync helper to `gen-service-compose-pack`.

## What changed

- Added `src/vhk/project/session_activation_policy.py`
- `gen-service-compose-pack` now emits `session_activation_policy` in plan JSON
- Generated service handoffs now include `sync_session_activation_env.sh`
- XDG autostart entries now call the sync helper before starting the VHK-owned
  user unit/socket
- Added generated doc `docs/VHK_SESSION_ACTIVATION.md`
- Updated README/spec/issues planning text to treat activation sync as a first-
  class Linux session concern

## Why it matters

Linux user services often need more than static `environment.d` exports:
`DBUS_SESSION_BUS_ADDRESS`, `XDG_RUNTIME_DIR`, desktop/session identifiers, and
current display variables may need to be imported into activation environments
at session startup. This revision makes that handoff explicit and reviewable
instead of leaving it to desktop-specific shell folklore.
