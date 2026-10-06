# Role-binding policy-consumed denials carry the consuming diff digest

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

`docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` already fixed that remembered-role spent-authority denials expose the earlier winner's resulting `binding.digest` through `consumed_binding_digest`.
`docs/542-role-binding-diff-as-review-surface.md` fixed that `intent.role.binding.diff` is the human review surface for remembered-role changes.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry `consumed_diff_digest` so support bundles and retry logic can read the winning reviewed `intent.role.binding.diff` digest directly instead of reopening the consuming event first.

See also:
- ADR: `adrs/ADR-0149-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- diff review surface: `docs/542-role-binding-diff-as-review-surface.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- exact-match recovery rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- stable recovery summary: `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- consuming-event digest: `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- consuming binding digest: `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- denial example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`
- consuming success example: `spec/examples/intent.role.binding.event.policy-consume-success.json`

## Why this needs a hard decision

The archive can already tell operators which event won, verify its canonical bytes offline, and expose the resulting remembered-role binding digest that winner produced.
But one practical review handle still stays hidden inside the joined winner event body: **which reviewed diff digest actually landed**.

Without one more summary field:

- support bundles have to reopen the winner event just to answer which reviewed change was applied,
- retry/export tooling can prove the winner result without being able to name the winner review surface directly,
- and `already-applied` explanations stay weaker than the archive's own `Registry→Diff→Gate` posture.

That is too much repeated join work for a lane we are already narrowing toward code-worthy behavior.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_by_event_id` remains required
- `consumed_by_event_digest` remains required
- `consumed_binding_digest` remains required
- `recovery_interpretation` remains required
- `consumed_diff_digest` is now also required
- `consumed_diff_digest` is the earlier successful consuming event's `diff.digest`
- the field is **evidence-only summary data**; it does **not** claim that the same diff is still pending or reusable later
- `recovery_interpretation = already-applied` remains allowed only when the consuming success matches the same exact mutation tuple, and `consumed_diff_digest` must therefore also equal the requested reviewed diff digest for `updated` retries

This is intentionally narrow.
It does not create a generic review-result object or a universal winner-summary envelope.
It only exposes the winning review surface on the denial that already depends on that earlier winner.

## Why this is the right cut

`consumed_binding_digest` answers **what resulting binding landed**.
`consumed_diff_digest` answers **which reviewed change digest landed**.
Those are not the same question.

Together with `consumed_by_event_id` and `consumed_by_event_digest`, support and retry tooling can answer four different things without ambiguity:

1. which event won?
2. can I verify that winner's bytes offline?
3. what resulting binding digest did that winner produce?
4. what reviewed diff digest did that winner apply?

That is the smallest addition that removes another repeated client-side join without pretending the denial itself authored a new diff or binding.

`docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` now takes the next equally narrow step on top of this review summary by also making the winner's replaced `previous_binding.digest` portable through `consumed_previous_binding_digest` for updated winners.

## Why we do **not** reuse `diff`

`diff` on the denial is still the review surface for **this denied attempt**.
A `write-denied` event may be talking about a retry, a mismatched replay, or another spent-authority attempt.
Overloading `diff` to also mean the earlier winning review surface would blur two different things:

- what this denied attempt proposed,
- and what the earlier consuming success actually applied.

`consumed_diff_digest` keeps that boundary clean:

- the denial's `diff.digest` still describes the denied attempt's review surface
- `consumed_diff_digest` describes the earlier winner's review surface

That keeps event semantics crisp while making support evidence sharper.

## Event rule after this cut

For remembered-role non-interactive denial evidence:

- `policy-denied` — no exact joined authorization existed
- `policy-expired` — exact joined authorization existed but was too old
- `policy-consumed` — exact joined authorization existed but had already been spent, and the denial must carry `consumed_by_event_id`, `consumed_by_event_digest`, `consumed_binding_digest`, `consumed_diff_digest`, and `recovery_interpretation`
- `precondition-failed` — live authority remained, but compare-and-swap lost against newer remembered-role state

That keeps the denial ladder unchanged while making the spent-authority branch more directly reviewable.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile retries can now report not only which remembered-role snapshot already landed, but also which reviewed diff digest produced it.
- **B / secure workstation:** support/import bundles can show the earlier winner event, the resulting binding digest, and the applied review diff as separate queryable evidence.
- **C / general-purpose OS:** host-local admin tooling can present exact-match retries as stable-result operations without reopening the winner event body just to rediscover the reviewed change.
- **D / appliance factory / regulatory:** detached evidence exports can prove both the winner bytes and the winning review-surface digest that justified **already-applied**.

## Review rule

When a remembered-role denial says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the denial plus the bundled winner event:

1. which earlier successful event id consumed the authorization?
2. what digest claims to identify that winner's canonical bytes?
3. what resulting binding digest did that winner produce?
4. what reviewed diff digest did that winner apply?
5. do the bundled winner bytes verify against `consumed_by_event_digest`?
6. does the winner event's own `diff.digest` equal `consumed_diff_digest`?
7. if `recovery_interpretation = already-applied`, does `consumed_diff_digest` also match the denied attempt's reviewed diff digest?

If question 6 or 7 cannot be answered, the spent-authority review summary is still too ambient.

## What this does **not** decide

This doc does **not** decide:

- a universal `result_diff_digest` field for every event family,
- a live-state claim that the winning diff is still pending or current later,
- replica/global winner election,
- or a broader generic transaction/result-object subsystem.

Those remain later bounded choices.

## References

- Stripe idempotent requests (same key returns the first stored result for the same request instead of recomputing a new one): https://docs.stripe.com/api/idempotent_requests
- AWS Well-Architected REL04-BP04 (idempotent APIs should return the same response for the same token, even if the underlying system state has since moved on): https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_prevent_interaction_failure_idempotent.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- `spec/examples/intent.role.binding.event.policy-consume-success.json`

Last updated: 2026-03-18r290
