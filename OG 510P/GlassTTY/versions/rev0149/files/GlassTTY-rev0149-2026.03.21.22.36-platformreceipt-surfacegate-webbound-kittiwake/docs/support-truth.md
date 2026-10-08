# Support truth

GlassTTY should make support claims at the level of **surface × workflow × browser lane**.

## Support tiers

- **unsupported** — no meaningful evidence or no implementation intent yet
- **investigated** — notes, profiles, or captures exist, but workflow support is not established
- **experimental** — at least one workflow path exists with partial evidence, but breakage is expected
- **provisional** — workflow has recent evidence and known caveats; support exists but is still brittle
- **supported** — workflow has recent evidence, release-gate coverage, and a stable support record

## Release-gate questions

Before strengthening a support claim, ask:

1. Was the workflow demonstrated on a real official browser surface?
2. Was the action visible and operator-traceable?
3. Did GlassTTY emit structured state and action outcomes?
4. Is there an evidence bundle that another implementer can inspect?
5. Does the evidence include navigation truth when route continuity matters?
6. Is the claim tied to a browser lane?
7. Is current known drift recorded?
8. Is the support record dated and actionable?

## Canonical support record shape

A support record should include:
- surface key
- browser lane scope
- workflow rows
- current tier per workflow
- evidence refs or evidence posture
- known caveats and blockers
- likely failure modes
- promotion requirements
- next recommended action

Use `docs/support-record-template.md` and `docs/support-records/*.md` for the living records.

## Important rule

Avoid all-or-nothing claims like “Surface X is supported.”
Prefer: “Surface X supports workflows A/B/C experimentally on `chromium-live`, with evidence refs Y/Z and caveats K/L.”

## Additional rule

Transient cues such as toasts, live-region status text, spinner changes, or brief overlays may support an interpretation, but they are not sufficient by themselves to strengthen a support tier. Prefer durable post-action state, route/history evidence, or inspectable turn/composer artifacts.
