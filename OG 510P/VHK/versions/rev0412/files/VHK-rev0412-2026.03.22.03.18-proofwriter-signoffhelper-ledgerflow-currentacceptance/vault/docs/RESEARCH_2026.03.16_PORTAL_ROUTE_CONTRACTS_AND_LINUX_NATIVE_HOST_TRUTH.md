# Research — portal route contracts and Linux-native host truth

This pass focused on a practical Linux-native question: once VHK can see live portal interfaces and installed backend manifests, where should that truth show up for operators?

## What upstream docs reinforce

- `xdg-desktop-portal` is a frontend service; most portal implementations come from backend services exposing `org.freedesktop.impl.portal.*` interfaces.
- `portals.conf` is an explicit per-interface routing layer with a precedence order across XDG config/data roots and desktop-specific filenames.
- portal backends are D-Bus-activatable services, so a host can have correct files on disk and still fail live if the activation environment is wrong (`XDG_CURRENT_DESKTOP`, `WAYLAND_DISPLAY`, `PATH`, etc.).
- backend manifests (`*.portal`) advertise `Interfaces`, `DBusName`, and `UseIn`, which means installation reality and desktop-eligibility reality are not the same thing.

## Ecosystem lessons worth preserving in VHK

- wlroots-class sessions still cannot be treated as one generic portal story; alternative backends such as Luminous are appearing and can change the practical route mix for screenshot/screencast/input-capture lanes.
- Hyprland/wlroots-class users still regularly hit RemoteDesktop/InputCapture gaps in downstream apps, which means VHK should keep compositor-native and helper-based fallbacks first-class.
- mixed backend installs remain a real source of routing confusion, so operator-facing packs should not collapse everything to “portal installed”.

## Product conclusion

A Linux-native automation tool needs at least three portal truths visible at once:

1. configured routing (`portals.conf`)
2. installed backend reality (`*.portal` manifests)
3. live frontend availability on D-Bus

That is why this revision adds a `portal_route_contract` surface to host-contract and readiness packs instead of leaving manifest-aware knowledge trapped inside `vhk doctor`.

## Remaining follow-up

The next route-contract consumers should be setup/native-install/release artifacts, so packaged handoffs preserve the same truth model instead of flattening back into package checklists.
