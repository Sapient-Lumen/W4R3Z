# Role-binding support-import join via content.import.receipt

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/543-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable remembered-role mutation trail.
`docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed the non-interactive authority join as `policy_decision_digest`.
`docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` fixed compare-and-swap apply semantics.

This doc makes the next narrow hard decision:

> if remembered role/default state is changed by a support/import/recovery workflow, the durable event must point at the exact typed import receipt that produced the mutation.

See also:
- ADR: `adrs/ADR-0137-role-binding-support-import-join-via-content-import-receipt.md`
- durable event trail: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- non-interactive policy lane: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- compare-and-swap denial boundary: `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- safe-open support-bundle intake: `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`
- typed support-bundle import profiles: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`

## Why this needs a hard decision

The archive already had most of the remembered-role chain:

- snapshot: `intent.role.binding`
- review surface: `intent.role.binding.diff`
- durable mutation trail: `intent.role.binding.event`
- authority join for non-interactive reconcile: `policy_decision_digest`
- stale-write denial: `reason_code = precondition-failed`

But one trigger still had an evidence hole:

- `trigger = support-import`

Without a typed import join, that trigger would mean “some import happened somewhere.”
That is not enough for forensics or support.
It pushes operators back toward shell history, file paths, or ticket comments to answer a basic question:

> which imported artifact actually produced this remembered browser/mail change?

The archive already solved that problem elsewhere with `content.import.receipt`.
A remembered-role import should reuse that lane instead of inventing a parallel remembered-role import receipt or pretending `policy_decision_digest` alone explains the whole path.

## Accepted boundary

`intent.role.binding.event` now carries:

- `import_receipt_digest`

If `trigger = support-import`, that digest is required.

The digest joins to the existing import evidence family:

- usually `content.import.receipt`
- often the support-bundle specialization of the same lane

That means imported remembered-role state now has one compact proof chain:

1. typed import receipt proves what entered and how it was handled
2. optional `policy_decision_digest` proves why replay/import policy allowed it
3. `intent.role.binding.diff` proves the posture delta
4. `intent.role.binding.event` proves when the mutation landed or was denied

## Why `content.import.receipt` is the right join

This keeps the archive small and coherent:

- foreign or risky artifacts already enter through typed import receipts
- support-bundle intake is already quarantine-first and execution-bounded
- provenance/metadata survival already hangs off import receipts

So the remembered-role family does not need a parallel restore/import receipt dialect.
It just needs to point back to the receipt family DeriveBSD already trusts for imported evidence.

## Product-shape fit without forks

- **A / secure fleet host:** if maintenance or restore tooling applies remembered-role state at all, the import path stays typed and auditable instead of hiding behind daemon logs.
- **B / secure workstation:** maintenance/support restore of browser/mail ownership stays explainable without turning ordinary settings UX into a restore subsystem.
- **C / general-purpose OS:** local import/recovery remains viable, but imported remembered state still lands on the same typed evidence chain.
- **D / appliance factory / regulatory:** dedicated-device maintenance and recovery imports can stay offline/auditable by pointing at the exact import receipt and optional policy decision.

## Compare-and-swap still wins

This does **not** weaken the stale-write rule.
A support/import mutation still applies only if the current authoritative binding digest matches the diff precondition.
If it races with a newer remembered-role change, the event must still deny with:

- `action = write-denied`
- `reason_code = precondition-failed`
- `observed_binding`
- and, when `trigger = support-import`, the same `import_receipt_digest`

That keeps imported state from silently rebasing over fresher local decisions.

## Entropy reduction worth taking now

The archive already shipped specialized remembered-role event examples for:

- `policy-reconcile`
- `write-denied.precondition`

This revision adds matching profile schemas for those examples and for the new `support-import` example.
That removes lingering example-validation warnings and makes the supported event subtypes explicit without inventing a bigger event family.

## Practical bundle/export answers

With this boundary in place, support bundles can now answer all of these from typed evidence:

- which import receipt brought in the remembered-role payload?
- was the import allowed by policy or only staged for review?
- what exact diff was attempted?
- did the mutation land or deny because current state had already moved?

That is a much better implementation target than “look at the restore logs.”

## References

- Qubes OS backup/restore guide (explicit restore workflow, source selection, and verify-only path): https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-back-up-restore-and-migrate.html
- Qubes OS emergency backup recovery (portable recovery format and disaster-recovery focus): https://doc.qubes-os.org/en/latest/user/how-to-guides/backup-emergency-restore-v4.html

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`
- `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `spec/intent.role.binding.event.schema.json`
- `spec/intent.role.binding.event.support-import.schema.json`

Last updated: 2026-03-17r277
