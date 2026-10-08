# Portability playbooks (`vhk plan-project`)

`vhk plan-project` now emits `portability_playbooks`.

This builds on `portability_gaps`.
Where `portability_gaps` explains what changes between the strongest target and a
more conservative one, `portability_playbooks` turns that into a concrete export
and install checklist.

## Why this matters

Linux-native automation projects often stall at the last mile:

- the planning layer correctly says that global hotkeys or pointer injection are weaker
- the team agrees that a launcher, WM bind, remapper, or watcher service is the better fit
- but nobody has a concrete list of artifacts to generate and verify

`portability_playbooks` is meant to close that gap.

## What each playbook contains

Each item includes at least:

- `id`
- `title`
- `priority`
- `goal`
- `summary`
- `artifacts`
- `commands`
- `install_checks`
- `related_surfaces`
- `learn_from`
- `baseline`

## Typical artifacts

Depending on the target lane, a playbook may point you toward:

- an Espanso package export
- a `.desktop` launcher entry
- a launcher helper script
- WM/compositor binding snippets
- remapper configs for keyd / Kanata / KMonad
- systemd user service/socket units
- helper-boundary review work for pointer-heavy flows

## Example reading

A conservative Hyprland playbook might not tell you to rewrite the project.
Instead, it can say:

- keep the text tier and launcher surface
- demote blanket pointer-support claims
- export a desktop entry or compositor-native trigger path
- validate the active portal/compositor routing before shipping

That is the desired shape.
The point is to keep macro logic shared while turning desktop-specific deployment
work into a visible checklist.
