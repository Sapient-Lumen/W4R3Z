# Role-binding policy-consumed denials carry the consuming previous-binding digest

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

`docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` already fixed that remembered-role spent-authority denials expose the earlier winner's reviewed `diff.digest` through `consumed_diff_digest`.
`docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` fixed that `intent.role.binding.diff.from_binding.digest` is the compare-and-swap precondition for `updated` remembered-role mutations.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry `consumed_previous_binding_digest` for `updated` winners, and `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` now makes that winner shape directly queryable through `consuming_event_action`, so support bundles and retry logic can read the winner's old side of the old→new binding edge directly instead of reopening the consuming event first.

See also:
- ADR: `adrs/ADR-0150-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`
- diff precondition boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- exact-match recovery rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- stable recovery summary: `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- consuming event digest: `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- consuming binding digest: `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`
- consuming diff digest: `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- denial example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`
- consuming success example: `spec/examples/intent.role.binding.event.policy-consume-success.json`

## Why this needs a hard decision

The archive can already tell operators which event won, verify its canonical bytes offline, expose the resulting remembered-role binding digest that winner produced, and expose the reviewed diff digest that winner applied.
But one exact-match tuple member for `updated` retries still stays hidden inside the earlier winner event body: **which previous binding digest did that winner compare against before it wrote the new binding?**

Without one more summary field:

- support bundles still have to reopen the winner event just to answer the starting side of the winning old→new edge,
- retry/export tooling can prove the winner result and reviewed diff without being able to query the winner's compare-and-swap precondition directly,
- and `already-applied` explanations stay one join away from the archive's own `Registry→Diff→Gate` posture.

That is too much repeated join work for a lane we are already narrowing toward code-worthy behavior.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_by_event_id` remains required
- `consumed_by_event_digest` remains required
- `consumed_binding_digest` remains required
- `consumed_diff_digest` remains required
- `recovery_interpretation` remains required
- `consumed_previous_binding_digest` is carried when the earlier successful consuming event was `action = updated`
- `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` now adds `consuming_event_action` so the denial also says whether that earlier successful consuming event was `initialized` or `updated`
- `consumed_previous_binding_digest` is the earlier successful consuming event's `previous_binding.digest`
- if `consuming_event_action = initialized`, `consumed_previous_binding_digest` must be absent
- the field is **evidence-only summary data**; it does **not** claim that the same previous binding is still current at some later read time
- `recovery_interpretation = already-applied` remains allowed only when the consuming success matches the same exact mutation tuple, and for `updated` retries `consumed_previous_binding_digest` must therefore also equal the requested `from_binding_digest`

This is intentionally narrow.
It does not create a generic compare-and-swap result object or a universal winner-summary envelope.
It only exposes the winner's previous binding digest on the denial that already depends on that earlier winner.

## Why this is the right cut

`consumed_binding_digest` answers **what resulting binding landed**.
`consumed_diff_digest` answers **which reviewed change landed**.
`consumed_previous_binding_digest` answers **which prior binding that winner proved before it landed**.

Those are not the same question.
Together with `consumed_by_event_id` and `consumed_by_event_digest`, support and retry tooling can answer five different things without ambiguity:

1. which event won?
2. can I verify that winner's bytes offline?
3. what resulting binding digest did that winner produce?
4. what reviewed diff digest did that winner apply?
5. which previous binding digest did that winner prove before it applied?

That is the smallest addition that removes another repeated client-side join without pretending the denial itself observed or authored a new previous-binding object.

## Why we do **not** reuse `previous_binding`

`previous_binding` on a successful `updated` event describes **the prior binding that this successful event actually replaced**.
A `write-denied` event did not replace that prior binding.
Reusing `previous_binding` on the denial would blur two different things:

- what this denied attempt was able to prove or observe directly,
- and what the earlier consuming success proved and replaced.

`consumed_previous_binding_digest` keeps that boundary clean:

- successful `updated` events still say what they replaced through `previous_binding`
- spent-authority denials only carry a narrow digest summary of what the earlier winner replaced

That keeps event semantics crisp while making exact-match retry evidence sharper.

## Event rule after this cut

For remembered-role non-interactive denial evidence:

- `policy-denied` — no exact joined authorization existed
- `policy-expired` — exact joined authorization existed but was too old
- `policy-consumed` — exact joined authorization existed but had already been spent, and the denial must carry `consumed_by_event_id`, `consumed_by_event_digest`, `consumed_binding_digest`, `consumed_diff_digest`, `recovery_interpretation`, and for `updated` winners `consumed_previous_binding_digest`
- `precondition-failed` — live authority remained, but compare-and-swap lost against newer remembered-role state

That keeps the denial ladder unchanged while making the spent-authority branch more directly queryable for the old→new update edge.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile retries can now report the exact old→new remembered-role edge that already landed without reopening the winner event body.
- **B / secure workstation:** support/import bundles can show the earlier winner event, the resulting binding digest, the reviewed diff digest, and the previous binding digest as separate queryable evidence.
- **C / general-purpose OS:** host-local admin tooling can present exact-match retries as stable-result operations without reparsing the winner event just to rediscover the compare-and-swap starting point.
- **D / appliance factory / regulatory:** detached evidence exports can prove the winning old→new binding edge that justified **already-applied**.

## Review rule

When a remembered-role denial says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the denial plus the bundled winner event:

1. which earlier successful event id consumed the authorization?
2. what digest claims to identify that winner's canonical bytes?
3. what resulting binding digest did that winner produce?
4. what reviewed diff digest did that winner apply?
5. what action did that winner take: `initialized` or `updated`?
6. if that winner was an `updated` event, what previous binding digest did it replace?
7. do the bundled winner bytes verify against `consumed_by_event_digest`?
8. does `consuming_event_action` match the bundled winner's own `action`?
9. if the winner was an `updated` event, does its own `previous_binding.digest` equal `consumed_previous_binding_digest`?
10. if `recovery_interpretation = already-applied` for an `updated` retry, does `consumed_previous_binding_digest` also match the requested `from_binding_digest`?

If question 7 or 8 cannot be answered for an `updated` retry, the spent-authority update summary is still too ambient.

## What this does **not** decide

This doc does **not** decide:

- a universal `previous_result_digest` field for every event family,
- a live-state claim that the winning previous binding is still current later,
- replica/global winner election,
- or a broader generic transaction/result-object subsystem.

Those remain later bounded choices.

## References

- RFC 9110 (`If-Match` and strong validators prevent the lost-update problem): https://www.rfc-editor.org/rfc/rfc9110
- Kubernetes optimistic concurrency via `resourceVersion` (only one concurrent update succeeds): https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md`

Last updated: 2026-03-18r291
