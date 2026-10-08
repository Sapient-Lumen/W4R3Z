# Target route pack

`vhk gen-target-route-pack <project_dir>` compares planner-backed route decisions across a small set of hypothetical Linux target profiles instead of only reflecting the current host.

## Why this exists

`gen-route-selection-pack` answers **which route should this host ship right now?**

`gen-target-route-pack` answers **which route would we probably ship on GNOME Wayland vs KDE Wayland vs wlroots-class Wayland vs a generic X11 desktop?**

That distinction matters because Linux automation products often need one release story per desktop family, not one universal activation claim.

## Generated artifacts

- `docs/VHK_TARGET_ROUTE_MATRIX.md`
- `docs/VHK_TARGET_ROUTE_FIXUPS.md`
- `docs/VHK_TARGET_ROUTE_PLAN.json`
- `scripts/vhk_compare_target_routes.sh`

## Default target profiles

The current pack compares four intentionally conservative profiles:

- `x11-desktop`
- `gnome-wayland`
- `kde-wayland`
- `wlroots-wayland`

They are not live proofs. They are planner-backed comparison profiles that keep release strategy honest before a team has every target desktop in front of them.

## What the JSON plan should expose

- per-profile reference routes
- per-profile selected groups and fallback candidates
- a cross-profile group matrix that shows which route ids diverge
- a compact summary of stable groups vs divergent groups

## Intended workflow

1. Run `vhk gen-route-selection-pack` for the current host.
2. Run `vhk gen-target-route-pack` to compare that host-local story against target desktops.
3. Decide whether the release should standardize on one profile first or publish separate route guidance per desktop family.
