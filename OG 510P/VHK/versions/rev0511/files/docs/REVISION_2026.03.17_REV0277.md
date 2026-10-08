# Revision 0277 — voice adapter context lanes

This revision teaches `plan-project` another Linux-native lesson: voice control
is healthiest as a reviewable adapter lane, not a hidden post-export trick and
not a second runtime inside VHK.

## What changed

- added `voice-command-adapter` to `surface_choices`
- added `voice-context-command-lane` to `reference_patterns`
- added `voice-tools-own-recognition-context` to `ecosystem_lessons`
- added planner analysis for deliberate voice metadata:
  - explicit `voice_phrases`
  - scoped `voice_when` contexts
  - unique spoken-form counts across macro/preset exports
- updated:
  - `docs/SPECS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/ISSUES_2026Q1.md`

## Why

The repo already exported Dragonfly and Talon packs, but the planner still
treated voice like an afterthought. That made a real Linux adapter lane hard to
see during project review.

Now projects with deliberate spoken phrases or scoped voice contexts get an
explicit planning surface early, so teams can review phrase quality, context
fidelity, and backend fit before treating voice like a generic support claim.

## Tests run

- `tests/test_plan_project_cli.py`
- `tests/test_dragonfly_pack_cli.py`
- `tests/test_talon_pack_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_design_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
