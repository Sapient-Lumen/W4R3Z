# Portability gaps (`vhk plan-project`)

`vhk plan-project` now emits `portability_gaps`.

This builds on `environment_diffs`.
The earlier comparison answers:

- how does this project land on X11/i3?
- how does it land on GNOME/KDE Wayland?
- how conservative should wlroots/Hyprland support be?

The new layer answers the next operational question:

- what changes when we move from the strongest target to a more conservative one?

## Why this matters

Linux-native automation work often fails at the handoff point.
A team proves the project on one target, then later discovers that another
session needs different trigger ownership, different helper boundaries, or a
weaker promise around pointer/global-input behavior.

`portability_gaps` makes that shift visible early.

## What each portability gap contains

Each item includes at least:

- `id`
- `title`
- `baseline`
- `score`
- `fit`
- `score_delta`
- `summary`
- `newly_blocked_capabilities`
- `degraded_capabilities`
- `relaxed_blockers`
- `keep_surfaces`
- `replace_surfaces`
- `new_preferred_surfaces`
- `migration_response`
- `commands`
- `learn_from`

## Interpretation

A good use of this output is:

1. find the strongest target for the current project
2. look at the environments you still want to support
3. inspect which capabilities become newly blocked or degraded
4. keep shared macro logic in VHK core
5. move the unstable edges into:
   - WM/compositor-native binds
   - text/export surfaces
   - helper boundaries
   - user-service packaging

## Example migration reading

A pointer-heavy project may show:

- baseline: **X11/i3 reference**
- target: **Hyprland conservative**
- newly blocked: `pointer_injection`, `global_hotkeys`
- replace surfaces:
  - X11 hotkey daemon -> compositor-native dispatch
  - pointer-heavy runner path -> helper-boundary or text-first path

That is exactly the kind of planning signal VHK should surface.
The goal is not to pretend every desktop can reach identical AHK breadth.
The goal is to make the portability cost explicit while preserving as much
shared macro logic as possible.
