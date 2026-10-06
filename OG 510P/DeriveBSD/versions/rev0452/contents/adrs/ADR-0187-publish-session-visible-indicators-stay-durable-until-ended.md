# ADR-0187: Publish-session visible indicators stay durable until ended

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` already says relay-backed temporary sharing is leased, revocable, reboot-cleared, and visible. But the compact evidence surface still expressed that visibility as a boolean `evidence.visible_indicator`. That was too weak for the archive’s own product story: a brief toast, one-time banner, or other transient flash could satisfy `true` even though the share remained active long after the cue disappeared.

The neighboring datacubes reinforced the right narrow cut here: if a compact outward/public-facing receipt says a user-visible cue existed for an active bounded act, the cue needs durable lifetime semantics instead of a one-shot announcement posture. DeriveBSD already says workstation support/share surfaces must be visible and revocable; it should not leave “visible” semantically under-specified inside the receipt itself.

## Decision

1. `net.publish.session.evidence.visible_indicator` is replaced by typed `evidence.visible_indicator_posture`.
2. The publish-session envelope requires `evidence.visible_indicator_posture = durable-until-ended`.
3. A transient toast/snackbar/flash is not sufficient evidence for the active publish-session cue. The visible share indicator must remain present for the lifetime of the active bounded share until the session ends.

## Consequences

- The compact publish-session receipt now says one exact thing about visible-share state instead of a weak boolean.
- UI/support/audit consumers no longer have to guess whether `visible_indicator = true` meant a durable active-share marker or a short-lived announcement that already vanished.
- Immediate stop/revoke affordance remains an adjacent UI requirement, but this ADR at least fixes the durability floor of the visible indicator itself.

## Alternatives considered

- **Keep boolean `evidence.visible_indicator`.** Rejected because it lets transient message posture masquerade as lifetime-visible share state.
- **Model the full indicator/revoke UI contract now.** Rejected as too wide for this round; the narrow fix is to type the durability floor first.
