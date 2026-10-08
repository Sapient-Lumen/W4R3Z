# Research notes: distribution handoff (2026 Q1)

This note captures a few current lessons from adjacent Linux automation tools
that matter for VHK's publish/package shape.

## Core lessons

### 1. Long-lived helper daemons are part of the product boundary

Projects like keyd and ydotool make the low-level boundary explicit instead of
pretending key injection is just an ordinary app concern. keyd is a system-wide
daemon built on `evdev`/`uinput`, and ydotool requires a persistent `ydotoold`
service to hold a virtual device open.

For VHK this means publish/install output should keep helper/service seams
visible in the release handoff instead of collapsing everything into “run this
macro tool” language.

### 2. Fast trigger tiers and higher-level macro tiers should stay distinct

Kanata's value proposition is not “replace your whole automation stack”; it is
fast keyboard behavior, layers, tap-hold logic, and macros with live reload.
Espanso likewise keeps text expansion/service behavior explicit.

For VHK this reinforces the product split we keep rediscovering:

- trigger/remapper tiers can be exported to fast native helpers
- text workflows can be exported as package/service shaped surfaces
- VHK's heavier orchestration/runtime should stay for cross-surface workflows,
  prompts, selectors, capture, and reviewable project-level logic

### 3. Wayland setup still includes environment and privilege choreography

xremap's Wayland guidance still shows environment transfer and compositor-
specific launch constraints. That is a reminder that “works on Wayland” is not
a single support statement.

For VHK this means publish/release handoffs should carry lane-specific install
commands and stage references forward instead of flattening everything into a
single generic Linux bundle.

### 4. X11-first tools remain instructive, but not sufficient

AutoKey still models a valuable product shape: macros + hotkeys + text
expansion + scripting. But its own project still documents X11 as the real
platform boundary.

For VHK, the lesson is to keep learning from AHK/AutoKey-style workflows while
refusing to hide the compositor/session split in support and packaging output.

### 5. Distribution proof matters too

Espanso's install docs now make service registration/start explicit and also
ship distro/appimage installation paths and checksum guidance.

For VHK this suggests the next layer after publish handoff trees: package or
AppImage/Flatpak skeletons that are generated from the same reviewed stage/publish
root instead of being assembled ad hoc later.
