# REV0291 — promotion input lanes and shipping ownership

REV0291 extends the project planner with a new `promotion_input_lane_plan`
surface so project-level promotion work stays tied to the Linux-native input
lane that should actually own the shipped experience.

## What changed

- `plan-project` now emits `promotion_input_lane_plan`.
- Each promotion surface can now name:
  - `shipping_posture` (`flagship`, `specialist`, `reviewed`, `orthogonal`)
  - `primary_input_lane_id`
  - `primary_input_lane_fit`
  - `alternate_input_lane_ids`
  - `recommended_input_lane_ids`
  - `host_requirement_ids`
  - lane-aware `commands`, `evidence`, and `cautions`
- Capability-audit artifacts now render a **Promotion lane plan** section.
- Human `vhk plan-project` output now prints a **Promotion lane plan** table.

## Why this matters

The repo already knew two important truths:

1. project promotion surfaces are not all the same thing (`text-package-export`,
   `remapper-export`, `helper-route-dossier`, `watcher-service-export`, ...)
2. Linux input is not one universal backend; it is split into workload-oriented
   lanes with different contracts (`clipboard-text-lane`,
   `virtual-keyboard-text-fastpath`, `daemon-backed-uinput-playback`,
   `portal-permissioned-input`, `x11-native-replay`)

Before REV0291, those truths only met indirectly. A project could have an
honest `input_lane_dossier`, but the promotion plan still stopped at export
surfaces. That left a gap where shipping work could drift away from the runtime
lane story.

REV0291 closes that gap by asking a sharper question:

> Which lane should actually own the shipped experience for this promotion
> surface?

Examples:

- text package promotion should usually lead with `clipboard-text-lane`
- Wayland remapper-like promotion should stay near
  `daemon-backed-uinput-playback`
- helper-heavy review surfaces should remain explicitly review-led around
  portal/helper seams instead of inheriting whichever lane scored highest
  overall
- watcher and launcher surfaces can stay `orthogonal`, because they are not
  primarily input-lane stories

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

## Test coverage

Focused planner/audit coverage was updated and kept green, including:

- `tests/test_plan_project_cli.py`
- `tests/test_capability_audit_pack_cli.py`
- `tests/test_promotion_pack_cli.py`
- `tests/test_readiness_pack_cli.py`
- `tests/test_runtime_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_route_selection_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_lint_project_cli.py`

## Next pressure point

Now that promotion surfaces can name a concrete shipping lane, the next natural
step is to let pack/export generators consume that plan more directly, so a
strong text lane can materialize package/service scaffolding with less repeated
manual review glue.
