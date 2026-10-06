# ADR-0189: Publish-session revocation affordances stay same-surface durable

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` now says the active-share cue itself stays durable until the bounded share ends. But the compact receipt still left the actual stop/revoke control implicit. That gap is now the next real ambiguity: a share can be "visible" while the kill path lives in a transient toast action, a buried submenu, a different route, or some later log/support lookup.

The neighboring datacubes reinforced the right narrow cut here: durable visible state is not enough when the controlling next action can disappear with the same transient message posture or get stranded behind return-state/navigation drift. DeriveBSD already says workstation and support share lanes must be revocable and easy to stop; it should not leave the revoke affordance semantically under-specified inside the bounded receipt.

## Decision

1. `net.publish.session.evidence.revocation_affordance_posture` is required.
2. The publish-session envelope requires `evidence.revocation_affordance_posture = same-surface-durable-until-ended`.
3. The active bounded share must keep an immediate revoke/stop affordance on the same trusted-UI surface as the durable active-share cue for the life of the session. A transient toast action, buried overflow path, or off-surface detour is not sufficient.

## Consequences

- The compact publish-session receipt now says one exact thing about how the user can stop the active share, not just whether some cue once existed.
- UI/support/audit consumers no longer have to guess whether "easy to stop" meant a same-surface live control or a later scavenger hunt through menus or logs.
- This remains a narrow control-surface floor rather than a full multi-route/history-return UI doctrine.

## Alternatives considered

- **Leave stop/revoke as prose in product-shape docs.** Rejected because the archive had already typed the active-share cue; leaving the control itself untyped would keep the real safety property informal.
- **Model the entire return-state/history/parallel-tab story now.** Rejected as too wide for this round; the narrow fix is to keep the stop/revoke affordance durably present on the same active-share surface first.
