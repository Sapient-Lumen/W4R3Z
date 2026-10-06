# ADR-0190: Publish-session return paths stay trusted-UI persistent

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` now says the active-share cue stays durable, the stop/revoke control stays on that same durable surface, and stale copied/share handles fail closed after the lease ends. But one more narrow ambiguity remained: a still-live share could become hard to manage as soon as the user left the active-share surface if return depended on browser back/history luck, a one-shot toast, or rediscovering the right route by hand.

The neighboring datacubes made that gap look real rather than cosmetic. Persistent status/control surfaces need a truthful re-entry path, not just a moment of visibility. DeriveBSD already treats relay-backed temporary sharing as a trusted-UI-mediated bounded act; it should not leave recovery of the active-share management surface to navigation folklore.

## Decision

1. `net.publish.session.evidence.management_return_path_posture` is required.
2. The publish-session envelope requires `evidence.management_return_path_posture = trusted-ui-persistent-until-ended`.
3. A still-live bounded share must keep a stable trusted-UI re-entry path back to the active-share management surface for the life of the session. Browser back/history luck, a one-shot toast/snackbar, or manual route rediscovery is not sufficient.

## Consequences

- The compact publish-session receipt now says one exact thing about how a user can get back to live-share controls after leaving the immediate surface.
- UI/support/audit consumers no longer have to guess whether a durable cue plus revoke button still left the session practically stranded once the surface was no longer frontmost.
- This remains a narrow management-surface continuity floor rather than a full browser-history / parallel-tab / overlay-navigation doctrine.

## Alternatives considered

- **Leave return/re-entry as generic UX guidance.** Rejected because the archive had already typed the active cue and live revoke affordance; leaving surface recovery implicit would keep one real operational property informal.
- **Model full history stacks, breadcrumb hierarchies, and multi-window coordination now.** Rejected as too wide; the narrow floor is that the active-share management surface stays reachable through a stable trusted-UI entry while the share is live.
