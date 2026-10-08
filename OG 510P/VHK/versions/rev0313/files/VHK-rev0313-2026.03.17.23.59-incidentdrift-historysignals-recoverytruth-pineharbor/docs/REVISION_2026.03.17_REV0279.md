# Revision 0279 — Desktop notification feedback planning

This revision teaches the planner a more Linux-native feedback lane.

## Added

- `plan-project` surface: `desktop-notification-feedback`
- planner reference pattern: `notification-daemon-feedback-lane`
- ecosystem lesson: `notifications-are-session-service-contract`
- explicit notification feedback analysis keyed off `Notify` usage and `WaitForDbusSignal` usage against `org.freedesktop.Notifications`

## Why

Linux desktop feedback already has a real shared contract through session notification services and daemons. VHK should notice when a project is already living on that surface and stop flattening passive status, modal prompts, and notification-driven follow-up into one generic UI bucket.

## Tests

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_lint_project_cli.py`
