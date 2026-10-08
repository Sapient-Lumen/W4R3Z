# Host contract pack

`vhk gen-host-contract-pack <project_dir>` turns planner `host_requirements`
plus a live host probe snapshot into a reviewable deployment contract.

It writes:

- `docs/VHK_HOST_REQUIREMENTS.md`
- `docs/VHK_HOST_FIXUPS.md`
- `docs/VHK_HOST_PLAN.json`
- `scripts/vhk_review_host_contract.sh`

The goal is to keep Linux-native deployment work explicit:

- packages are only one lane
- service lifecycle is a separate lane
- permissions/groups are a separate lane
- portal routing and consent/session requirements are a separate lane

This pack is intentionally conservative. It is a review surface, not a promise
that VHK can auto-install or auto-enable every helper on every Linux desktop.
When you pass `--evidence-lane <profile-id>`, that selected proof lane stays
visible in the generated docs/JSON/review script so host review does not drift
back to the default flagship lane.
