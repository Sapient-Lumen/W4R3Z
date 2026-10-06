# Role-binding retries need a stable recovery interpretation field

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` already fixed that remembered-role spent-authority denials must point at the earlier successful consuming event through `consumed_by_event_id`.
`docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then fixed when that denial may be treated as **already-applied**: only when the consuming success proves the same exact mutation tuple.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry a stable `recovery_interpretation` summary so support/export tooling does not have to re-derive the retry story from raw joins.

See also:
- ADR: `adrs/ADR-0146-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- consuming-event pointer: `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- exact-match recovery rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- consuming binding digest summary: `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`

## Why this needs a hard decision

The archive can now prove the right retry semantics, but it still leaves one costly freedom point open.
A support bundle reader or reconcile client can infer **already-applied** by joining `consumed_by_event_id` and checking the exact tuple, yet nothing forces implementations to expose that derived answer the same way.
One client may show success, another may show a raw spent-authority denial, and a third may bury the answer in notes.

That is too much UI/reporting drift for a boundary we are trying to make worth coding.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `recovery_interpretation` is required
- allowed values are:
  - `policy-consumed`
  - `already-applied`
- the field is an **evidence-only summary**; it never changes the durable event `action` or `reason_code`
- `recovery_interpretation = already-applied` is allowed only when `consumed_by_event_id` resolves to an earlier successful event, that success matches the same exact mutation tuple from `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `consumed_binding_digest` therefore matches the winner's `binding.digest`, `consumed_diff_digest` therefore matches the winner's `diff.digest`, and for updated retries `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` now also requires `consumed_previous_binding_digest` to match the winner's `previous_binding.digest`
- otherwise the field must stay `policy-consumed`

This is intentionally narrow.
It does not add a new event family or a generic outcome framework.
It only makes the already-decided recovery interpretation stable and queryable.

## Why this is the right cut

The archive already treats many support/export surfaces as digest-bound summaries rather than raw forensic archaeology.
This field does the same thing for remembered-role retry semantics:

- durable evidence still says the apply attempt was denied because the authorization was already spent,
- `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` now makes the consuming-event join portable through `consumed_by_event_digest`, and `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now makes the winning reviewed diff portable through `consumed_diff_digest`,
- the digest-bound consuming-event join plus `consumed_binding_digest` / `consumed_diff_digest` still prove whether it was the *same* mutation and which reviewed change actually landed,
- `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` now also adds `consuming_event_action` so detached readers can tell whether the winner was `initialized` or `updated` and can interpret whether the old-edge summary must exist,
- and `recovery_interpretation` gives operators and tools one stable field to read once that proof exists.

That keeps the semantics small without forcing every client to rebuild the same exact-match logic ad hoc.

## Event rule after this cut

For the remembered-role non-interactive denial ladder:

- `reason_code = policy-denied` → no joined exact authorization existed
- `reason_code = policy-expired` → joined exact authorization existed but was too old
- `reason_code = policy-consumed` + `recovery_interpretation = policy-consumed` → authorization was already spent and exact-match replay collapse was not proven
- `reason_code = policy-consumed` + `recovery_interpretation = already-applied` → authorization was already spent, and the pointed-to winner proves the same exact mutation tuple
- `reason_code = precondition-failed` → live authority remained, but compare-and-swap lost against newer binding state

That keeps `reason_code` authoritative for the durable denial ladder while making recovery semantics stable for bundle/query surfaces.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile loops can report deterministic replay success-equivalence without hiding true spent-authority conflicts.
- **B / secure workstation:** support/import bundles can say “already applied” explicitly while preserving the underlying denial evidence and consuming-event pointer.
- **C / general-purpose OS:** host-local admin tooling gets one stable field to show in CLI/GUI status instead of recomputing from notes.
- **D / appliance factory / regulatory:** exported evidence can present a compact retry story that remains queryable and auditable in offline review.

## Review rule

When a remembered-role denial carries `recovery_interpretation`, reviewers should be able to answer all of these from the denial plus the joined consuming success:

1. what durable denial reason was recorded?
2. what recovery interpretation was surfaced?
3. which earlier successful event consumed the authorization?
4. did that winner prove the same exact mutation tuple?
5. if the interpretation says `already-applied`, can the bundle still prove *why* that summary was allowed?

If question 5 cannot be answered from bundle evidence, the summary field is too loose.

## What this does **not** decide

This doc does **not** decide:

- a generic `recovery_interpretation` field for every event family,
- a new success event action,
- replica/global result synthesis,
- or whether UIs should visually collapse `policy-consumed` + `already-applied` by default.

Those remain later bounded choices.

## References

- Stripe idempotent requests (same key returns the first result; retries are meant to recover a definitive answer, not perform the mutation twice): https://docs.stripe.com/api/idempotent_requests
- AWS Well-Architected REL04-BP04 (idempotent services should return the same response for the same request token, making retries operationally transparent): https://docs.aws.amazon.com/wellarchitected/2023-04-10/framework/rel_prevent_interaction_failure_idempotent.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`

Last updated: 2026-03-18r291
