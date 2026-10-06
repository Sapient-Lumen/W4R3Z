# ADR-0136: Role-binding diff precondition and conflict denial

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`adrs/ADR-0132-role-binding-diff-as-review-surface.md` fixed `intent.role.binding.diff` as the compact review surface.
`adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable mutation trail.
`adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive approval join.
`adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed the non-interactive policy join.

That leaves one practical cliff before implementation:

- what stops two trusted writers from silently overwriting each other?
- what proves a reviewed diff was still based on the current binding when it applied?
- how do A / B / C / D stay coherent without inventing a bigger settings transaction subsystem?

The archive already has the right raw materials:

- `intent.role.binding.diff.from_binding.digest`
- `intent.role.binding.event`
- the existing `write-denied` action

So the smallest coherent move is to treat the diff's `from_binding` digest as the mutation precondition and make stale writes leave typed denial evidence instead of silently rebasing.

HTTP and Kubernetes both use the same underlying lesson: state-changing writes should carry a validator/precondition so parallel actors do not lose updates accidentally.

## Decision

Role-binding mutations are now compare-and-swap against the current binding digest.

The boundary is:

1. `intent.role.binding.diff.from_binding.digest` is not only a review aid; it is the required precondition for applying that diff.
2. A role-binding writer must compare the current authoritative binding digest with `diff.from_binding.digest` before mutating remembered state.
3. If the digests differ, the writer must deny the mutation rather than silently rebasing or auto-merging.
4. That denial is recorded as `intent.role.binding.event` with:
   - `action = write-denied`
   - `reason_code = precondition-failed`
   - the attempted `diff` digest
   - `observed_binding` pointing at the current authoritative binding digest seen at denial time
5. Successful `updated` events continue to record `previous_binding` and `binding`.
6. Interactive workstation changes may still carry `consent_receipt_digest`; non-interactive reconcile changes may still carry `policy_decision_digest`. The precondition rule applies to both.
7. No silent rebase, daemon-side merge, or background retry becomes part of the product boundary. If a policy or trusted UI wants to retry, it must generate a new diff against the new current binding.

## Consequences

- The archive now has a compact lost-update answer without inventing `intent.role.binding.apply.plan` or a replayable settings-operation subsystem.
- A / B / C / D can share one mutation rule: every remembered-role write is either an update against the expected snapshot or a typed denial against a newer observed snapshot.
- Incident/support surfaces can answer not only what diff was attempted, but which current binding blocked it.
- Trusted UI and reconcile daemons stay honest: they cannot quietly win races by rewriting a user's or policy's newer remembered default behind the archive's back.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- priority between competing authorities beyond "current digest wins unless a new diff is generated",
- richer actor/quorum attribution,
- a full settings transaction log,
- or mandatory automatic retry policy after `precondition-failed`.

Those remain later bounded choices.

## Related

- `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `adrs/ADR-0132-role-binding-diff-as-review-surface.md`
- `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`
- `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `spec/intent.role.binding.event.schema.json`
