# Role-binding policy-consumed same-mutation retries collapse to already-applied

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` already fixed that `policy-consumed` is the winning denial before later expiry or compare-and-swap stale-state denial.
`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` then fixed that spent-authority denial must point at the earlier successful consuming event through `consumed_by_event_id`.

This doc makes the next narrow hard decision:

> a remembered-role retry that hits `policy-consumed` may collapse to **already-applied** only when the referenced consuming success is proven to be the same exact mutation tuple.

See also:
- ADR: `adrs/ADR-0145-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- consuming-event pointer: `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- consuming-event digest: `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`

## Why this needs a hard decision

The archive can now explain a lot about remembered-role retries:

- which exact policy decision instance authorized the write,
- that the authorization is short-lived and single-apply,
- that a spent authorization stays typed as `policy-consumed`,
- and which earlier successful event consumed it.

But one implementation cliff remains.
A retry after a crash, timeout, disconnect, or uncertain local tool exit can now discover that **something already consumed the authorization**.
Without one more rule, implementations still diverge on the final operator story:

- some will report a hard failure,
- some will silently treat it as success,
- and some will guess from timestamps.

That is too much freedom for a boundary we are trying to make worth coding.

## Accepted boundary

For non-interactive remembered-role retries that receive `reason_code = policy-consumed`:

1. resolve `consumed_by_event_id` to the earlier successful `intent.role.binding.event`
2. verify that event against `consumed_by_event_digest` when working from detached bundles or exports
3. compare that consuming success against the exact requested mutation tuple
4. collapse the retry to **already-applied** only when the consuming success matches all relevant tuple members

The exact-match floor is:

- same `subject.host_id`
- same `subject.profile_id`
- same `trigger`
- same resulting binding digest, which `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` now surfaces directly as `consumed_binding_digest` on the denial
- same winner action shape, which `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` now surfaces directly as `consuming_event_action` on the denial
- same reviewed diff digest for `updated` retries, which `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now surfaces directly as `consumed_diff_digest` on the denial
- same `previous_binding.digest` and `diff.digest` when the request shape is `updated`, and `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` now surfaces that winner-side `previous_binding.digest` directly as `consumed_previous_binding_digest` on the denial
- same `policy_decision_digest`
- same `import_receipt_digest` when `trigger = support-import`

If the consuming success cannot be resolved, or mismatches any required tuple member, the outcome stays an ordinary `policy-consumed` denial.

## Why this is the right cut

This keeps the archive small.
We do **not** add a general idempotency-key subsystem, a new transaction object, or a second success event.
We only say how to interpret an existing denial once the archive already has enough evidence to prove it is a replay of the same exact mutation.

That is the narrowest decision that still buys practical recovery semantics.

## Event semantics after this cut

`intent.role.binding.event` does **not** gain a new action or reason code.
The durable event still says `reason_code = policy-consumed`.

What changes is the retry/reporting rule layered on top of existing evidence:

- `policy-consumed` + unresolved consuming event → remain `policy-consumed`
- `policy-consumed` + consuming event for a different exact tuple → remain `policy-consumed`
- `policy-consumed` + consuming event for the same exact tuple → surface the retry as **already-applied**

`docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` takes one more narrow step on top of that rule: `policy-consumed` denials now also carry `recovery_interpretation` so support/export surfaces can query the derived answer directly while `reason_code` remains the durable denial truth.

That keeps event storage simple while making client and support behavior deterministic.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile workers can retry safely after process/network faults and stop turning successful prior apply into noisy false-negative alerts.
- **B / secure workstation:** support/import restore workflows can tell the difference between “this restore already landed” and “some other change spent the authorization first”.
- **C / general-purpose OS:** host-local admin tooling can behave like a careful idempotent mutator without inventing a separate CLI transaction family.
- **D / appliance factory / regulatory:** deterministic support/export bundles can report “already applied by event X” instead of forcing operators to infer whether a line actually landed.

## Review rule

When a remembered-role retry is surfaced as **already-applied**, reviewers should be able to answer all of these from the denial plus the joined consuming success:

1. which exact decision instance was spent?
2. which successful event spent it?
3. did that success match the same subject/trigger/binding tuple?
4. if this was an update, did it also match the same prior binding and diff?
5. if this was support-import, did it match the same import receipt digest?

If any of those answers is missing, the retry should remain a visible `policy-consumed` denial instead of collapsing to success.

## What this does **not** decide

This doc does **not** decide:

- a general idempotency framework for every mutable subsystem,
- cross-replica winner election,
- a first-class `already-applied` event action,
- or whether future UIs should visually collapse `policy-consumed` + `recovery_interpretation = already-applied` by default.

Those remain later bounded choices.

## References

- IETF HTTPAPI Idempotency-Key draft (servers publish lifecycle/expiry rules and may distinguish duplicate request handling from mismatched re-use): https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07
- Stripe idempotent requests (same key returns the first result; changed parameters with the same key are treated as misuse): https://docs.stripe.com/api/idempotent_requests
- Stripe low-level error handling (retry the same request with the same idempotency key until the outcome is clear; change the key when changing parameters): https://docs.stripe.com/error-low-level

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r291
