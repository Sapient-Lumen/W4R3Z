# ADR-0191: Publish-session management return paths stay lease-exact

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` now says the active-share cue stays durable, the stop/revoke control stays on that same durable surface, stale copied/share handles fail closed after the lease ends, and a still-live share keeps a stable trusted-UI re-entry path. But one narrow ambiguity remained: that return path could still land on a generic sharing hub, the nearest active share, or a successor share using the same broad surface vocabulary instead of the exact bounded share instance that was still live.

The neighboring datacubes made that gap look real rather than cosmetic. Persistent return affordances are not fully truthful if they quietly retarget. History/return surfaces need stale-target discipline and compare-and-set style exactness, not just persistence. DeriveBSD already treats relay-backed temporary sharing as a lease-shaped bounded act; the trusted-UI return path should therefore bind back to that exact lease while it remains live.

## Decision

1. `net.publish.session.evidence.management_return_binding` is required.
2. The publish-session envelope requires `evidence.management_return_binding = lease-exact`.
3. The trusted-UI re-entry path for a still-live bounded share must resolve back to the active-share management surface for that exact `authority.lease_id`, not to a generic share home, a nearest-current-share view, or a successor lease.

## Consequences

- The compact publish-session receipt now says one exact thing about what the stable return path is allowed to target.
- UI/support/audit consumers no longer have to guess whether a persistent return affordance preserves bounded-share identity or merely reopens some broad sharing surface.
- This stays a narrow target-binding floor rather than a full browser-history / multi-tab / routing-stack model.

## Alternatives considered

- **Let any trusted sharing surface satisfy return persistence.** Rejected because persistent-but-fuzzy return still leaves operators guessing which live share they are back on.
- **Model full browser-history entry identity, parallel-tab reconciliation, and breadcrumb stacks now.** Rejected as too wide; the narrow floor is that the stable return path keeps lease identity exact while the share is live.
