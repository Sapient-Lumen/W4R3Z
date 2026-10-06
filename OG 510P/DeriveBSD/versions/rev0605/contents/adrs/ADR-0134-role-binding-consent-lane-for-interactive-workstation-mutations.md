# ADR-0134: Role-binding consent lane for interactive workstation mutations

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`adrs/ADR-0132-role-binding-diff-as-review-surface.md` fixed `intent.role.binding.diff` as the compact review surface.
`adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable mutation trail.

That leaves one narrow but important implementation cliff:

- what proves that an interactive workstation user actually approved a remembered browser/mail default change?
- how do we keep trusted settings UI from turning into an unreceipted ambient settings writer?
- how do we add that proof without inventing a brand-new settings-approval subsystem?

The archive already has a generic answer for human-mediated high-leverage actions:

- `consent.request`
- `consent.receipt`

Profile **B** already says trusted-UI user consent is the normal authority model for personal-risk actions, while shared-trust/org-wide mutations move into an explicit admin lane rather than hijacking ordinary prompts.
That means remembered browser/mail default changes should reuse the generic consent lane, but through a constrained profile that binds the same high-signal objects people already review:

- the posture diff (`intent.role.binding.diff`)
- the resulting remembered state (`intent.role.binding`)
- the trusted UI approval outcome (`consent.receipt`)

Android role requests also reinforce the shape: role changes are explicit request flows rather than ambient registry writes, while XDG AppChooser chooses from a provided list and XDG Settings is explicitly read-only and not for general-purpose settings.

## Decision

For interactive workstation role/default mutations, DeriveBSD now standardizes a constrained consent lane:

- `intent.role.binding.consent.request.profile`
- `intent.role.binding.consent.receipt.profile`

The boundary is:

1. Profile **B** trusted-settings UI changes to remembered `browsing` / `communications` ownership should reuse the generic `consent.request` / `consent.receipt` substrate rather than inventing a new settings-approval artifact family.
2. The constrained request profile must bind the posture change and resulting state through:
   - `action.kind = change.confirm`
   - `action.plan_digest` = the `intent.role.binding.diff` digest being reviewed
   - `action.artifact_digest` = the resulting `intent.role.binding` digest
   - `secure_attention_required = true`
3. The constrained receipt profile may record `approved`, `denied`, or `timeout`, but it must not use `method = auto`.
4. `intent.role.binding.event` is extended with optional `consent_receipt_digest` so the durable mutation trail can join back to the generic consent lane when that lane was used.
5. For `trigger = trusted-settings-ui` on profile **B**, successful `updated` events should carry `consent_receipt_digest`; denied interactive attempts may also carry it on `write-denied` events.
6. This is the workstation interactive lane, not a universal approval mandate. Admin CLI, policy reconcile, fleet, and factory/regulatory shapes may use stricter or different authority lanes.

## Consequences

- The archive now has a stable answer to “which approval authorized this remembered browser/mail default change?”
- Trusted settings UI can stay small: review the typed diff, request consent on the existing substrate, emit the typed event, and point to the joined consent receipt.
- Support bundles and event-journal queries can answer not only *what changed* and *when*, but also whether the interactive consent lane approved or denied it.
- A/C/D remain coherent because they are not forced into the workstation prompt model; they can omit or replace this lane while still reusing the same state/diff/event family.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- a replayable trusted-settings transaction log,
- richer actor/approver graphs beyond the generic consent substrate,
- exact trusted-UI wording or display layout,
- or whether non-interactive admin/fleet/factory role-binding changes need a stricter dedicated approval profile.

Those remain later bounded decisions.

## Related

- `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `adrs/ADR-0132-role-binding-diff-as-review-surface.md`
- `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`
- `docs/256-consent-ux-contract.md`
- `docs/474-high-risk-approval-posture-by-profile.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `spec/intent.role.binding.consent.request.profile.schema.json`
- `spec/intent.role.binding.consent.receipt.profile.schema.json`
- `spec/intent.role.binding.event.schema.json`
