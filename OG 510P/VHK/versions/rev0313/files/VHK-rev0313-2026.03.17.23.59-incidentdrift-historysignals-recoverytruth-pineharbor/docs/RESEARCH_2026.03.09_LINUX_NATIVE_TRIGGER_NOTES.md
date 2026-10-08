# Research notes — 2026-03-09 Linux-native trigger/context lanes

This note records a few ecosystem realities that should keep shaping VHK's
Linux-native architecture rather than being treated as one-off trivia.

## 1) App-aware behavior on Wayland is still desktop-specific

Current remapper/tooling ecosystems still depend on desktop/compositor-specific
context bridges for reliable per-app behavior. VHK should keep GNOME, KDE,
wlroots/sway, Hyprland, and similar targets as explicit lanes when app/window
context matters.

## 2) Portal GlobalShortcuts is important, but still a soft boundary

Portal-first hotkeys are strategically valuable for Linux-native Wayland work,
but backend consent flows, app-id association, and early-session timing issues
still mean the route needs explicit validation and fallback planning.

## 3) Cross-compositor input injection remains a layered problem

`libei` / EIS matters as an interop seam, but practical deployment still depends
on compositor/backend support and portal/RemoteDesktop plumbing. VHK should keep
native helpers/export lanes explicit instead of assuming one universal input
stack.

## 4) VHK's differentiation remains real

AutoKey's official positioning still leaves it X11-centric, while xremap keeps
expanding compositor-specific lanes. That reinforces VHK's strategic niche:
Linux-native route selection plus honest runtime capability/contracts, not a
single fake-universal automation path.
