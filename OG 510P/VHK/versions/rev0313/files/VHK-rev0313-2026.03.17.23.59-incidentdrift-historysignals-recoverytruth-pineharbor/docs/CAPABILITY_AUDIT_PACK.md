# Capability audit pack

`vhk gen-capability-audit-pack <project_dir>` turns session facts, helper boundaries, portal routing hints, and fallback routes into one reviewable audit surface.

Generated artifacts:

- `docs/VHK_CAPABILITY_AUDIT.md`
- `docs/VHK_CAPABILITY_FIXUPS.md`
- `docs/VHK_CAPABILITY_AUDIT_PLAN.json`
- `scripts/vhk_refresh_capability_audit_pack.sh`
- `build/capability-audit/<project>/README.md`
- `build/capability-audit/<project>/vhk_capability_audit_handoff.json`
- `build/capability-audit/<project>/collect_capability_audit.sh`

The pack deliberately joins four viewpoints that were already present in the repo but not previously shipped together:

1. `vhk doctor` session facts
2. host requirements / helper boundaries
3. readiness checks
4. activation fallback routes

That makes it easier to answer release questions such as:

- which capabilities are actually degraded or blocked on this desktop?
- which helper/service/permission boundaries are part of the install story?
- what is the conservative fallback route when one hotter surface is unavailable?
- do our target claims overstate what the current artifacts prove?

The handoff capture script is meant for repeatable review on a target host. It writes a fresh doctor/validate/plan snapshot plus regenerated audit docs into `reports/latest/`.
