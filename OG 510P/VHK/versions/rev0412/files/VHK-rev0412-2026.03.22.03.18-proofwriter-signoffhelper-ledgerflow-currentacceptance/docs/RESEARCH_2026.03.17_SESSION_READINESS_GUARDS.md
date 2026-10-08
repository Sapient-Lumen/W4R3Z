# Research — session readiness guards

Current Linux service guidance keeps teaching the same lesson: target lifetime,
startup ownership, and activation environment are not the whole story.

## What current tooling/docs are teaching

- `systemd.service` documents `ExecCondition=` as a hybrid condition/pre-start
  mechanism: an exit status from 1 to 254 skips the remaining start commands
  without marking the unit failed.
- `graphical-session.target` is specifically about graphical session lifetime,
  not generic user-login truth.
- `dbus-update-activation-environment --systemd` and `environment.d` solve
  activation/export problems, but neither one proves that the live session is
  currently ready for a graphical automation lane.
- XDG autostart is a desktop startup contract, not proof that every launched
  process is already in the correct runtime/session state.

## Product lesson for VHK

A Linux-native AHK-like system should not flatten “installed”, “enabled”, and
“session-ready” into one state. The generated service handoff now keeps those
states separate by shipping an explicit readiness probe and using it in the
owned user unit as an `ExecCondition=` gate.
