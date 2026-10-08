# Research: graphical-session target binding

## What current Linux docs/tools teach

- `graphical-session.target` is meant for services that should be active as part
  of the current graphical session.
- systemd's own documentation describes session-specific targets as starting and
  stopping `graphical-session.target` with `BindsTo=graphical-session.target`.
- systemd guidance also distinguishes session-specific graphical services from
  generic user services that do not actually need live display/session context.
- Importing session variables and binding service lifetime are related, but they
  are separate problems.

## Product lesson for VHK

A Linux-native automation product should not flatten these into one vague “user
service” story. A VHK watcher/runtime lane that depends on live display/session
context should say so explicitly and make that lifetime binding verifiable after
install.

## Resulting implementation direction

- emit one session-target policy in the service compose plan
- generate a small probe script that inspects `PartOf`, `BindsTo`, and target
  dependency state via `systemctl --user`
- bind generated VHK-owned session units to `graphical-session.target` when the
  lane is explicitly graphical-session-bound
- keep `default.target` as a reviewable fallback because desktop/session target
  behavior is not perfectly uniform across Linux environments
