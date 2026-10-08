# REV0273 — WM modal trigger lanes become planner-visible

Date: 2026-03-17
Codename: modaltruth-bindlayer-resetpath-brightgrove

## What changed

This revision turns an existing export capability into an explicit planning
surface.

Added:

- `wm-modal-trigger-layer` to `plan-project` surface choices
- `wm-modal-submap-lane` to reference patterns
- `wm-modes-submaps-grouped-triggers` to ecosystem lessons

The new lane appears for X11/i3-class, sway, and Hyprland-shaped projects when
there are enough bindings/macros that one flat hotkey grid is starting to look
less honest than a grouped entry chord.

## Why

VHK already knew how to export launcher modes and WM configs, but the planner
still forced a false binary too often:

- either keep adding more global bindings
- or jump all the way to launcher/menu surfaces

Real Linux WMs already offer a middle layer:

- i3 binding modes
- Hyprland submaps
- sxhkd chord-chain flows on X11

That middle layer is useful because it is temporary, desktop-native, and thin.
It groups actions without stealing macro semantics away from VHK.

## Tests run

Passed:

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_activation_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_wm_modes.py`
- `tests/test_wm_bundle_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_lint_project_cli.py`

## Docs updated

- `docs/SPECS.md`
- `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
- `docs/ISSUES_2026Q1.md`
- `docs/RESEARCH_2026.03.17_WM_MODES_SUBMAPS_AND_GROUPED_TRIGGER_LAYERS.md`
