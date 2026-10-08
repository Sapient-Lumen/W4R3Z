# Claim pack

`vhk gen-claim-pack <project_dir>` turns planner output into explicit support-claim artifacts:

- `docs/VHK_CLAIM_GUIDE.md`
- `docs/VHK_TARGET_CLAIMS.yaml`
- `docs/VHK_CLAIM_AUDIT_PLAN.json`
- `scripts/vhk_audit_claims.sh`

Why this exists:

- Linux automation tools rarely support every desktop/session equally.
- VHK already knows this in `plan-project`, `gen-portability-pack`, and the target rollout.
- Teams still need a place to write down what they are actually willing to claim in release notes, support docs, and package metadata.

The generated claim manifest seeds each target with:

- a `recommended_level`
- an editable `claim_level`
- current blockers/caveats
- required proof artifacts
- review commands

Use `vhk audit-target-claims <project_dir>` to compare the edited claim manifest against the current planner output.

The audit is intentionally conservative:

- stronger-than-recommended claims fail
- missing proof artifacts can fail stronger claims
- missing maintainer notes/evidence state produce warnings

This gives VHK a review surface for statements like:

- “X11/i3 is our reference lane”
- “GNOME Wayland is supported with caveats”
- “Portable text mode is experimental”
- “Hyprland is helper-boundary only for now”

Instead of pretending those judgments live only in README prose, the claim pack makes them explicit, editable, and checkable.
