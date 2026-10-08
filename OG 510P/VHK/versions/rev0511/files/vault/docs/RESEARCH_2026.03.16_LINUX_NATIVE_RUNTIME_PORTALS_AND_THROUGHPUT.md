# Research notes (2026-03-16): Linux-native trigger lanes, helper boundaries, and text throughput

This note captures a quick current-state check against the upstream Linux/X11/Wayland ecosystem while planning VHK toward "AHK-class usefulness on Linux".

## 1) Global shortcuts and input capture remain portal/backend-specific

The freedesktop portal stack does expose `GlobalShortcuts` and `InputCapture`,
but VHK should continue to model them as **conditional surfaces**, not generic
Wayland guarantees. Backend routing still depends on portal configuration and
desktop/backend support.

Implication for VHK:

- keep `doctor` / `validate` / `lint-project` honest about the active shortcut lane
- do not market portal triggers as universal Wayland hotkeys
- keep WM/compositor bindings and helper daemons as first-class alternatives

## 2) X11 remains the cleanest "AHK-like" path for full replay

`xdotool` still rides XTEST/Xlib and remains fundamentally an X11 lane. That is
precisely why X11/i3 is still VHK's best near-term target for the most complete
record/replay/debug loop.

Implication for VHK:

- keep X11 recorder/optimizer/report loops very strong
- avoid pretending that the same replay semantics exist everywhere on Wayland

## 3) Wayland helper lanes belong at explicit product boundaries

Projects like keyd sit below the compositor using evdev/uinput, and wlroots-ish
application/context helpers still tend to depend on compositor-specific or
non-standard metadata. That makes remappers and app-context adapters real
boundaries, not invisible implementation details.

Implication for VHK:

- plan/export/install docs should keep remap/helper choices explicit
- "app-aware" trigger surfaces should carry a scoped portability story

## 4) Text throughput deserves first-class treatment

A large amount of practical desktop automation is text insertion, canned replies,
forms, and structured snippets. VHK already has the raw mechanisms for typed,
clipboard, and hybrid segmented text; the current product opportunity is to make
that choice explicit earlier in lint/planner/studio flows.

Implication for VHK:

- long literal typed text should be visible as a performance smell
- structured Tab/Enter-rich text should suggest hybrid segmentation, not only raw typing
- text-first automation should remain a first-class lane even when the project started from recorder output
