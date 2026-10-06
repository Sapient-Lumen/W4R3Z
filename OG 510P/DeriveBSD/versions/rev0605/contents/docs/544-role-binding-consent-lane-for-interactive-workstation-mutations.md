# Role-binding consent lane for interactive workstation mutations

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`docs/542-role-binding-diff-as-review-surface.md` fixed the compact review surface as `intent.role.binding.diff`.
`docs/543-role-binding-event-as-durable-mutation-evidence.md` fixed the durable mutation trail as `intent.role.binding.event`.

This doc makes the next narrow hard decision:

> interactive workstation role/default changes reuse the existing consent substrate instead of inventing a new settings-approval subsystem.

See also:
- ADR: `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- consent substrate: `docs/256-consent-ux-contract.md`
- approval posture: `docs/474-high-risk-approval-posture-by-profile.md`
- remembered state: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- review surface: `docs/542-role-binding-diff-as-review-surface.md`
- durable event trail: `docs/543-role-binding-event-as-durable-mutation-evidence.md`

## Why this needs a hard decision

Once remembered browser/mail ownership has a typed snapshot, a compact diff, and a durable event, the next likely drift point is authority evidence.
If interactive changes still happen as “whatever the trusted settings UI wrote,” the archive gains nice nouns but still loses the answer to a very practical question:

- did a real trusted-UI approval happen for this default change?

The archive already has a generic solution for human-mediated actions:

- `consent.request`
- `consent.receipt`

So the smallest coherent move is to reuse that substrate rather than inventing a workstation-only approval family.

## Accepted boundary

For interactive workstation role/default changes, the official constrained approval lane is now:

- `intent.role.binding.consent.request.profile`
- `intent.role.binding.consent.receipt.profile`

This lane is intentionally narrow.
It is for trusted-settings UI changes to remembered `browsing` / `communications` ownership on profile **B**.
It is **not** a claim that every future role-binding mutation across A/C/D must use the same prompt model.

## The request profile

The constrained request profile stays on top of generic `consent.request`, but fixes the minimum shape of what the human is approving.

It must bind:

- `action.kind = change.confirm`
- `action.plan_digest` = the `intent.role.binding.diff` digest being reviewed
- `action.artifact_digest` = the resulting `intent.role.binding` digest
- `secure_attention_required = true`

Optional but encouraged:

- `action.policy_digest` when a remembered-role policy snapshot participates
- `action.summary` naming the role and the target move in human terms

That keeps the approval prompt tied to the same reviewable objects the archive already standardized. The approval is still not authority to overwrite newer remembered state: stale reviewed diffs must deny with `reason_code = precondition-failed` and `observed_binding` instead of silently rebasing.

## The receipt profile

The constrained receipt profile stays on top of generic `consent.receipt`.
It keeps the important workstation rule simple:

- `method = auto` is **not** good enough

The receipt may record:

- `approved`
- `denied`
- `timeout`

That means both successful changes and refused interactive attempts can leave typed authority evidence.

## Event-journal join

`intent.role.binding.event` now carries optional:

- `consent_receipt_digest`

For profile **B**:

- `trigger = trusted-settings-ui` + `action = updated` should ordinarily include it
- `trigger = trusted-settings-ui` + `action = write-denied` may include it when denial/timeout happened on the consent lane

This is the key small join:

- snapshot: `intent.role.binding`
- review surface: `intent.role.binding.diff`
- durable event: `intent.role.binding.event`
- approval proof: `consent.receipt`

For the complementary non-interactive lane, see `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`: `policy-reconcile` events should point at `policy.decision` through `policy_decision_digest` instead of borrowing this prompt model. That is enough to keep remembered-role/default changes explainable without dragging the archive into a general settings-transaction platform.

## Product-shape fit without forks

- **A / secure fleet host:** usually has thin or absent interactive role bindings; if a maintenance UI exists, it can choose stricter admin authority instead of inheriting workstation prompts.
- **B / secure workstation:** this is the primary fit; trusted-UI user consent stays the normal authority model for personal remembered-role changes.
- **C / general-purpose OS:** may compile to the same profiles for local UI flows, but can still allow a thinner single-principal lane without pretending ambient desktop settings are the authority.
- **D / appliance factory / regulatory:** production images can omit the interactive lane while maintenance/operator images still reuse the same state/diff/event family.

## What this does **not** decide

This doc does **not** decide:

- a replayable trusted-settings transaction log,
- quorum or shared-trust approval for non-workstation role-binding mutations,
- chooser-history evidence,
- or richer actor/approver graphs beyond generic consent receipts.

Those remain later bounded choices.

## Related docs

- `docs/256-consent-ux-contract.md`
- `docs/288-multiparty-approvals-and-separation-of-duties.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/474-high-risk-approval-posture-by-profile.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`
- `spec/intent.role.binding.consent.request.profile.schema.json`
- `spec/intent.role.binding.consent.receipt.profile.schema.json`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-17r276
