# ADR-0133: Role-binding event as durable mutation evidence

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed the authoritative remembered role/default state as `intent.role.binding`.
`adrs/ADR-0132-role-binding-diff-as-review-surface.md` then fixed `intent.role.binding.diff` as the compact review surface when that state changes.

That leaves one narrow but important implementation gap:

- where does the durable event-journal trail for remembered role/default changes live?
- what should an incident/support bundle point at when it needs to answer **when** remembered browser/mail ownership changed?
- how do we avoid smuggling this back into grep-only shell history, desktop-settings logs, or a giant future settings-operation platform?

The archive already has a strong pattern in other lanes:

- authoritative snapshot/object
- compact diff for review
- event trail for durable time-ordered mutation evidence

That same shape fits remembered role/default state.
It also matches the primary external pressure: Android’s role system uses explicit host-managed roles with explicit user-grant flows instead of ambient registry edits, while XDG AppChooser chooses from a provided list and XDG Settings is explicitly read-only and not for general-purpose settings.
That combination argues for keeping remembered role/default state narrow, host-owned, and durable in the evidence journal without inventing a universal settings subsystem.

## Decision

DeriveBSD now standardizes a durable event artifact for remembered role/default changes:

- `intent.role.binding.event`

The boundary is:

1. `intent.role.binding` remains the authoritative remembered state snapshot.
2. `intent.role.binding.diff` remains the compact review/gating surface.
3. `intent.role.binding.event` is the durable event-journal evidence object for remembered role/default mutation outcomes.
4. v0 actions are intentionally narrow:
   - `initialized`
   - `updated`
   - `write-denied`
5. Successful mutation events should point at the resulting binding snapshot and, when there was a prior snapshot, the compact diff that summarizes the posture change.
6. `intent.role.binding.event` is for durable mutation evidence and event-journal/support-bundle joins; it is **not** the full trusted-settings receipt family.
7. Actor identity, approver identity, and replayable settings transactions remain future work. v0 may record only bounded trigger class/source metadata.

## Consequences

- The archive now has a stable answer to “when did remembered browser/mail ownership change?”
- Structured event logs and incident bundles can include remembered-role/default changes without scraping settings logs or desktop registries.
- Trusted settings/admin implementation can start from a small trio:
  - snapshot: `intent.role.binding`
  - review surface: `intent.role.binding.diff`
  - durable mutation trail: `intent.role.binding.event`
- A/C/D remain coherent because they can emit the same event family when role bindings exist, while still compiling to thinner or absent role populations.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- full actor/approver attribution for every role-binding change,
- a replayable settings transaction / receipt family,
- chooser-history or “last used” evidence,
- or whether broader role vocabularies should enter the baseline.

Those remain later bounded decisions.

## Related

- `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `adrs/ADR-0132-role-binding-diff-as-review-surface.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/215-structured-event-log-as-evidence.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `spec/intent.role.binding.schema.json`
- `spec/intent.role.binding.diff.schema.json`
- `spec/intent.role.binding.event.schema.json`
