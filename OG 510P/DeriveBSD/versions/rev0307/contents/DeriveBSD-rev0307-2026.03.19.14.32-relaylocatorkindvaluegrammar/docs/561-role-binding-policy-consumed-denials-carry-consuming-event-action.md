# Role-binding policy-consumed denials carry the consuming event action

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

`docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` already fixed that a remembered-role spent-authority denial must identify and verify the earlier winning event.
`docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, and `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` then made the winner's result/review/old-edge summaries directly queryable.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry `consuming_event_action`, and that action decides whether `consumed_previous_binding_digest` is required or forbidden.

See also:
- ADR: `adrs/ADR-0151-role-binding-policy-consumed-denials-carry-consuming-event-action.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- exact-match retry rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- stable recovery summary: `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- consuming old-edge summary: `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- examples: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`

## Why this needs a hard decision

After ADR-0150, a detached retry/export/support reader can already learn almost the full winner tuple from the denial itself:

- which exact successful event consumed the one-shot authorization,
- whether the bundled winner bytes verify,
- which resulting binding digest landed,
- which reviewed diff digest landed,
- and, for updated winners, which previous binding digest that winner replaced.

One small ambiguity still remains.
A denial that does **not** carry `consumed_previous_binding_digest` does not by itself tell the reader whether:

- the winner was an `initialized` event so no previous binding existed,
- or the reader still has to reopen the winner event body to discover the winner action before it knows whether the missing digest is expected.

That is too much ambient interpretation for a path we now expect support bundles, deterministic exports, and host-local retry logic to consume directly.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

1. `consuming_event_action` is required
2. `consuming_event_action` is limited to `initialized` or `updated`
3. `consuming_event_action` must equal the earlier successful consuming event's `action`
4. if `consuming_event_action = updated`, `consumed_previous_binding_digest` is required
5. if `consuming_event_action = initialized`, `consumed_previous_binding_digest` must be absent
6. `recovery_interpretation = already-applied` remains allowed only when the same exact mutation tuple is proven; for `updated` retries that still includes the old-side binding match from `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`

So the denial now says not only **which event won**, but also **what shape of remembered-role write that winner was**: whether the winner was a first-write `initialized` event or a compare-and-swap `updated` event.

## Why this is the right cut

This keeps the archive small.
We do **not** add a new success envelope, a result-object family, or a generic idempotency subsystem.
We only surface the winner action that already exists inside the joined consuming event.

That buys a lot of practical clarity:

- absence of `consumed_previous_binding_digest` becomes mechanically interpretable
- updated winners keep the full old→new edge queryable from denial evidence alone
- initialized winners no longer look like “maybe missing data” in detached bundle review

## Event semantics after this cut

`intent.role.binding.event` still keeps `action = write-denied` on the denial itself.
The new field is **not** a second action for the denial.
It is an evidence-only summary of the earlier successful consuming event's action.

That means the canonical spent-authority denial surface becomes:

- `reason_code = policy-consumed`
- `consumed_by_event_id`
- `consumed_by_event_digest`
- `consuming_event_action`
- `consumed_binding_digest`
- `consumed_diff_digest`
- `recovery_interpretation`
- and, only when `consuming_event_action = updated`, `consumed_previous_binding_digest`

That is a smaller and more deterministic surface than reopening the winner event body just to interpret whether the old-edge summary should exist.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile loops can explain whether the winning remembered-role write created baseline state or updated an existing binding without extra journal fetches.
- **B / secure workstation:** restore/support flows can present a stable retry explanation that distinguishes a first-write winner from an update winner.
- **C / general-purpose OS:** host-local admin tooling can render deterministic retry/help text without inventing a separate CLI transaction/result family.
- **D / appliance factory / regulatory:** detached bundle review can tell whether the authorized winner created state or updated prior state even when the live journal is unavailable.

## Review rule

When a remembered-role denial says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the denial plus the bundled winner event:

1. which earlier successful event id consumed the authorization?
2. do the bundled winner bytes verify against `consumed_by_event_digest`?
3. what action did that winner take: `initialized` or `updated`?
4. what resulting binding digest did that winner produce?
5. what reviewed diff digest did that winner apply?
6. if `consuming_event_action = updated`, does the denial also carry `consumed_previous_binding_digest`?
7. if `consuming_event_action = updated`, does that digest equal the winner's own `previous_binding.digest`?
8. if `recovery_interpretation = already-applied` for an updated retry, does `consumed_previous_binding_digest` also match the requested `from_binding_digest`?

If question 3 or 6 cannot be answered from the denial + bundled winner, the spent-authority summary surface is still too ambient.

## What this does **not** decide

This doc does **not** decide:

- a universal action-summary field for every event family,
- a generic winner/result envelope,
- a first-class `already-applied` event action,
- or replica/global winner election.

Those remain later bounded choices.

## References

- RFC 9110 (`If-None-Match: *` and `If-Match` distinguish create-vs-update safety and prevent lost-update ambiguity): https://www.rfc-editor.org/rfc/rfc9110
- Stripe idempotent requests (same request key returns the first result and parameter changes are treated as misuse): https://docs.stripe.com/api/idempotent_requests

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`

Last updated: 2026-03-18r291
