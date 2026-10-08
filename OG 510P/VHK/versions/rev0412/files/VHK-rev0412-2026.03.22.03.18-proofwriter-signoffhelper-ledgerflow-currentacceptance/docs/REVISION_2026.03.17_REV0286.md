# Revision 0286 — notification action/progress lane

This revision extends the notification feedback lane again so VHK can model more of the real Linux desktop-notification contract instead of stopping at replaceable ids.

## What changed

- extended `Notify` with:
  - `progress`
  - `actions`
  - `wait`
  - `out_action`
- upgraded `src/vhk/system/notify.py` so it can:
  - emit progress hints for `notify-send` and `dunstify`
  - attach reviewable action ids/labels for both backends
  - block when action feedback is requested and capture the selected action id from stdout
- updated runner plumbing so selected notification actions can round-trip into macro vars (`out_action`, `last_notification_action`)
- strengthened planner notification evidence with:
  - `actionable_notifications`
  - `progress_notifications`
- added/expanded tests:
  - `tests/test_notify_step.py`
  - `tests/test_plan_project_cli.py`
- updated:
  - `README.md`
  - `docs/SPECS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/ISSUES_2026Q1.md`
  - `docs/RESEARCH_2026.03.17_NOTIFICATION_ACTIONS_AND_PROGRESS_HINTS.md`

## Why this matters

A Linux-native automation tool should be able to say:

- show one replaceable progress toast
- update its value over time
- optionally let the operator choose `open`, `retry`, or `dismiss`
- branch on that choice without converting the whole flow into a fake modal dialog

This keeps notification feedback closer to the real desktop contract while still keeping macro logic reviewable.

## What passed

- `tests/test_notify_step.py`
- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_runtime_pack_cli.py`
- `tests/test_lint_project_cli.py`

## Remaining honest gap

- close reasons are still not modeled as a first-class cross-daemon output
- notification capability probing is still thinner than the playerctl/portal/WM route probes
- VHK still does not ship a dedicated notification adapter pack with reviewable daemon-specific install/runtime notes
