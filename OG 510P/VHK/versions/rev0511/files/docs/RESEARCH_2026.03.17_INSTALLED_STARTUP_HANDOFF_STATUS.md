# Research — installed startup handoff status

## What we learned from current Linux docs/tooling

1. `systemctl is-enabled` exposes more than a boolean state; generated and
   transient units are not “enabled” in the normal sense, and invalid/bad states
   are distinct from ordinary disabled units.
2. `systemd-xdg-autostart-generator` exists specifically to turn XDG autostart
   entries into user-service startup objects in desktops that opt into that
   model.
3. The XDG autostart spec treats `Hidden=true` and an unresolved `TryExec=` as
   real reasons an autostart entry should not run.

## Implication for VHK

A Linux-native AHK-like tool should not flatten startup truth into:

- “the unit exists”, or
- “the desktop file exists”

Instead it should capture the effective startup owner from both sides:

- user-unit enablement state
- autostart effectiveness

That is the design basis for rev0309’s installed startup-handoff verdicts.
