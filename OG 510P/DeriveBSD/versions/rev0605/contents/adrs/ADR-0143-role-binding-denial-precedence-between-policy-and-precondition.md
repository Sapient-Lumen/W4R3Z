# ADR-0143: Role-binding denial precedence is policy-window first, compare-and-swap second

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`

## Context

ADR-0136 made remembered-role writes compare-and-swap against `intent.role.binding.diff.from_binding.digest` and required stale writes to emit typed `precondition-failed` evidence.
ADR-0140 then made non-interactive remembered-role policy decisions short-lived and single-apply.
ADR-0141 required unique `decision_instance_id` so re-issued decisions for the same tuple stay distinguishable.
ADR-0142 then split joined-policy apply failures into `policy-expired` and `policy-consumed`.

That leaves one more implementation cliff:
a single non-interactive apply attempt can now satisfy more than one denial condition at the same time.
Examples include:

- the joined exact-mutation policy decision is already consumed **and** the reviewed diff is stale,
- the joined decision is already expired **and** the reviewed diff is stale,
- or a retry happens after both consumption and expiry have become true.

Without a precedence rule, different implementations will emit different `reason_code` values for the same real-world situation.
That would make support bundles, replay, and operator guidance drift even though the underlying state is the same.

## Decision

For remembered-role mutation attempts, denial reasons are evaluated in this order:

1. `policy-denied`
   - use when non-interactive policy never authorized the exact mutation at all, or when the required joined authorization is absent/invalid before apply
2. `policy-consumed`
   - use when the joined `policy_decision_digest` refers to a decision instance that was already consumed by an earlier successful `initialized` or `updated` event
3. `policy-expired`
   - use when the joined decision instance still identifies the exact mutation, but `at > must_apply_before`
4. `precondition-failed`
   - use only after the applicable policy-window checks above have passed and the current binding digest still does not match `diff.from_binding.digest`
5. otherwise the mutation may succeed

Additional rule:

- if more than one denial condition is true, emit the first matching `reason_code` in that order
- `policy-consumed` therefore wins over `policy-expired`
- both policy-window reasons win over `precondition-failed`
- interactive `trusted-settings-ui` flows that do not join `policy_decision_digest` skip the policy-window checks and therefore only use the consent + compare-and-swap path

## Consequences

- Non-interactive remembered-role apply logic now has one stable denial ladder instead of implementation-defined branch ordering.
- `precondition-failed` becomes the stale-state answer only after the mutation still has live authority to proceed.
- A consumed authorization never decays into a mere expiry story later; replay evidence stays replay evidence.
- Support bundles no longer need to guess whether a stale diff mattered when the joined authorization was already spent or too old.

## Not decided here

- distributed/global coordination mechanics for deciding which replica records successful consumption first
- whether implementations capture secondary non-winning denial facts anywhere beyond local diagnostics
- any richer request-transaction family or actor/quorum model

## Follow-ups

- add `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` as the implementer-facing rule
- guard the rule with `tools/check_role_binding_denial_precedence_contract.py`
- keep `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` as the typed reason vocabulary boundary
- keep `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` as the compare-and-swap boundary
