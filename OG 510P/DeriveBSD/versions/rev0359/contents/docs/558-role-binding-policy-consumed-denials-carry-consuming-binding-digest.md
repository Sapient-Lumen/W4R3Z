# Role-binding policy-consumed denials carry the consuming binding digest

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` already fixed that remembered-role spent-authority denials must point at the earlier successful consuming event through `consumed_by_event_id`.
`docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` then made that winner verifiable away from the live journal by requiring `consumed_by_event_digest`.
`docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` made the retry/export answer stable through `recovery_interpretation`.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry `consumed_binding_digest` so support bundles and retry logic can read the winner's resulting binding digest directly instead of reopening the consuming event first.

See also:
- ADR: `adrs/ADR-0148-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- consuming-event pointer: `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- exact-match recovery rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- stable recovery summary: `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- consuming-event digest: `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- denial example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`
- consuming success example: `spec/examples/intent.role.binding.event.policy-consume-success.json`

## Why this needs a hard decision

The archive can now tell operators which earlier successful event spent a remembered-role authorization and can verify the canonical bytes of that winner away from the live journal.
But one practical result still stays hidden inside the joined event body: **which resulting remembered-role binding digest did that winner produce?**

Without one more summary field:

- retry/reporting surfaces have to reopen the consuming event just to answer what binding actually landed,
- support bundles cannot query the winner result as a first-class value,
- and deterministic exports keep too much low-level join logic in every client.

That is too much repeated work for a lane we are already narrowing toward code-worthy behavior.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_by_event_id` remains required
- `consumed_by_event_digest` remains required
- `recovery_interpretation` remains required
- `consumed_binding_digest` is now also required
- `consumed_binding_digest` is the earlier successful consuming event's `binding.digest`
- the field is **evidence-only summary data**; it does **not** claim that the same binding is still current at some later read time
- `recovery_interpretation = already-applied` remains allowed only when the consuming success matches the same exact mutation tuple, and `consumed_binding_digest` must therefore also equal the requested resulting binding digest

This is intentionally narrow.
It does not create a generic mutation-result object or a universal event summary envelope.
It only exposes the winner's resulting binding digest on the denial that already depends on that winner.

## Why this is the right cut

`consumed_by_event_id` is the readable locator.
`consumed_by_event_digest` is the verifier for the bundled winner bytes.
`consumed_binding_digest` is the portable result handle.

Together they let support and retry tooling answer three different questions without ambiguity:

1. which event won?
2. can I verify that winner's bytes offline?
3. what resulting binding digest did that winner produce?

`docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now takes the next equally narrow step on top of this result summary by also making the winner's reviewed `diff.digest` portable through `consumed_diff_digest`.

That is the smallest addition that removes a repeated client-side join without pretending the denied event itself wrote a new binding.

## Why we do **not** reuse `binding`

Successful `initialized` and `updated` events own `binding` because they actually authored the new remembered-role snapshot.
A `write-denied` event did not write that snapshot.
Reusing `binding` on the denial would blur the difference between **the state this event created** and **the state an earlier winner created**.

`consumed_binding_digest` keeps that boundary clean:

- success events still say what they wrote through `binding`
- spent-authority denials still say what an earlier winner wrote through `consumed_binding_digest`

That keeps support/retry evidence richer without weakening event semantics.

## Event rule after this cut

For remembered-role non-interactive denial evidence:

- `policy-denied` — no exact joined authorization existed
- `policy-expired` — exact joined authorization existed but was too old
- `policy-consumed` — exact joined authorization existed but had already been spent, and the denial must carry `consumed_by_event_id`, `consumed_by_event_digest`, `consumed_binding_digest`, and `recovery_interpretation`
- `precondition-failed` — live authority remained, but compare-and-swap lost against newer remembered-role state

That keeps the denial ladder unchanged while making the spent-authority branch more directly queryable.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile retries can report the exact resulting binding digest that already landed without reopening the winner event body first.
- **B / secure workstation:** support/import bundles can show both the earlier winner event and the remembered-role digest it produced as separate queryable evidence.
- **C / general-purpose OS:** host-local admin tooling can treat exact-match retries as stable-result operations without inventing a separate transaction/result vocabulary.
- **D / appliance factory / regulatory:** detached evidence exports can prove both the winner event bytes and the resulting binding digest that justified **already-applied**.

## Review rule

When a remembered-role denial says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the denial plus the bundled winner event:

1. which earlier successful event id consumed the authorization?
2. what digest claims to identify that winner's canonical bytes?
3. what resulting binding digest did that winner produce?
4. do the bundled winner bytes verify against `consumed_by_event_digest`?
5. does the winner event's own `binding.digest` equal `consumed_binding_digest`?
6. if `recovery_interpretation = already-applied`, does `consumed_binding_digest` also match the requested resulting binding digest?

If question 5 or 6 cannot be answered, the spent-authority result summary is still too ambient.

## What this does **not** decide

This doc does **not** decide:

- a universal `result_digest` field for every event family,
- a live-state claim that the winning binding digest is still current later,
- replica/global winner election,
- or a broader generic idempotency/result-object subsystem.

Those remain later bounded choices.

## References

- Stripe idempotent requests (same key returns the first stored result for the same request instead of recomputing a new one): https://docs.stripe.com/api/idempotent_requests
- AWS Well-Architected REL04-BP04 (idempotent APIs should return the same response for the same token, even if the underlying system state has since moved on): https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- `spec/examples/intent.role.binding.event.policy-consume-success.json`

Last updated: 2026-03-18r289
