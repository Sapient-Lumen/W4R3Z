# Revision 0280 — playerctl / MPRIS adapter pack

This revision turns the MPRIS planning lane into a concrete export surface.

## Added

- `vhk gen-playerctl-pack`
- new module: `src/vhk/project/playerctl_pack.py`
- planner command wiring so the MPRIS surface/pattern/lesson point to `gen-playerctl-pack`

## What it writes

- `vhk.playerctl.routes.yml` — reviewable route catalog derived from MPRIS-shaped `WaitForDbusSignal` steps
- `vhk.playerctl.commands.json` — machine-readable command ledger
- `bin/*.sh` — thin helper wrappers for `playerctl --follow` and optional `vhk run ...` dispatch
- `README.md` — operator-facing explanation of the lane and its limits

## Why

The planner already knew to recommend playerctl/MPRIS-style media control, but that advice still stopped at session-fit/design packs. This revision gives that lane a concrete adapter handoff without turning VHK into a media daemon or hiding latest-player policy inside the runner.

## Tests

- `tests/test_playerctl_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
