# Revision 0285 — replaceable notification runtime lane

This revision turns the notification feedback lane into a more Linux-native runtime contract instead of leaving `Notify` as a one-shot summary/body wrapper.

## What changed

- extended `Notify` with:
  - `app_name`
  - `icon`
  - `category`
  - `timeout_ms`
  - `replace_id`
  - `transient`
  - `out_id`
- upgraded `src/vhk/system/notify.py` so it can:
  - emit backend-specific metadata for both `notify-send` and `dunstify`
  - request/parse notification ids (`--print-id` / `--printid`)
  - send replaceable updates (`--replace-id` / `--replace`)
  - keep transient notifications explicit (`--transient` or `BOOLEAN:transient:true` hint)
- updated runner plumbing so notification ids can round-trip through macro vars and later `Notify` steps
- strengthened planner notification evidence with:
  - `replaceable_notifications`
  - `timed_notifications`
  - `transient_notifications`
- added tests:
  - `tests/test_notify_step.py`
- updated:
  - `docs/SPECS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/ISSUES_2026Q1.md`

## Why this matters

Linux notification stacks already support replace/update semantics. VHK should be able to express “start progress notification, then update/replace it later” directly instead of forcing projects to spray a new passive popup for every status change.

That makes the lane more honest for:

- progress/status updates
- volume/brightness/toast replacement patterns
- app-branded notifications with reviewable categories/icons/timeouts
- future notification-action workflows where VHK reacts to daemon-owned close/action events

## What passed

- `tests/test_notify_step.py`
- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`

## Remaining honest gap

This still stops short of a full notification action/runtime layer:

- `Notify` does not yet expose first-class action buttons / selected-action outputs
- VHK still does not ship a reviewable notification adapter pack the way it now does for playerctl, kitty, mpv, WezTerm, and qutebrowser
- desktop capability differences still matter, especially around timeout handling, persistence, and action support
