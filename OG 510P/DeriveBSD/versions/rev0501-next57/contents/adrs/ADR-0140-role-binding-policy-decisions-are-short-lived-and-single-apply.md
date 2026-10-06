# ADR-0140: Role-binding policy decisions are short-lived and single-apply

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/93-policy-decision-records.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`

## Context

ADR-0135 decided that non-interactive remembered-role changes join to `policy.decision` through `policy_decision_digest`.
ADR-0136 then made role-binding writes compare-and-swap.
ADR-0139 then required the joined policy record to bind the exact remembered-role mutation tuple.

That still left one more expensive ambiguity:
an exact-mutation policy decision could still behave like a durable reusable capability.
If the same tuple reappears later, or if a reconciler keeps a cached allow record around indefinitely, `policy_decision_digest` stops being a crisp explanation and starts becoming ambient authority.

## Decision

For remembered-role mutations that carry `policy_decision_digest`, the joined exact-mutation policy profile must also be short-lived and single-apply.
The archive tightens `spec/intent.role.binding.policy.profile.schema.json` so `effective_constraints.intent_role_binding_apply` now requires:

- `must_apply_before`
- `max_successful_events = 1`

Semantics:

1. a successful `intent.role.binding.event` with `action = initialized` or `updated` must occur no later than `must_apply_before`
2. only one such successful event may consume a given `policy_decision_digest`
3. `write-denied`, validation failure, or other non-success paths do not consume the allow record; they only prove that the attempted apply did not land
4. if the exact same mutation is still wanted after expiry or after one successful apply, the system must mint a fresh `policy.decision`

## Consequences

- `policy_decision_digest` now behaves like a compact apply grant instead of a reusable standing permission.
- A / C / D non-interactive role-binding paths stay implementable without inventing a separate transaction family: the event journal itself is enough to prove successful consumption, while the apply profile gives a concrete expiry boundary.
- Replay risk is reduced even when the same host/profile/binding tuple could recur later.
- Support bundles gain a sharper explanation: operators can tell whether a remembered-role mutation was denied because of stale state, because the decision expired, or because the decision had already been consumed by an earlier successful event.

## Not decided here

- per-request nonce / request-uid semantics for otherwise identical parallel role-binding requests
- distributed coordination details for enforcing consumption across replicas
- broader role-binding baseline distribution language
- richer actor/quorum receipts for shared admin workflows

## Follow-ups

- keep `docs/549-role-binding-policy-decisions-bind-exact-mutation.md` as the tuple-binding boundary
- use `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` as the freshness/consumption boundary
- guard the new rule with `tools/check_role_binding_policy_apply_window_contract.py`
