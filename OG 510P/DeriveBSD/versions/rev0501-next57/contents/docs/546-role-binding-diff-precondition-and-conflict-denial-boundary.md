# Role-binding diff precondition and conflict denial boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

`docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`docs/542-role-binding-diff-as-review-surface.md` fixed `intent.role.binding.diff` as the compact review surface.
`docs/543-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable mutation trail.
`docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive approval join.
`docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed the non-interactive policy join.

This doc makes the next narrow hard decision:

> reviewed remembered-role diffs are also mutation preconditions, and stale writes must leave typed denial evidence instead of silently rebasing.

See also:
- ADR: `adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md`
- remembered state: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- review surface: `docs/542-role-binding-diff-as-review-surface.md`
- durable mutation event: `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- interactive approval lane: `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- non-interactive policy lane: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- denial precedence: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`

## Why this needs a hard decision

The archive can now say:

- what the remembered role/default snapshot is,
- what changed in reviewable form,
- which durable event recorded the mutation,
- and which approval/policy join authorized it.

But one implementation-risk cliff still remains:

- what happens when a trusted-settings UI, reconcile daemon, support import, or admin command tries to apply a diff that was built against an older binding snapshot?

Without a rule here, the product silently falls back into folklore:

- trusted settings silently rebases over a newer user or policy change,
- a reconcile daemon wins races because it writes later,
- support bundles cannot explain why an approved diff did not land,
- and the real concurrency model lives in implementation accidents instead of archive law.

A smaller answer is better than inventing a whole transaction subsystem.

## Accepted boundary

`intent.role.binding.diff.from_binding.digest` is now the mutation precondition.

That means a remembered-role mutation is compare-and-swap against the current authoritative binding digest:

- if `current_binding_digest == diff.from_binding.digest`, the mutation may apply
- otherwise the mutation must be denied and recorded as typed evidence

No silent rebase, hidden merge, or automatic background rewrite is part of the product boundary.

## Event rule

`intent.role.binding.event` now grows a small denial surface for stale writes:

- `reason_code`
- `observed_binding`

For v0:

- `action = updated` keeps the existing success path (`previous_binding`, `binding`, `diff`)
- `action = write-denied` now requires `diff` and `reason_code`
- `reason_code = precondition-failed` also requires `observed_binding`

This makes the denial mechanically explainable:

For non-interactive remembered-role mutations that also join `policy_decision_digest`, `precondition-failed` is now the *last* denial in the ladder, not the first: `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` requires policy-window validity (`policy-denied`, `policy-consumed`, `policy-expired`) to win before compare-and-swap stale-state checks.


- attempted change = `diff.digest`
- expected current snapshot = `diff.from_binding.digest`
- actual current snapshot at denial time = `observed_binding.digest`

## Why use compare-and-swap here

This follows well-understood optimistic-concurrency prior art:

- HTTP conditional writes use strong validators and `If-Match` to prevent the lost-update problem.
- Kubernetes uses object `resourceVersion` so only one concurrent update succeeds when multiple actors race.

DeriveBSD does not need to import either full subsystem.
It only needs the same discipline at the remembered-role boundary: reviewed writes apply against an expected current digest, or they fail explicitly.

## Product-shape fit without forks

- **A / secure fleet host:** policy reconcile can retry by generating a new diff against the latest snapshot instead of silently stomping newer state.
- **B / secure workstation:** a trusted-settings approval does not become authority to overwrite a newer role binding that landed while the user was deciding.
- **C / general-purpose OS:** explicit local-admin tooling gets the same honest behavior without importing a giant transaction engine.
- **D / appliance factory / regulatory:** reconcile/import lanes stay auditable because failed writes can prove both the attempted diff and the observed current state.

## Incident / support effect

When remembered-role behavior matters to a postmortem, support surfaces should now be able to show:

- the latest authoritative `intent.role.binding` digest,
- the attempted `intent.role.binding.diff` digest,
- the `intent.role.binding.event` showing `reason_code = precondition-failed`,
- the `observed_binding.digest` that blocked the write,
- and, when the denied mutation came from a support/import workflow, the same event's `import_receipt_digest` so operators can see exactly which typed import attempt lost the race.

That gives operators a practical answer to "why did the approved/policy-shaped role change not land?" without shell logs or daemon folklore. If the same attempt also carried a spent or expired joined policy decision, the policy-window denial wins instead and support should guide operators to re-issue authority before they bother rebuilding the diff. `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` now adds one more narrow complement on that spent-authority side for updated winners: `consumed_previous_binding_digest` keeps the earlier winner's replaced `previous_binding.digest` queryable without reopening the winner event body.

## What this does **not** decide

This doc does **not** decide:

- automatic retry or rebase policy after denial,
- which authority should win when two actors disagree about desired remembered state,
- a replayable settings transaction log,
- or richer actor/quorum graphs.

Those remain later bounded choices.

## References

- RFC 9110 conditional requests / `If-Match` (preventing the lost-update problem): https://www.rfc-editor.org/rfc/rfc9110
- Kubernetes optimistic concurrency with `resourceVersion` (only one concurrent update succeeds): https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/
- Android RoleManager API reference (explicit role ownership and request flow): https://developer.android.com/reference/android/app/role/RoleManager

## Related docs

- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r290
