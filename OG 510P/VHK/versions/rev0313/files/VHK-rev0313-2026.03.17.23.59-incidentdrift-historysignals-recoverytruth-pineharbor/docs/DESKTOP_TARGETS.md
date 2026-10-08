# Desktop target matrix

`vhk plan-project` now emits `desktop_targets` to make a harder product
question explicit:

> Which desktop/compositor targets should this project optimize for first?

This surface is intentionally shaped by current Linux automation lessons:

- text surfaces want export-friendly packaging and app scoping
- trigger planes want tiny always-on helpers or compositor/WM binds
- vision flows want a selector asset pack, not recorder leftovers
- Wayland support is a capability matrix and often needs helper boundaries
- wlroots/Hyprland-class targets should be approached conservatively when a
  project depends on pointer injection or generic portal parity

## Current target families

### Portable text/export

Use when the project is mainly snippets, hotstrings, forms, or structured text
macros. The runner remains valuable for prompts and variable collection, but
not every expansion needs to pay the price of full macro playback.

### X11 tiling-native

Use when the goal is explicit i3/X11-class desktop automation and broad pointer
+ hotkey + screen workflows matter more than abstract portability.

### Portal-centric Wayland

Use when the project can work inside explicit permission/session flows and can
accept capability-aware deployment instead of “Wayland yes/no”.

### Helper-boundary Wayland

Use when the project still needs pointer-heavy automation or always-on trigger
behavior on Wayland. Macro logic stays in VHK; injection stays behind adapters.

### wlroots / Hyprland conservative

Use when you want to support fast-moving compositor stacks without promising
more than the current capability matrix actually gives you. Bias toward binds,
watchers, services, and text surfaces first.
