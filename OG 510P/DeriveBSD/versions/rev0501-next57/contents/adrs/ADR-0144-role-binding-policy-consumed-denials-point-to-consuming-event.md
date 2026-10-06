# ADR-0144: Role-binding policy-consumed denials point to the consuming success event

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`

## Context

ADR-0140 made remembered-role policy decisions single-apply.
ADR-0141 made independently issued decisions for the same exact tuple stay distinguishable.
ADR-0142 then made spent or expired decisions stay typed as `policy-consumed` or `policy-expired` rather than collapsing into generic denial.
ADR-0143 fixed the winning-denial order so `policy-consumed` stays primary even when a retry later also crosses expiry or stale-state conditions.

That leaves one more expensive ambiguity:
when a remembered-role denial says `policy-consumed`, support and retry logic still need to answer **which exact successful event spent the authorization**.
If that answer only exists by scanning event logs heuristically, implementations can diverge in what they surface to operators and support bundles become less deterministic than the archive intends.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- the event must carry `consumed_by_event_id`
- `consumed_by_event_id` identifies the earlier successful `intent.role.binding.event` instance that consumed the joined exact-mutation authorization
- the referenced consuming event must be an `initialized` or `updated` event for the same remembered-role mutation family
- `policy-expired` does **not** require `consumed_by_event_id`
- this is an evidence join only; it does not define replica/global arbitration mechanics

## Consequences

- support bundles can answer “spent by what?” without replaying the whole log by hand
- retry logic can distinguish “re-issue policy because this one was already spent” from “same process retried twice and lost the race”
- the remembered-role lane gains a narrow winner pointer instead of a larger transaction/replay subsystem
- `policy-consumed` remains a typed denial reason, and now also becomes a minimally actionable one

## Not decided here

- distributed/global winner selection or replica coordination for single-apply decisions
- whether future profiles also record a digest pointer to the consuming event bytes
- any broader actor/quorum receipt family
- generalized replay winner pointers outside the remembered-role lane

## Follow-ups

- add `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` as the implementer-facing rule
- extend `spec/intent.role.binding.event.schema.json` and the policy-window denial subtype so `policy-consumed` requires `consumed_by_event_id`
- update the canonical policy-window denial example to point at the successful consuming event
- guard the rule with `tools/check_role_binding_policy_consumption_pointer_contract.py`
