# Revision 0276 — app-native protocol lanes

This revision teaches `plan-project` another Linux-native lesson: some target
apps already expose better control contracts than simulated input.

## What changed

- added `app-native-control-adapter` to `surface_choices`
- added `app-native-protocol-lane` to `reference_patterns`
- added `native-app-protocols-beat-input-replay` to `ecosystem_lessons`
- added target analysis for known protocol-rich apps reached through selectors
  and scoped bindings:
  - kitty
  - WezTerm
  - mpv
  - qutebrowser
- updated:
  - `docs/SPECS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/ISSUES_2026Q1.md`

## Why

Linux-native automation is often healthiest when VHK uses app-native control
contracts where they exist, instead of replaying keys/pixels into every target
window by default.

The planner can now make that explicit early, based on real project selectors,
so teams see adapter opportunities during design instead of only after brittle
replay logic accumulates.

## Tests run

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
