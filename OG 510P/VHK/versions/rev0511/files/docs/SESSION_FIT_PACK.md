# Session fit pack

`vhk gen-session-fit-pack <project_dir>` joins the planner's project-shape view
with the current session capability matrix.

It generates:

- `docs/VHK_SESSION_FIT.md`
- `docs/VHK_SESSION_FIXUPS.md`
- `docs/VHK_SESSION_PLAN.json`
- `scripts/vhk_review_session_fit.sh`

Use it when you need to answer:

- Is this project actually ready on **this** host?
- Which required capabilities are blocked or degraded here?
- Which helper/bootstrap groups are relevant to fixing that?

The generated docs intentionally stay conservative. They are a host-review and
fixup surface, not a universal installer. Package names remain best-effort and
desktop-specific consent/permission flows still need review. When you pass
`--evidence-lane <profile-id>`, that selected proof lane stays visible in the
generated docs/JSON/review script so reruns do not silently revert to the
flagship default.
