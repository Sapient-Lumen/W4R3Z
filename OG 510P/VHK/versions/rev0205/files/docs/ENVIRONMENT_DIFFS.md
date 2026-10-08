# Hypothetical environment comparison (`vhk plan-project`)

`vhk plan-project` now emits `environment_diffs`.

This is the next step after `surface_choices` and `desktop_targets`.
Instead of asking only:

- what kind of project is this?
- which surfaces are promising?

it also asks:

- how does the same project land on **X11/i3** vs **GNOME Wayland** vs
  **KDE Wayland** vs **wlroots/sway** vs **Hyprland**?

## Why this matters

Linux automation is not only fragmented by *tool choice*.
It is also fragmented by *desktop target*.

A project that looks healthy on X11 may need a helper boundary or a text tier on
Wayland. A project that looks fine on GNOME or KDE may still need a more
conservative plan on wlroots/Hyprland-style targets.

VHK should make those shifts visible during planning, not only after deployment.

## What `environment_diffs` contains

Each environment entry includes:

- `id`
- `title`
- `backend`
- `score`
- `fit`
- `summary`
- `assumptions`
- `learn_from`
- `capability_statuses`
- `top_target`
- `top_profile`
- `preferred_surfaces`
- `blocking_capabilities`
- `diff_highlights`
- `commands`

## Current hypothetical targets

The planner currently compares the project against these target environments:

- portable text baseline
- X11/i3 reference
- GNOME Wayland conservative
- KDE Wayland portal-first
- wlroots/sway conservative
- Hyprland conservative

These are **planning heuristics**, not live capability claims.
They encode current ecosystem lessons into reusable target profiles so authors
can see how the architecture shifts before they boot every session.

## Interpretation

A good use of the comparison output is:

1. find the strongest overall environment for the project
2. find the most conservative environment you still want to support
3. compare the top profile / top target / preferred surfaces between them
4. move shared logic into VHK core and push environment-specific behavior toward
   exports, helpers, compositor binds, or service layers

## Example

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
```

A pointer-heavy project might show:

- **X11/i3** -> `x11-tiling-native` target
- **GNOME/KDE Wayland** -> helper-boundary or portal-centric profiles
- **wlroots/Hyprland** -> conservative compositor-bind and watcher-first plans

That is the intended result.
The goal is not to crown one desktop as “best”; it is to expose the architecture
changes required to keep the project honest.
