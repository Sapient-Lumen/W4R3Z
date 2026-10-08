# Research notes: target desktops and route comparison

These notes explain why VHK now compares route decisions across hypothetical
Linux target profiles instead of assuming one universal desktop story.

## Product lessons carried into the target-route pack

- X11-style automation remains materially different from Wayland-native desktop
  automation, so trigger ownership should not be flattened into one route.
- Portal-managed shortcut and capture paths behave like explicit session/config
  surfaces, not like timeless process-local hooks.
- Remapper/helper stacks remain realistic primary routes on some Wayland desktop
  families because low-level input ownership and app-context plumbing vary.
- Launcher/palette entrypoints remain the one universal escape hatch across
  every target profile.

## Current target profiles

- `x11-desktop`: native WM/compositor bindings are the cleanest first trigger
  surface; portals are not treated as the reference lane.
- `gnome-wayland`: model a portal-first release story while keeping launcher
  fallback mandatory.
- `kde-wayland`: model a portal-friendly Wayland story while still keeping
  desktop-native trigger surfaces visible.
- `wlroots-wayland`: treat remapper/helper seams as realistic primary routes for
  trigger/input ownership and keep portal routes secondary.

## Intentional limits

This pack is a planning artifact, not a live proof artifact.

It should inform:

- release notes
- support claims
- operator/deployment guidance
- which desktop family should become the first-class reference lane

It should not be mistaken for:

- a guarantee that the target desktop has already been tested
- proof that portal or remapper lifecycle details are working on a real host
- a replacement for `doctor`, `gen-readiness-pack`, or `gen-route-selection-pack`
