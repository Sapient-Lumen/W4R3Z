# ADR-0149: Role-binding policy-consumed denials carry the consuming diff digest

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/542-role-binding-diff-as-review-surface.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`

## Context

ADR-0144 made remembered-role `policy-consumed` denials point at the earlier successful consuming event through `consumed_by_event_id`.
ADR-0147 then made detached-bundle verification portable by requiring `consumed_by_event_digest`.
ADR-0148 added `consumed_binding_digest`, so support/retry/export tooling can query the winner's resulting remembered-role snapshot digest without reopening the winner event body.

One practical review surface still stays hidden inside that earlier winner event: **which reviewed `intent.role.binding.diff` digest actually landed**.

That matters because the diff is the human review surface for remembered-role changes.
A detached support bundle can already prove which event won and what resulting binding digest it produced, but it still has to reopen the winner event body just to answer which reviewed change digest consumed the one-shot authorization.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_by_event_id` remains required
- `consumed_by_event_digest` remains required
- `consumed_binding_digest` remains required
- `recovery_interpretation` remains required
- `consumed_diff_digest` is now also required
- `consumed_diff_digest` is the earlier successful consuming event's `diff.digest`
- `consumed_diff_digest` is evidence-only summary data; it does **not** claim that the same diff is still pending, current, or reusable later
- `recovery_interpretation = already-applied` remains allowed only when the consuming success matches the same exact mutation tuple, and `consumed_diff_digest` must therefore also equal the requested reviewed diff digest for `updated` retries

`diff` on the denial remains the attempted/requested review surface for *this* denied event.
`consumed_diff_digest` is the winning review surface from the *earlier* consuming success.

## Consequences

Positive:

- the remembered-role lane keeps the reviewed change as a first-class portable handle, not just the resulting binding
- support bundles and deterministic exports can answer “which reviewed diff actually landed?” without reopening the winner event body first
- already-applied retry collapse gains a sharper review/evidence join without inventing a generic transaction or result object

Negative / trade-offs:

- one more evidence-only summary field exists on `policy-consumed` denials
- docs, examples, and guardrails must now keep the winner diff digest aligned with the consuming-success example

## Rejected alternatives

- reusing `diff` on the denial to mean both the requested and earlier consuming review surface
- forcing every bundle/query client to reopen the winner event body for diff identity
- inventing a broader generic transaction/result summary envelope

## Follow-up

- add `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` as the implementer-facing rule
- extend `spec/intent.role.binding.event.schema.json` and the policy-window denial subtype so `policy-consumed` requires `consumed_diff_digest`
- add a dedicated guardrail for the winner diff-digest summary and wire it into `tools/hygiene.py`

