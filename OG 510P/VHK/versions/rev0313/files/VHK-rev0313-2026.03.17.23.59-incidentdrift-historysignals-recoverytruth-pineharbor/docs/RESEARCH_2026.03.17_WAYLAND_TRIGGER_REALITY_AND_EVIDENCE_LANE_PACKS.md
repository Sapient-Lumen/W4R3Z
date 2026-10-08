# Research notes: Wayland trigger reality and evidence-lane review packs

Date: 2026-03-17

## Why this note exists

VHK keeps trying to answer the same hard Linux-native question honestly: which
part of the automation story belongs in a runner, which part belongs in a
permissioned portal lane, and which part belongs in a remapper/helper lane?

Current upstream docs still reinforce three product lessons.

## 1) Global shortcuts are real now, but still desktop-shaped

The XDG GlobalShortcuts portal explicitly supports creating a session, binding
shortcuts, and receiving activation/deactivation signals, so VHK is right to
model portal-first triggers as a first-class Linux-native route rather than a
future fantasy. GNOME 48 also now documents full support for global shortcuts,
with permission gating and Settings-side removal.

Sources:
- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html
- https://release.gnome.org/48/developers/
- https://release.gnome.org/48/

### Product issue that follows

VHK should keep treating GlobalShortcuts as one reviewed lane, not the whole
answer. Operators still need proof about *which* desktop lane is under review,
which is exactly why evidence-lane context must survive into session-fit and
host-contract artifacts.

## 2) xremap keeps validating the app-aware remapper lane

xremap still presents itself as a Linux remapper that supports Wayland,
application-specific remapping, command triggers, and multiple compositor
features (GNOME, KDE, wlroots, Hyprland, Niri, COSMIC). That means VHK should
keep investing in reviewable remapper/export lanes instead of trying to absorb
all hotkey ownership into the Python runner.

Source:
- https://github.com/xremap/xremap

### Product issue that follows

VHK should continue to separate:
- permissioned portal-first triggers
- remapper-owned app-aware trigger lanes
- runner-owned macro/runtime logic

Those are not interchangeable proof surfaces, so support artifacts need to keep
the chosen evidence lane explicit.

## 3) libei/EIS still argues for a distinct compositor-mediated input lane

The current libei documentation still frames emulated input as a client/server
model aimed at the Wayland stack, with EIS implemented by the compositor and an
optional `liboeffis` helper for D-Bus communication with the XDG RemoteDesktop
portal. That supports VHK's existing decision to keep portal/EIS-style input
routes distinct from uinput/remapper lanes.

Source:
- https://libinput.pages.freedesktop.org/libei/

### Product issue that follows

VHK should keep treating compositor-mediated input, portal-mediated input, and
raw-device/remapper lanes as different evidence targets with different host
contracts and review expectations.

## Concrete repo follow-through

The most immediate gap exposed by this research was not another new backend. It
was proof-context loss: host/session review packs could be regenerated without
carrying the operator's chosen evidence lane.

That is now the right near-term fix:
- preserve `--evidence-lane` through session-fit and host-contract packs
- show selected lane + fit in generated docs/JSON
- keep review scripts pinned to the same explicit lane on rerun
