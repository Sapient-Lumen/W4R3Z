# Revision REV0272 — portal catalog honesty for Wayland trigger planning

This revision turns another current Linux lesson into executable planner logic.

VHK already knew that the GlobalShortcuts portal was a real Wayland trigger
lane. But the planner still treated Wayland hotkeys too eagerly as portal-first,
which blurred an important boundary: portal shortcuts work best for a reviewed,
predeclared action catalog, not for every helper-sensitive or fast-changing
hotkey in a project.

## What changed

- added planner-side portal catalog analysis that classifies bound macros as
  either stable portal-catalog fits or dynamic/helper-sensitive trigger flows
- updated the `portal-global-shortcuts` surface so its score/evidence now name
  `stable_shortcut_candidates` and `dynamic_shortcut_candidates`
- added a new reference pattern:
  `portal-session-catalog-lane`
- updated the `portal-shortcuts-route` activation lane so it is scored/documented
  as a stable-catalog route instead of a generic Wayland default
- updated macro route ownership so helper-sensitive Wayland hotkeys no longer
  default to the portal route when a native/compositor trigger lane is the more
  honest wake-up path
- added a focused research note:
  `docs/RESEARCH_2026.03.17_PORTAL_CATALOG_STABILITY_AND_DYNAMIC_TRIGGER_BOUNDARIES.md`

## Why it matters

A Linux-native AHK analogue needs to know more than “the portal exists.” It
needs to know **when that route is actually the right product shape**.

For Wayland trigger ownership, the new distinction is:

- portal session route for stable action catalogs
- compositor/native bind route for hotter, helper-sensitive, or more dynamic
  trigger inventories
- launcher/palette fallback when either of those routes is weak or desktop-bound

That is a more honest planning model than portal-first by default.

## Validation

Focused suites pass for the affected planning and downstream pack surfaces:

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_activation_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
