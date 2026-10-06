# ADR-0193: Publish-session ended states stay terminal-cause exact

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` now says the active-share cue stays durable, the stop/revoke control stays on that same durable surface, a still-live share keeps a stable trusted-UI re-entry path, that live return path stays bound to the exact `authority.lease_id`, stale copied/share handles fail closed after the lease ends, and any surviving trusted-UI management return that is followed after end resolves to the explicit ended state for that same bounded share. But one narrow ambiguity remained: the archive still did not say whether explicit ended-share state had to preserve which declared end condition actually fired.

The neighboring datacubes made that gap look real rather than cosmetic. Typed recovery surfaces are weaker if they stop at “ended somehow” and erase whether the bounded share died by lease expiry, manual revoke, local-service loss, user session end, support/operator session end, maintenance-window end, or host reboot. Support/export/audit consumers should not have to reopen side logs or infer terminal cause from unrelated timing clues once the archive already carries an end-condition vocabulary.

## Decision

1. `net.publish.session.lifecycle.terminal_end_condition` is introduced.
2. If `ended_at` is present, `lifecycle.terminal_end_condition` is required.
3. If `ended_at` is absent, `lifecycle.terminal_end_condition` must be absent.
4. `lifecycle.terminal_end_condition` must stay within the existing publish-session `lifecycle.end_conditions` vocabulary and must name one of the declared end conditions for that bounded share.

## Consequences

- Explicit ended-share state now stays typed all the way to the exact terminal cause instead of flattening into a vague ended / expired / revoked label.
- This composes with the recent return-path and fail-closed work: stale handles fail closed, surviving management return stays exact, and the explicit ended state itself remains exact too.
- The change stays narrow: it does not introduce a new event log or causal timeline model, only a typed terminal-cause floor on the compact publish-session receipt.

## Alternatives considered

- **Leave terminal cause implicit in side logs or support interpretation.** Rejected because the archive already has a typed end-condition vocabulary and should not discard it at the moment the share ends.
- **Require a richer causal chain on the compact receipt.** Rejected as too wide; the narrow floor is to preserve the exact terminal cause, not to explain every contributing factor.
