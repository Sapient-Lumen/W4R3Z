# ADR-0192: Publish-session post-end management return stays lease-exact-ended

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` now says the active-share cue stays durable, the stop/revoke control stays on that same durable surface, a still-live share keeps a stable trusted-UI re-entry path, that live return path stays bound to the exact `authority.lease_id`, and stale copied/share handles fail closed after the lease ends. But one narrow ambiguity remained: the archive still did not say what a surviving trusted-UI return path or management deep link was allowed to do after that exact bounded share ended.

The neighboring datacubes made that gap look real rather than cosmetic. Stale-link recovery and history-return surfaces need exact recovery state, not just live-state exactness. If the same trusted UI path later falls through to a generic share hub, a successor lease, or a blank miss, support/export/audit consumers still have to guess what happened to the original bounded act.

## Decision

1. `net.publish.session.lifecycle.post_end_management_return_posture` is required.
2. The publish-session envelope requires `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed`.
3. If a surviving trusted-UI return path, browser-history entry, or management deep link for that bounded share is followed after the lease ended, it must resolve to the explicit ended/revoked/expired state for that same `authority.lease_id`, not to a generic share home, a successor lease, or a blank “not found” miss that destroys bounded-share identity.

## Consequences

- The compact publish-session receipt now says one exact thing about post-end management return semantics instead of leaving them to UI folklore.
- Live exactness and post-end exactness now compose: the return path is lease-exact while live, and lease-exact-ended if followed after end.
- This stays a narrow recovery-state floor rather than a full browser-history or multi-tab model.

## Alternatives considered

- **Let post-end management return disappear into generic sharing or a blank miss.** Rejected because it destroys the identity of the bounded share precisely when operators/support most need an exact ended explanation.
- **Require the trusted-UI return affordance itself to persist after end.** Rejected as too wide; the narrow floor is what any surviving return path is allowed to resolve to if followed after end.
