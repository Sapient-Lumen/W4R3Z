# Role-binding policy-consumed denials carry a consuming-event digest

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

`docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` already fixed that remembered-role spent-authority denials must point at the earlier successful consuming event through `consumed_by_event_id`.
`docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` then fixed when that denial may collapse to **already-applied**: only when the joined consuming success proves the same exact mutation tuple.
`docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` made that retry/export answer stable through `recovery_interpretation`.

This doc makes the next narrow hard decision:

> remembered-role `policy-consumed` denials must also carry `consumed_by_event_digest` so offline bundles can verify the exact winner event bytes instead of trusting only an id pointer.

See also:
- ADR: `adrs/ADR-0147-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy join: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- consuming-event pointer: `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- exact-match recovery rule: `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- stable recovery summary: `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- schema: `spec/intent.role.binding.event.schema.json`
- subtype schema: `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- denial example: `spec/examples/intent.role.binding.event.write-denied.policy-window.json`
- consuming success example: `spec/examples/intent.role.binding.event.policy-consume-success.json`

## Why this needs a hard decision

The archive can now tell operators which earlier successful event spent a remembered-role authorization and whether a retry may be surfaced as **already-applied**.
But an `event_id` alone is still only a correlation handle.
It does not let an offline support bundle or deterministic export verify that the bundled winner event bytes are the same event instance that justified the denial's recovery story.

That is too much trust in local log lookup for a lane that is already trying to become code-worthy and export-worthy. `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` takes the next narrow result-summary step on top: once the winner bytes are verifiable, the denial should also expose that winner's `binding.digest` directly as `consumed_binding_digest` instead of forcing every reader to reopen the bundled winner event first.

## Accepted boundary

For remembered-role non-interactive `write-denied` events with `reason_code = policy-consumed`:

- `consumed_by_event_id` remains required
- `consumed_by_event_digest` is now also required
- `consumed_by_event_digest` is the digest of the canonical bytes of the earlier successful consuming `intent.role.binding.event`
- the pointed-to winner must still be an `initialized` or `updated` event in the same remembered-role mutation family
- `policy-expired` does not require this field
- `recovery_interpretation = already-applied` remains allowed only when that digest-bound winner also proves the same exact mutation tuple, and `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` now makes the winning reviewed diff digest queryable next to the winner-event verifier

This is intentionally narrow.
It does not introduce a generic event self-hash for every subsystem.
It only makes the remembered-role spent-authority join verifiable away from the live event journal.

## Why id plus digest is the right pair

`consumed_by_event_id` is still the right human/operator correlation handle.
It is short, readable, and easy to quote in logs, tickets, and support summaries.

`consumed_by_event_digest` adds the missing verifier:

- bundles can carry the winner event bytes and prove they match the denial's pointer,
- deterministic exports can survive path changes or journal sharding,
- and `already-applied` stops depending on ambient trust in event-id lookups.

That mirrors the wider archive pattern: a readable locator is useful, but a digest-bound artifact is what makes evidence portable and independently checkable.

## Event rule after this cut

For remembered-role non-interactive denial evidence:

- `policy-denied` — no exact joined authorization existed
- `policy-expired` — exact joined authorization existed but was too old
- `policy-consumed` — exact joined authorization existed but had already been spent, and the denial must carry both `consumed_by_event_id` and `consumed_by_event_digest`
- `precondition-failed` — live authority remained, but compare-and-swap lost against newer remembered-role state

That keeps the denial ladder unchanged while tightening the spent-authority branch into a content-addressed join.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile exports can prove exactly which successful event spent the decision even when operators inspect a detached bundle.
- **B / secure workstation:** support/import bundles can carry the winner event bytes plus the denial and verify the retry story offline.
- **C / general-purpose OS:** host-local admin tooling can show a readable event id while scripts verify the digest-bound winner from exported evidence.
- **D / appliance factory / regulatory:** audits can verify that the cited consuming event bytes match the denial without trusting a live database or mutable path.

## Review rule

When a remembered-role denial says `reason_code = policy-consumed`, reviewers should be able to answer all of these from the denial plus the bundled winner event:

1. which earlier successful event id consumed the authorization?
2. what digest claims to identify that winner's canonical bytes?
3. do the bundled winner bytes verify against `consumed_by_event_digest`?
4. does that same winner also justify `recovery_interpretation`, if one is present?
5. if the export is detached from the live journal, does the retry story remain independently checkable?

If question 3 or 5 cannot be answered, the evidence contract is still too ambient.

## What this does **not** decide

This doc does **not** decide:

- a universal `event_digest` field for all event families,
- replica/global winner election,
- signed event envelopes beyond the existing canonical-bytes hashing discipline,
- or how many winning-event artifacts support bundles should retain by default.

Those remain later bounded choices.

## References

- RFC 6920, *Naming Things with Hashes* (hash-based names let the binding between a reference and object be verified without trusting the retrieval path): https://www.rfc-editor.org/rfc/rfc6920.html
- OCI image-spec descriptor digest rules (a digest acts as a content identifier and retrieved content should be verified against it, especially from untrusted sources): https://github.com/opencontainers/image-spec/blob/main/descriptor.md

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`
- `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`
- `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`
- `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.write-denied.policy-window.schema.json`
- `spec/examples/intent.role.binding.event.policy-consume-success.json`

Last updated: 2026-03-18r289
