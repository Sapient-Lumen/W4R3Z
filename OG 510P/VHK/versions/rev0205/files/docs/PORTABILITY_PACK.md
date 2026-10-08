# Portability pack

`vhk gen-portability-pack <project_dir>` turns `vhk plan-project`'s cross-desktop
comparison into reviewable artifacts for a real project.

Generated artifacts:

- `docs/VHK_PORTABILITY_GUIDE.md`
- `docs/VHK_TARGET_ROLLOUT.md`
- `docs/VHK_PORTABILITY_PLAN.json`
- `scripts/vhk_review_portability.sh`

Why this exists:

- Linux automation does not have one honest deployment target.
- The same VHK project can fit very differently on X11/i3, GNOME Wayland, KDE
  Wayland, and conservative wlroots/Hyprland targets.
- Teams need a place to review rollout order, portability gaps, and migration
  playbooks before they promise broad support.

What the artifacts contain:

- guide: target rollout order, capability coverage hot spots, portability gaps,
  migration playbooks, export surfaces, and optional current-session fit
- rollout worksheet: baseline refresh, target order, capability proof points,
  and handoff reminders to operator / verification / support packs
- JSON plan: the normal planner output plus `target_rollout`,
  `portability_commands`, and review-path metadata
- review script: captures `doctor` / `validate` / `plan-project`, regenerates
  the related planner-backed packs, and writes a portability review bundle

This command is intentionally a review surface, not a fake compatibility badge.
It helps VHK say which Linux targets it should claim first and what must change
before it claims the next one.
