# Revision 0301 — authority-aware setup and release handoffs

This revision carries the Linux authority model out of planner/install/service prose and into the setup/release artifacts operators actually follow.

## What changed

- added `src/vhk/project/authority_policy.py` to centralize project-level authority-policy derivation
- `build_setup_pack_plan()` now carries `authority_policy`, and setup docs render **Authority-aware setup boundaries**
- `build_release_lane_plan()` now computes per-lane `authority_story` plus an `authority_summary`
- release-lane docs now render **Release authority overview** and **Copy-ready authority handoff snippets**
- release-deploy plans/docs inherit the same authority story so deploy choices and install snippets stop hiding ownership boundaries
- release-stage plans/docs/README output now carry the same authority story so staged handoffs preserve who owns a lane after shipping

## Why it matters

VHK had already become much better at saying which Linux lane should be warm, which lane should ship helper state, and which lane deserved portal-first review. But setup and release artifacts could still flatten those differences back into package/deploy prose. This revision keeps the boundary honest all the way through setup, release-lane planning, deployment, and staged handoff output.

## Test coverage

- `tests/test_setup_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_release_stage_pack_cli.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_service_compose_pack_cli.py`
