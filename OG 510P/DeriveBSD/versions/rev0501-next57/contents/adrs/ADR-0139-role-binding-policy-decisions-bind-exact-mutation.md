# ADR-0139: Role-binding policy decisions must bind the exact mutation

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/93-policy-decision-records.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/547-role-binding-support-import-join-via-content-import-receipt.md`, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`

## Context

ADR-0135 decided that non-interactive remembered-role changes join to `policy.decision` through `policy_decision_digest`.
ADR-0136 then made role-binding writes compare-and-swap.
ADR-0137 and ADR-0138 kept import provenance and authority lanes explicit.

That still left one implementability gap:
`policy_decision_digest` could identify **which** policy record was consulted without yet fixing **how tightly** that record had to bind the exact role-binding mutation.
A broad "role binding allowed" decision is not enough for A / B / C / D because it permits replay, weakens support-bundle explanations, and makes host-local admin viability in profile C too dependent on daemon or shell folklore.

## Decision

For remembered-role mutations that carry `policy_decision_digest`, the joined policy record must conform to a constrained role-binding policy profile.
The archive adds `spec/intent.role.binding.policy.profile.schema.json` and its canonical example.

The profile binds two compact surfaces:

1. `inputs.intent_role_binding_request`
   - names the authority/apply lane (`policy-reconcile` or policy-governed `support-import`)
   - names the subject host/profile
   - names the roles in scope
   - names the requested resulting binding digest
   - names the precondition digest for updates
   - names the import receipt digest when support/import policy is involved
2. `effective_constraints.intent_role_binding_apply`
   - names the exact apply mode (`initialized` or `updated`)
   - repeats the subject and required event trigger
   - binds the allowed resulting binding digest
   - binds the compare-and-swap precondition and diff digest for updates
   - binds the import receipt digest when the allow decision is specific to a support/import mutation

## Consequences

- `policy_decision_digest` now means both "which policy engine/inputs decided" and "which exact remembered-role mutation tuple was authorized".
- Profile C local-admin viability stays coherent without inventing a separate `admin-cli` authority lane: host-local tools still compile through the same exact-mutation policy profile.
- A / D maintenance or appliance reconcile flows stay auditable because import- or baseline-shaped policy decisions cannot be replayed across unrelated hosts or bindings without changing the typed tuple.
- The archive does **not** add a new admin transaction subsystem.
  It only narrows the existing `policy.decision` lane enough to be worth implementing.

## Not decided here

- broader role-binding baseline distribution language
- multi-host or org-shared quorum receipts
- batching multiple remembered-role objects into one higher-order transaction
- transport/auth details for admin tooling

## Follow-ups

- keep `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` as the lane decision
- use `docs/549-role-binding-policy-decisions-bind-exact-mutation.md` as the exact-mutation profile boundary
- guard the profile with `tools/check_role_binding_policy_profile_contract.py`
