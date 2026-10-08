# Revision 0278 — MPRIS media service-bus planning

This revision teaches the planner a more Linux-native media lane.

## Added

- `plan-project` surface: `mpris-media-bus-adapter`
- planner reference pattern: `mpris-follow-control-lane`
- ecosystem lesson: `mpris-standard-media-bus`
- explicit MPRIS signal analysis keyed off `WaitForDbusSignal` usage against `org.mpris.MediaPlayer2*`

## Why

Linux media automation already has a real standard contract through MPRIS and thin adapter tools like `playerctl`. VHK should notice when a project is already living on that bus and avoid flattening those flows into generic media-key replay or polling folklore.

## Tests

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
