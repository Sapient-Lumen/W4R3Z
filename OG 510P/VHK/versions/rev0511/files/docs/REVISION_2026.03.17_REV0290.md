# Revision 0290 — workload-shaped input lane dossiers

This revision turns a real Linux-native product lesson into code: VHK now
models input review by **workload lane** instead of only by helper/tool names.

## What changed

- `plan-project` now emits `input_lane_dossier` with one grouped view of:
  - clipboard-first text lanes
  - Wayland virtual-keyboard fast paths
  - daemon-backed uinput playback
  - portal-permissioned input lanes
  - X11-native replay
- the planner CLI now prints an **Input lane dossier** table in human output
- `gen-capability-audit-pack` now carries that dossier into
  `docs/VHK_CAPABILITY_AUDIT.md` and `docs/VHK_CAPABILITY_AUDIT_PLAN.json`
- added tests covering planner JSON, session-aware lane scoring, and audit-pack
  rendering

## Why it matters

Linux desktop automation keeps teaching the same lesson: the hard part is not
just “which binary is installed?” but “which lifecycle/policy lane fits this
workload on this host?” Long snippets, short typed bursts, repeated pointer
playback, and portal/libei-style permissioned control are not the same product
route.

That makes VHK more honest and more creative at the same time. It stops treating
Linux input as a flat backend menu and starts treating it as a set of reviewed
operator-owned lanes.

## Files touched

- `src/vhk/project/strategy.py`
- `src/vhk/cli.py`
- `src/vhk/project/capability_audit_pack.py`
- `tests/test_plan_project_cli.py`
- `tests/test_capability_audit_pack_cli.py`
- `README.md`
- `docs/SPECS.md`
- `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
- `docs/ISSUES_2026Q1.md`
- `docs/RESEARCH_2026.03.17_WORKLOAD_INPUT_LANES_AND_OPERATOR_DOSSIERS.md`

## Validation

Focused suites passed:

- `tests/test_plan_project_cli.py`
- `tests/test_capability_audit_pack_cli.py`
- `tests/test_readiness_pack_cli.py`
- `tests/test_runtime_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_route_selection_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_lint_project_cli.py`
