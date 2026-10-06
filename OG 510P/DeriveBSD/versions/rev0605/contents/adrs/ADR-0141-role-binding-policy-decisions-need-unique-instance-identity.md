# ADR-0141: Role-binding policy decisions need unique instance identity

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/93-policy-decision-records.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`

## Context

ADR-0139 required remembered-role `policy.decision` records to bind the exact mutation tuple.
ADR-0140 then required those decisions to be short-lived and single-apply.

That still left one more implementability cliff:
if the archive allows two independently issued remembered-role decisions to have identical content, they hash to the same `policy_decision_digest`.
That collapses separate issuance events into one digest even when operators intended two separate single-apply allow records.

In practice that makes several questions ambiguous:

- which issuance instance was actually consumed by the successful remembered-role write?
- how do we safely re-issue the same exact tuple after expiry or after a failed first attempt without mutating arbitrary unrelated fields?
- how do support bundles distinguish “the same authorization reused” from “a fresh authorization for the same tuple”?

## Decision

The remembered-role exact-mutation policy profile now requires a top-level `decision_instance_id`.

Semantics:

1. `decision_instance_id` is unique per independently issuable remembered-role policy decision
2. it participates in the content-addressed digest, so separately issued decisions remain separately consumable even when the exact mutation tuple and apply window are otherwise identical
3. successful remembered-role events still point only at `policy_decision_digest`; no new event field is required in this iteration
4. if the same exact remembered-role mutation is re-issued later, the new policy record must carry a fresh `decision_instance_id`

## Consequences

- The archive can now distinguish “same tuple, fresh issuance” from “same digest reused”.
- Single-apply consumption from ADR-0140 becomes implementable without inventing a larger transaction object.
- Support bundles and event review gain a compact answer for which issuance instance an event actually consumed.
- Profile C local-admin viability stays coherent because a host-local policy compiler can mint a fresh decision instance without inventing a separate admin-authority dialect.

## Not decided here

- the exact generator format for `decision_instance_id` (UUID, ULID, structured local id, etc.)
- broader distributed coordination mechanics for replica-safe consumption
- richer request/approval actor graphs
- any new event-family fields beyond the existing `policy_decision_digest` join

## Follow-ups

- keep `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` as the freshness/consumption boundary
- keep `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` as the issuance-identity boundary
- guard the new rule with `tools/check_role_binding_policy_instance_identity_contract.py`
