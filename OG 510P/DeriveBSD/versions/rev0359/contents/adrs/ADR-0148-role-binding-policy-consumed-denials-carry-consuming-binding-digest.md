# ADR-0148: Role-binding policy-consumed denials carry the consuming binding digest

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`

## Context

ADR-0144 made remembered-role `policy-consumed` denials point at the earlier successful consuming event through `consumed_by_event_id`.
ADR-0147 then tightened detached-bundle verification by requiring `consumed_by_event_digest`, so support exports can verify the exact winner event bytes away from the live journal.
ADR-0145 and ADR-0146 fixed the retry story on top of that evidence: only an exact tuple match may collapse the denial to **already-applied**, and `recovery_interpretation` now makes that answer stable and queryable.

One practical gap remains.
A bundle reader or retrying client can now prove **which event** won, but still has to reopen or replay that winner event just to learn the resulting remembered-role snapshot digest.
That keeps too much low-level join work in every support/export/retry implementation for a boundary we are already trying to make worth coding.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_binding_digest` is required
- `consumed_binding_digest` is the resulting `binding.digest` from the earlier successful consuming `intent.role.binding.event`
- `consumed_binding_digest` is evidence-only summary data; it does **not** assert that the same binding is still current at some later read time
- `recovery_interpretation = already-applied` remains allowed only when the consuming success still matches the same exact mutation tuple, and `consumed_binding_digest` must therefore also equal the requested resulting binding digest

We do **not** reuse the ordinary `binding` object on the denied event.
`binding` remains reserved for successful `initialized` / `updated` events that actually wrote the remembered-role snapshot.
The denial carries only a narrow summary of the earlier winner's result.

## Consequences

- support bundles and deterministic exports can say both **who won** and **what binding digest that winner produced** without reparsing the winner event first
- host-local admin and reconcile tooling get a stable result-handle for exact-match retries without inventing a broader idempotency/result object
- event semantics stay crisp because denied events still do not pretend to have authored a new binding snapshot

## Follow-up

- add `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` as the implementer-facing rule
- extend `spec/intent.role.binding.event.schema.json` and the policy-window denial subtype so `policy-consumed` requires `consumed_binding_digest`
- update the canonical denial example so the field equals the consuming success example's `binding.digest`
- add a guardrail checker that keeps the docs/examples/schema wired together
