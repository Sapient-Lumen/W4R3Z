# Revision REV0271 — explicit daemonized helper lanes for repeated Wayland playback

This revision turns another Linux-native lesson into executable planning output.

VHK already had service generators, setup recipes, and host/readiness contracts
for `dotoold`, `ydotoold`, sockets, and `/dev/uinput`. But the top-level planner
still stopped short of elevating that into a visible deployment lane.

## What changed

- added `uinput-helper-daemon` to `plan-project` candidate surface choices for
  Wayland-facing projects that lean on repeated text/pointer playback
- added `daemonized-uinput-helper-lane` to planner reference patterns
- added `daemonized-helper-lifecycle` to ecosystem lessons
- updated specs/plan/issues docs with the product lesson: daemon lifecycle is
  part of the Linux-native surface, not just an install footnote
- added a research note: `docs/RESEARCH_2026.03.17_DAEMONIZED_HELPER_LANES_AND_UINPUT_SERVICE_BOUNDARIES.md`

## Why it matters

A Linux-native AHK analogue should not only know that helper tools exist. It
should help operators choose a **reviewable lane** that can actually survive
deployment. For repeated playback on Wayland-class hosts, that often means:

- persistent helper daemon
- explicit socket ownership
- reviewed `/dev/uinput` policy
- swappable helper family choice

## Validation

Focused suites pass for the affected planner surfaces:

- `tests/test_plan_project_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
