# ADR-0145: Role-binding policy-consumed same-mutation retries collapse to already-applied

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`

## Context

ADR-0140 made remembered-role policy decisions single-apply.
ADR-0141 made independently issued decisions for the same exact tuple stay distinguishable.
ADR-0142 kept spent authorizations typed as `policy-consumed`.
ADR-0143 fixed denial precedence so `policy-consumed` beats later expiry and stale-state denial.
ADR-0144 then made `policy-consumed` denials point at the earlier successful consuming event through `consumed_by_event_id`.

That still leaves one more expensive ambiguity:
a retry after an uncertain transport/process failure can now prove **which** earlier event consumed the authorization, but the archive still does not say when that denial should be treated as a success-equivalent replay rather than a fresh failure.
If implementations answer that differently, support bundles and retry paths drift even when they agree on every prior field.

## Decision

For remembered-role non-interactive retries that receive `reason_code = policy-consumed`:

- implementations must resolve `consumed_by_event_id` to the earlier successful `intent.role.binding.event`
- they may collapse the denial to **already-applied** only when the consuming success matches the same exact mutation tuple
- the exact-mutation match is:
  - same `subject.host_id`
  - same `subject.profile_id`
  - same `trigger`
  - same resulting binding digest
  - same `previous_binding.digest` and `diff.digest` when the request shape is `updated`
  - same `policy_decision_digest`
  - same `import_receipt_digest` when the trigger lane is `support-import`
- if the consuming success cannot be resolved, or does not match that tuple, the outcome stays an ordinary `policy-consumed` denial
- this is a retry/reporting interpretation rule; it does not add a new event kind or a broader transaction protocol

## Consequences

- crash-retry and reconnect paths can become success-equivalent without weakening the single-apply authorization boundary
- support bundles can distinguish “already happened” from “spent by some different winner” using existing event evidence
- the remembered-role line gets idempotent recovery semantics without inventing a general idempotency-key family
- `policy-consumed` remains the durable event reason; `already-applied` is a derived interpretation once the consuming success is joined and verified

## Not decided here

- a generic idempotency token family across other subsystems
- replica coordination or winner election beyond the existing consuming-event pointer
- whether future event/export profiles carry a first-class `recovery_class`
- automatic fetch/caching policy for the consuming success event in every runtime

## Follow-ups

- add `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` as the implementer-facing rule
- tighten the `consumed_by_event_id` schema text and example notes to describe the exact-match recovery rule
- wire the rule through evidence/support/risk/runbook/discovery surfaces
- guard the rule with `tools/check_role_binding_policy_consumption_recovery_contract.py`
