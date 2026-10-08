# REV0283 — WezTerm CLI adapter pack

This revision turns another app-native planning lane into a concrete export surface.

## What changed

- added `vhk gen-wezterm-pack`
- added `src/vhk/project/wezterm_pack.py`
- added `tests/test_wezterm_pack_cli.py`
- updated app-native planner command wiring so WezTerm-targeted projects now point at a real pack
- updated specs/plan/issues docs

## Why

The planner already recognized WezTerm as an app-native target, but the lane still stopped at prose. This revision makes that lane reviewable and runnable through thin helper scripts that keep WezTerm CLI in charge of pane transport while VHK keeps macro semantics.

## Validation

Focused tests passed for:

- `tests/test_wezterm_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
