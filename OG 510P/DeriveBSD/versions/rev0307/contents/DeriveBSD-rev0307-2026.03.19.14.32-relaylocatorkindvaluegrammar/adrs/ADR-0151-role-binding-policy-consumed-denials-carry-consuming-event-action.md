# ADR-0151: Role-binding policy-consumed denials carry the consuming event action

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`

## Context

ADR-0147 through ADR-0150 progressively removed the need to reopen the earlier successful remembered-role event body when a retry/export/support view hits `reason_code = policy-consumed`.
The denial can now identify the winning event, verify its canonical bytes, summarize the resulting binding digest, summarize the reviewed diff digest, and for updated winners summarize the replaced `previous_binding.digest`.

One small ambiguity still remains.
If `consumed_previous_binding_digest` is absent, detached tools still cannot tell whether the earlier winner was an `initialized` event, or whether they need to reopen the winner event body to learn its action before they know whether that absence is expected.

That keeps one more branch of retry/export logic ambient at exactly the boundary we are trying to make worth coding.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `intent.role.binding.event` now carries `consuming_event_action`
- `consuming_event_action` is required and is limited to `initialized` or `updated`
- `consuming_event_action` must equal the earlier successful consuming event's `action`
- if `consuming_event_action = updated`, `consumed_previous_binding_digest` is required
- if `consuming_event_action = initialized`, `consumed_previous_binding_digest` must be absent
- `recovery_interpretation = already-applied` remains allowed only when the same exact mutation tuple is still proven; for `updated` retries that still includes the old-side binding digest match from ADR-0150

## Consequences

This keeps successful events authoritative for the full winner body while making one more part of the winner shape queryable from detached denial evidence.
Support bundles, deterministic exports, and host-local retry logic no longer need to reopen the winner event body just to answer whether the winner was a first-write `initialized` event or a compare-and-swap `updated` event.

The action summary also makes the `consumed_previous_binding_digest` contract sharper:

- presence is no longer inferred indirectly from the winner body
- absence is no longer ambiguous
- updated winners keep the full old→new edge queryable from denial evidence alone

## Why this is the right cut

This is still a small evidence-shaping decision, not a new subsystem.
We do **not** add a generic result object, an idempotency ledger, or a new winner envelope.
We only surface the already-existing winner `action` so the rest of the denial summaries become mechanically interpretable.

That keeps A/B/C/D on one contract surface without growing a special workstation or fleet-only retry family.

## Implementation notes

- extend `spec/intent.role.binding.event.schema.json` with `consuming_event_action`
- keep the policy-window denial subtype aligned with the same requirement
- update the canonical `policy-consumed` denial example so `consuming_event_action = updated`
- guard the rule with a dedicated `tools/check_role_binding_policy_consumption_action_contract.py`

## References

- RFC 9110 (`If-None-Match: *` and `If-Match` distinguish create-vs-update safety and prevent lost-update ambiguity): https://www.rfc-editor.org/rfc/rfc9110
- Stripe idempotent requests (same request key returns the first result and parameter changes are treated as misuse): https://docs.stripe.com/api/idempotent_requests
