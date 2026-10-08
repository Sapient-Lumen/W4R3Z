# Research: session activation sync and user-bus environment

## What current Linux docs/tools teach

- `environment.d` config is for environment passed to services started by the
  systemd user instance.
- `dbus-update-activation-environment --systemd` updates the environment used by
  both D-Bus session services and `systemd --user` activation.
- `graphical-session-pre.target` is specifically described as containing
  services that set up environment or global configuration for a graphical
  session.
- XDG Desktop Portal presents itself as a session service, so session/user-bus
  environment correctness matters for portal-routed surfaces too.

## Product lesson for VHK

VHK should not stop at static user-unit files plus `environment.d`. A Linux-
native automation product also needs an explicit activation-sync story for live
session variables such as:

- `DBUS_SESSION_BUS_ADDRESS`
- `XDG_RUNTIME_DIR`
- `XDG_CURRENT_DESKTOP`
- `XDG_SESSION_TYPE`
- `WAYLAND_DISPLAY` / `DISPLAY`
- `XAUTHORITY` where X11 lanes still matter

## Resulting implementation direction

- keep the variable set narrow and reviewable
- generate one sync helper in the service handoff
- run that helper from the autostart bridge before starting the VHK-owned unit
- document this separately from authority ownership, because ownership and
  activation timing are related but distinct Linux concerns
