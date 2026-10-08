# REV0274 — Accessibility lanes become planner-visible

Date: 2026-03-17
Codename: busproof-widgetlane-structurepath-amberframe

## What changed

This revision turns Linux accessibility automation from an implied future idea
into an explicit planning lane.

Added:

- `atspi-structured-ui` to `plan-project` surface choices
- `atspi-structured-selector-lane` to reference patterns
- `atspi-separate-bus-structured-automation` to ecosystem lessons
- stronger `window-introspection` toolchain guidance that now keeps
  `AT-SPI/Accerciser` and `dogtail/pyatspi` visible alongside desktop metadata
  bridges

## Why

VHK already had pieces of this story:

- a doctor probe for the accessibility bus
- window/context tooling
- long-standing repo intent around AT-SPI selectors

But the planner still left a gap between:

- raw window metadata
- vision/capture flows
- future semantic widget targeting

That gap matters because Linux accessibility automation is neither fake nor
universal. It is a separate contract: separate bus, per-toolkit coverage,
inspector-driven authoring, and explicit fallbacks when the tree is absent or
poor.

## Product effect

`plan-project` can now say something more honest for structured UI work:

- use desktop metadata bridges for container/focus/workspace truth
- use AT-SPI-style structured targeting when widget semantics are exposed
- keep vision and other fallbacks ready for the apps that do not expose a good
  tree

That makes VHK more Linux-native and more creative at the same time: it learns
from real accessibility tooling instead of flattening every UI problem into
window titles or screenshots.

## Tests run

Passed:

- `tests/test_plan_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`

## Docs updated

- `docs/SPECS.md`
- `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
- `docs/ISSUES_2026Q1.md`
- `docs/RESEARCH_2026.03.17_ATSPI_STRUCTURED_UI_LANES_AND_ACCESSIBILITY_CONTRACTS.md`
