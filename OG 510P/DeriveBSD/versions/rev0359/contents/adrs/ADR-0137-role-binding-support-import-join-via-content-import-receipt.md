# ADR-0137: Role-binding support-import join via content.import.receipt

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`adrs/ADR-0132-role-binding-diff-as-review-surface.md` fixed `intent.role.binding.diff` as the compact review surface.
`adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable mutation trail.
`adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed `policy_decision_digest` as the non-interactive authority join.
`adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md` fixed compare-and-swap apply semantics.

But the event family still had a real gap:

- `intent.role.binding.event` already allowed `trigger = support-import`
- the archive already has a typed safe-open intake lane through `content.import.plan` / `content.import.receipt`
- yet nothing in the remembered-role event trail could prove **which import actually produced the mutation**

That left a subtle but expensive ambiguity.
A support/import/recovery event could point at policy or stale-write evidence, but still lose the concrete intake provenance.
Support bundles would have to infer the import source from side logs or operator memory.

The archive already decided elsewhere that foreign support bundles and similar risky imported artifacts must stay on the generic `content.import.receipt` lane rather than host-open folklore.
The remembered-role family should reuse that same evidence lane instead of inventing a new import receipt family.

## Decision

1. `intent.role.binding.event` is extended with optional `import_receipt_digest`.
2. If `trigger = support-import`, `import_receipt_digest` is required.
3. `import_receipt_digest` joins to the existing generic import evidence lane:
   - normally a `content.import.receipt`
   - often the support-bundle specialization of that lane
4. `support-import` events may still carry `policy_decision_digest` when replay/import policy explicitly governed the mutation.
5. `support-import` events still follow the same compare-and-swap rule ADR-0136 fixed; stale imports deny instead of silently rebasing.
6. This ADR does **not** invent a new restore/transaction family and does **not** require embedding raw path/origin blobs inside the role-binding event.

## Consequences

- The support/import path becomes queryable: operators can answer which exact typed import receipt produced or attempted a remembered-role mutation.
- Support bundles and event-journal exports can carry one compact chain for imported remembered state:
  - `content.import.receipt`
  - optional `policy.decision`
  - `intent.role.binding.diff`
  - `intent.role.binding.event`
- The archive stays coherent across A/B/C/D:
  - B may restore remembered workstation defaults under maintenance/support workflows without turning support import into desktop folklore
  - A/C/D keep non-interactive import/replay explicit without inheriting workstation prompts
- The archive also gets a small entropy reduction: event-subtype profile schemas now exist for the shipped `policy-reconcile`, `support-import`, and `write-denied.precondition` examples, so example validation no longer has to warn about unmatched example names.

## Follow-up intentionally left open

This ADR still does **not** decide:

- whether every support/import mutation must always carry `policy_decision_digest`
- richer actor/quorum attribution for import-driven remembered-role changes
- or a bigger restore transaction subsystem

Those remain future work if implementation pressure proves they are needed.

## Related

- `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`
- `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.support-import.schema.json`
