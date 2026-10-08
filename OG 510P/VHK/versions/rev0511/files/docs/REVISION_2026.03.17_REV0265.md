# Revision REV0265 — planner witnesses and early host proof

This revision closes a planner-shaped gap: core `plan-project` / strategy output
now exposes claim-witness posture directly instead of waiting for later
claim/promotion overlays.

## What changed

- fixed a regression where `plan-project --json` referenced an undefined
  `host_snapshot`
- `plan-project` now computes live host truth when session checks are enabled and
  passes current `host_truth` plus `portal_route_contract` into the core
  strategy payload
- `summarize_project_strategy()` now accepts optional planner-side host/portal
  truth inputs
- strategy JSON now emits:
  - `planner_target_claims`
  - `planner_claim_review`
  - `planner_claim_witness`
  - current `host_truth`
  - current `portal_route_contract`
- terminal `plan-project` output now renders:
  - `Current host proof posture`
  - `Planner target claims`
- shared claim-witness logic now lives in `src/vhk/project/claim_witness.py`
  instead of being trapped only inside claim-pack logic

## Why it matters

VHK had already learned how to keep support claims honest in claim/promotion
packs, but the base planner still let wrong-host evidence stay hidden until much
later in the workflow. This revision brings that proof boundary into the core
strategy surface.

## Validation

Targeted tests now cover:
- `plan-project --json` working again without the `host_snapshot` crash
- planner-side witness posture when current host review is available
- existing host/window planner expectations still present in JSON output
