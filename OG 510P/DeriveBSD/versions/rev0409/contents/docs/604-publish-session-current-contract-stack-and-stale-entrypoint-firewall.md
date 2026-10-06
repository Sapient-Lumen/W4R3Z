# Publish-session current contract stack and stale entrypoint firewall
**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability  
**Patterns:** Registry→Diff→Gate, Bundles  

- Status: Accepted
- Date: 2026-03-20
- Tags: publish-session, archive-control, discovery, hygiene
- Related: `adrs/ADR-0194-publish-session-current-contract-stack-stays-canonical-and-pointer-backed.md`
Last updated: 2026-03-20r334

## What this changes

The recent publish-session tightening cluster is now dense enough that nearby entry docs and numbered publish-session pages can accidentally turn into stale partial companion lists.

This document fixes one canonical **current-stack map** for the recent `docs/593-*` through `docs/603-*` cluster and acts as a stale entrypoint firewall: local docs may stay useful, but they should point back here instead of each acting like the full current register.

This is archive-control only.
It does **not** widen `net.publish.session`, and `session_version` stays `0.33`.

## Canonical current-stack map

- `docs/593-publish-session-organization-user-shares-stay-organization-scoped.md`
- `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`
- `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`
- `docs/596-publish-session-notes-stay-off-baseline-envelope.md`
- `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md`
- `docs/598-publish-session-post-end-access-stays-fail-closed.md`
- `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`
- `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`
- `docs/601-publish-session-management-return-paths-stay-lease-exact.md`
- `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`
- `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`

## Why this is worth doing

Once a contract cluster gets dense enough, stale local summaries become their own form of ambiguity.
A maintainer following one adjacent doc should not have to guess whether its local companion list is current.
One compact canonical current-stack map is the smaller and safer floor.

## Wire-up points

- `README.md`
- `CHANGELOG.md`
- `docs/00-index.md`
- `docs/98-archive-hygiene.md`
- `docs/99-llm-runbook.md`
- `docs/110-juicy-os-lessons.md`
- `docs/266-open-questions-and-risk-register.md`
- `tools/check_publish_session_current_stack_contract.py`

## Related

- `adrs/ADR-0194-publish-session-current-contract-stack-stays-canonical-and-pointer-backed.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`
