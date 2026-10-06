# ADR-0147: Role-binding policy-consumed denials carry a consuming-event digest

- Status: Accepted
- Date: 2026-03-18
- Deciders: DeriveBSD archive maintainers
- Consultation: `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/216-incident-snapshots-and-support-bundles.md`

## Context

ADR-0144 made `policy-consumed` denials point at the earlier successful consuming event through `consumed_by_event_id`.
ADR-0145 then fixed when that denial may collapse to **already-applied**: only when the joined consuming success proves the same exact mutation tuple.
ADR-0146 then made that derived retry story stable through `recovery_interpretation`.

That still leaves one more practical export gap.
An `event_id` is a good correlation handle, but by itself it is not a content-addressed verifier for offline bundles or copied evidence sets.
When support or regulatory reviewers receive a bundle away from the live event journal, they should be able to verify *which exact canonical event bytes* justified the retry interpretation, not merely trust an identifier string.

## Decision

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- the event must carry `consumed_by_event_digest` in addition to `consumed_by_event_id`
- `consumed_by_event_digest` is the digest of the canonical bytes of the earlier successful consuming `intent.role.binding.event`
- the digest and id must refer to the same earlier successful `initialized` or `updated` event instance
- `policy-expired` does **not** require this field
- this is an evidence join only; it does not add a new event family or distributed replay protocol

## Consequences

- offline bundles can verify the pointed-to consuming winner without trusting live log lookups
- support/export tooling gets a stable human handle (`consumed_by_event_id`) plus a stable verifier (`consumed_by_event_digest`)
- `already-applied` remains narrow because the digest-bound winner can be checked directly against bundled bytes
- the archive stays small: no new transaction object, no generic event digest requirement on every event, and no replica arbitration machinery

## Not decided here

- a generic digest-pointer field for every event family
- replica/global winner election for multi-node consume races
- whether future event envelopes grow a first-class self-digest field
- richer export-manifest embedding rules beyond carrying the winning event artifact itself when needed

## Follow-ups

- add `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` as the implementer-facing rule
- tighten `spec/intent.role.binding.event.schema.json` and `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- add a canonical consuming-success example and bind the denial example to it through `consumed_by_event_digest`
- wire the rule through support/evidence/risk/runbook/discovery surfaces
- guard the rule with `tools/check_role_binding_policy_consumption_digest_contract.py`
