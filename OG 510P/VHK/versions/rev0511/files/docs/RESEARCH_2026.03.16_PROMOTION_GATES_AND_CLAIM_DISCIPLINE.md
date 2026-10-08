# Research notes — promotion gates and Linux claim discipline

This pass was guided by a recurring lesson from current Linux automation tools:
**the sharpest product problems are no longer just "can it run" but "what can
it honestly promise on this desktop/session?"**

## Current ecosystem lessons

### 1) Text, remapping, and helper-driven automation are still separate product lanes

- Espanso still treats text expansion as a dedicated surface with app-specific
  configuration and precedence rules; its Wayland story remains more conditional
  than its X11 story.
- keyd and similar evdev/uinput tools still frame remapping as a low-level,
  system-wide lane rather than a generic scripting runtime feature.
- xremap keeps proving that app-aware remapping is possible across X11/Wayland,
  but with desktop/context caveats that are not the same thing as generic macro
  playback.

Implication for VHK: planner output should not only identify these lanes; it
should also guard against release language that collapses them back into one
"Linux automation backend" story.

### 2) Portal/session surfaces are real, but they are review surfaces

- GlobalShortcuts is session-based, not a generic permanent hotkey grab.
- InputCapture has enabled/active phases, with the compositor deciding when
  activation actually happens.
- portal backend routing still depends on desktop configuration (`portals.conf`
  and related backend selection).
- libportal gained Input Capture support recently enough that packaging and host
  drift are still relevant parts of the product story.

Implication for VHK: helper-sensitive routes should keep showing up as review or
fail gates unless the target session story is explicit.

### 3) Mature Linux tools keep their honesty at the edges

- AutoKey still states that the mainline tool is X11-oriented.
- AHK_X11 still frames itself as an X11-based Linux AutoHotkey rather than a
  universal Wayland parity layer.
- Kando's Linux/Hyprland instructions still rely on compositor-owned shortcut
  hookup and reviewable desktop integration steps.
- `wtype` and related virtual-keyboard tools remain compositor/protocol shaped,
  not universal text injection guarantees.

Implication for VHK: release planning should surface claim discipline directly,
not bury it in docs. That is why this revision adds planner/lint/promotion-pack
**promotion gates**.

## Product idea carried into the repo

VHK should develop a consistent ladder:

1. classify macro ownership
2. aggregate project promotion surfaces
3. mark readiness
4. derive explicit promotion/claim gates
5. reuse those gates in lint/release/claim artifacts

That keeps the product creative without becoming hand-wavy.
