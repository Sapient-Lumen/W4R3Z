# REV0292 — promotion-pack shipping lane map

REV0292 threads the planner's `promotion_input_lane_plan` into
`gen-promotion-pack`, so project-level promotion artifacts stop talking only in
export surfaces and start naming the Linux-native input lane that actually owns
shipping for each surface.

## What changed

- `build_promotion_pack_plan()` now carries `promotion_input_lane_plan` forward
  into the promotion-pack JSON payload.
- Added `promotion_input_lane_summary` with posture counts plus dominant primary
  lane ids.
- `docs/VHK_PROMOTION_PLAN.md` now renders a **Promotion shipping lanes**
  section showing shipping posture, primary lane, alternate lanes, related host
  requirements, summary, cautions, and review commands for each surface.
- Promotion review commands now also include lane-specific review commands from
  `promotion_input_lane_plan`.
- Updated README/spec/plan/issues docs so promotion-pack expectations match the
  planner's lane-aware strategy model.

## Why it matters

VHK had already learned a healthier Linux-native lesson: export surfaces and
shipping lanes are not the same thing. Text packages, helper-route dossiers,
remapper exports, and launcher surfaces can all exist in one project, but they
should not all pretend to ship through one universal input story. Before this
revision, reviewers had to open planner output or reconstruct lane ownership by
hand. Now the promotion pack itself shows which lane owns each surface.

## Tests

Passed focused tests:

- `tests/test_promotion_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_capability_audit_pack_cli.py`
