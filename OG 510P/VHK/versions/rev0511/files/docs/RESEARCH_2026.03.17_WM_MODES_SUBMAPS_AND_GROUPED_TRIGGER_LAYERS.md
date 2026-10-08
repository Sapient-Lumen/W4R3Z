# Research — WM modes/submaps and grouped trigger layers

Date: 2026-03-17
Revision: REV0273

## Why this note exists

VHK already exported i3/sway/Hyprland launcher modes and could generate
mode/submap-friendly WM snippets, but the planner still under-modeled that idea.

That left a real Linux-native trigger lesson stranded in tooling instead of
surfaced as product guidance:

- flat always-on global bindings are not the only alternative to launcher menus
- modern Linux WMs already provide a middle layer for grouped actions
- that grouped layer is useful precisely because it is **desktop-native** and
  **temporary**, not because it becomes a second automation runtime

## What others are doing that matters

### 1) i3 treats binding modes as a first-class config primitive

The i3 User's Guide documents binding modes as multiple sets of bindings where
switching modes releases the current mode and activates the next one until the
user returns to `default`.

That matters because it means grouped action families are not an afterthought in
an i3-class stack. They are a normal way to keep related actions behind one
entry chord instead of minting more permanent global shortcuts.

### 2) Hyprland submaps push the same idea further

Current Hyprland docs explicitly describe submaps as modes/groups, show reset
requirements, allow nesting, and document automatic close/reset behavior after a
dispatch.

That is a sharper product lesson than “Hyprland supports binds”:

- grouped trigger layers are part of the compositor model
- reset semantics are a real safety/usability contract
- one-shot or auto-closing flows are desirable for action families that should
  not leave hidden state behind

### 3) sxhkd keeps the X11 side of the same lesson alive

The current sxhkd manual still documents chord chains and the special `:`
behavior where a chain tail is not aborted, plus an Escape abort path.

That means the X11/i3 side of Linux automation also has a credible grouped
trigger story even when it is not spelled as a formal “mode” primitive. The
important architectural point is the same: a thin hotkey layer can expose a
transient action family without owning macro semantics.

## Product implication for VHK

VHK should model **grouped trigger layers** as a first-class planning lane:

- flat binds remain one trigger surface
- launcher/menu hubs remain another
- WM-native modes/submaps/chord-groups become the middle lane for projects that
  have too many related actions for flat globals but do not want to force
  everything through a launcher

That lane should stay explicit and target-desktop-shaped:

- strong for i3/sway/Hyprland and X11/i3-class stacks
- paired with reset/escape requirements
- paired with launcher fallbacks
- never described as a generic Linux hotkey guarantee

## Concrete repo effect in REV0273

`plan-project` now surfaces this lesson in three places instead of leaving it as
implicit exporter capability:

- `wm-modal-trigger-layer` in surface choices
- `wm-modal-submap-lane` in reference patterns
- `wm-modes-submaps-grouped-triggers` in ecosystem lessons

That makes VHK a little more honest and a little more creative at the same
time: it learns from real Linux desktop ergonomics without collapsing those
lessons into one fake universal backend.
