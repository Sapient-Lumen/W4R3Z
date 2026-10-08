# Revision REV0266 — explicit evidence lanes

This revision turns VHK's newer proof model into an operator-controlled review
feature: maintainers can now pin one explicit evidence lane across planner,
claim, audit, promotion, and capability-audit flows.

## What changed

- added explicit `evidence_lane_profile` / `--evidence-lane <profile-id>`
  support to:
  - `plan-project`
  - `gen-claim-pack`
  - `audit-target-claims`
  - `gen-promotion-pack`
  - `gen-capability-audit-pack`
- core planner JSON now carries:
  - `planner_evidence_lane`
  - `planner_evidence_lane_fit`
- claim/promotion/audit/capability-audit outputs now keep the selected evidence
  lane visible in JSON and human docs
- refresh scripts preserve explicit evidence lanes so reruns do not silently
  fall back to the flagship default
- fixed a regression path introduced while wiring the feature into
  `plan-project` / strategy JSON
- kept cycle risk under control by moving target-fit imports behind the
  functions that actually need them

## Why it matters

Linux-native support claims are often lane-specific. A healthy current machine
is not automatically valid proof for GNOME Wayland, KDE Wayland, sway/wlroots,
Hyprland, or X11 fallback interchangeably. This revision lets VHK ask the more
honest question directly: how does *this* machine fit *this* chosen lane?

## Validation

Focused coverage now includes:
- `tests/test_plan_project_cli.py`
- `tests/test_claim_pack_cli.py`
- `tests/test_promotion_pack_cli.py`
- `tests/test_capability_audit_pack_cli.py`

Broader regression coverage also passed across:
- `tests/test_release_stage_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_host_rehearsal_pack_cli.py`
- `tests/test_host_dossier_pack_cli.py`
