# ADR-0150: Role-binding policy-consumed denials carry the consuming previous-binding digest

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`

## Context

ADR-0145 made remembered-role retries collapse to **already-applied** only when the earlier consuming success matches the same exact mutation tuple.
ADR-0148, ADR-0149, and ADR-0147 then exposed the winner's resulting binding digest, reviewed diff digest, and event digest directly on `policy-consumed` denials.

One exact-match member still stays hidden inside the earlier winner event body for `updated` retries: the starting binding digest that the winner compared against before it wrote the new remembered-role snapshot.
That keeps too much low-level join logic in support bundles and retry/export tooling for a lane we are already trying to make worth coding.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_previous_binding_digest` is carried when the earlier successful consuming event was an `updated` event
- `consumed_previous_binding_digest` is the earlier successful consuming event's `previous_binding.digest`
- the field is evidence-only summary data; it does **not** assert that the same prior binding is still current later
- `recovery_interpretation = already-applied` remains allowed only when the consuming success still matches the same exact mutation tuple, and for `updated` retries `consumed_previous_binding_digest` must therefore also equal the requested `from_binding_digest`

We do **not** reuse `previous_binding` on the denied event.
`previous_binding` remains reserved for successful `updated` events that actually wrote the new remembered-role snapshot.
The denial carries only a narrow summary of the earlier winner's compare-and-swap starting point.

## Consequences

- support bundles and deterministic exports can query the winner's full old→new edge without reparsing the earlier winner event body
- host-local admin and reconcile tooling get one more exact-match tuple member as portable evidence for **already-applied** recovery
- event semantics stay crisp because denied events still do not pretend to have authored or observed a new `previous_binding` object themselves

## Follow-up

- add `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` as the implementer-facing rule
- extend `spec/intent.role.binding.event.schema.json` and the policy-window denial subtype with the optional summary field
- update the canonical denial example so the field equals the consuming-success example's `previous_binding.digest`
- add a guardrail checker that keeps the docs/examples/schema wired together
