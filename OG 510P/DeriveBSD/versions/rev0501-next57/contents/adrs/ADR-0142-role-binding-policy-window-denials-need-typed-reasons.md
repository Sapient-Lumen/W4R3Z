# ADR-0142: Role-binding policy-window denials need typed reasons

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`

## Context

ADR-0140 required remembered-role policy decisions to be short-lived and single-apply.
ADR-0141 then required unique `decision_instance_id` so re-issued decisions for the same exact mutation tuple do not collapse to the same digest.

That left one more implementation cliff:
when a non-interactive remembered-role apply attempt reaches the boundary with a joined `policy_decision_digest`, the archive still needs a typed answer for why the apply was refused.
If expired or already-consumed authorizations collapse into generic `policy-denied`, support bundles and replay can no longer distinguish:

- a policy engine that refused to mint an authorization in the first place,
- an authorization that existed but expired before apply,
- and an authorization that existed but had already been consumed by an earlier successful event.

## Decision

Extend `intent.role.binding.event.reason_code` with two more typed denial outcomes for remembered-role non-interactive apply attempts:

- `policy-expired`
- `policy-consumed`

Semantics:

1. these codes apply to `action = write-denied` remembered-role events that joined a concrete `policy_decision_digest`
2. `policy-expired` means the joined decision instance existed, but the apply happened after `must_apply_before`
3. `policy-consumed` means the joined decision instance existed, but an earlier successful `initialized` or `updated` event had already consumed its one allowed success
4. generic `policy-denied` remains for cases where policy evaluation refused to authorize the attempted mutation at all
5. no new event family is introduced; the existing `intent.role.binding.event` surface remains the durable evidence lane

## Consequences

- Support bundles can now distinguish “expired grant”, “already used grant”, and “never allowed” without daemon folklore.
- Fleet/factory reconcile loops gain a small typed retry surface instead of ambiguous generic denial logs.
- Profile C local-admin compilation through `policy.decision` stays viable without inventing a separate shell/admin error taxonomy.
- The short-lived single-apply rule from ADR-0140 becomes easier to implement, test, and explain.

## Not decided here

- distributed/global coordination mechanics for deciding which replica wins consumption
- any new policy-decision mutation surface that writes back consumption state into the policy record itself
- richer actor/quorum receipts
- any new request-transaction family beyond the existing event join

## Follow-ups

- keep `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` as the freshness/consumption boundary
- keep `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` as the issuance-identity boundary
- add `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` as the typed failure boundary
- guard the rule with `tools/check_role_binding_policy_denial_contract.py`
