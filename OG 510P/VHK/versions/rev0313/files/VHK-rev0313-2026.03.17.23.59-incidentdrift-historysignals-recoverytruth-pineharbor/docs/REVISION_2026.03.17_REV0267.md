# Revision REV0267 — evidence-lane host/session packs

This revision closes the next proof-context gap after REV0266: explicit
evidence lanes now survive into the host/session review packs instead of only
existing in planner/claim/audit/promotion flows.

## What changed

- fixed regressions where:
  - `gen-host-contract-pack` referenced an undefined `evidence_lane`
  - `gen-session-fit-pack` referenced undefined `host_snapshot` /
    `evidence_lane` values
- `gen-session-fit-pack` now accepts `--evidence-lane <profile-id>`
- `build_session_fit_plan()` / `write_session_fit_pack()` now carry one
  explicit evidence lane into generated JSON, markdown, and review scripts
- `build_host_contract_plan()` / `write_host_contract_pack()` now do the same
  for host-contract output
- generated review scripts preserve the explicit lane on rerun instead of
  silently falling back to the flagship default
- session-fit / host-contract docs now show the selected lane plus current fit
  summary directly in their snapshot sections

## Why it matters

VHK is trying to make Linux-native support claims honest. Session-fit and
host-contract packs are exactly the places where a maintainer checks “is this
box valid proof for this target lane?” If those packs drop the selected lane, a
GNOME/KDE/sway/Hyprland review can quietly turn back into generic flagship
proof.

## Validation

Focused coverage now includes:
- `tests/test_host_contract_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_claim_pack_cli.py`
- `tests/test_promotion_pack_cli.py`
- `tests/test_capability_audit_pack_cli.py`
