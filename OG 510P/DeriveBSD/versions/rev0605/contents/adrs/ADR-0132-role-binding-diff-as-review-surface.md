# ADR-0132: Role-binding diff as a review surface

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` already decided that remembered `browsing` / `communications` defaults live in a typed `intent.role.binding` object rather than in desktop-registry folklore.
That gave the archive a stable *state object*, but it still left one practical implementation cliff:

- how should trusted settings/admin UX present a change to that object for review?
- what compact artifact should `drift.bundle` attach when role ownership or chooser enrollment changes?
- how do strict profiles avoid turning workstation role/default changes into opaque settings writes that only a local shell or a GUI database can explain?

If we leave that unanswered until much later, the likely first implementation will be a bag of stateful writes with no stable drift surface.
That would recreate the old “default app changed somehow” problem in a typed archive that still cannot summarize *what* changed.

Current practice pushes toward a narrow answer rather than a giant settings subsystem.
Android’s role system keeps some handler classes explicit and host-managed, XDG’s AppChooser chooses from a provided list rather than an unrestricted registry, and XDG’s Settings backend is explicitly read-only and “not for general purpose settings.”
That is the right shape for DeriveBSD too: keep runtime routing state typed, and make *changes* to that state visible through a compact review artifact before inventing a general mutation platform.

## Decision

For remembered role/default state, the archive now standardizes a compact review surface:

- `intent.role.binding.diff`

The boundary is:

1. `intent.role.binding` remains the authoritative remembered state object.
2. When trusted settings/admin workflows change that object, the canonical compact review artifact is `intent.role.binding.diff`.
3. `intent.role.binding.diff` compares old/new binding snapshots by digest and summarizes only the high-signal posture changes:
   - default target changes per role
   - enrolled targets added
   - enrolled targets removed
   - stable `risk_flags` suitable for review UI and policy gates such as `role-binding-default-changed`, `role-binding-target-enrolled`, and `role-binding-target-removed`
4. The diff surface is intentionally **not** a full mutation receipt family.
   Actor identity, approval chains, and durable settings-operation receipts may still arrive later, but the review/gating surface is standardized now.
5. For profile **B**, role-binding changes should be reviewable through trusted settings/admin UX using `intent.role.binding.diff` rather than raw settings blobs or desktop-registry deltas.
6. For stricter profiles, policy may require attaching `intent.role.binding.diff` to promotion/review bundles whenever role-binding state exists and changes.

## Consequences

- The archive now has a stable answer to “what changed in remembered browser/mail role ownership?”
- `drift.bundle` can attach a small artifact instead of forcing humans to diff raw binding snapshots by eye.
- Settings/admin implementation work can start from snapshot + diff without having to settle the whole future mutation-receipt family.
- A/C/D remain coherent because they can compile to the same snapshot/diff pair while keeping the actual role population smaller, absent, or more compatibility-shaped.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- the full trusted-settings mutation receipt family,
- actor/approver attribution for every role-binding change,
- whether chooser history or “last used” state deserves a separate evidence object,
- or whether more roles beyond `browsing` / `communications` should enter the baseline vocabulary.

Those remain later bounded decisions.

## Related

- `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `docs/542-role-binding-diff-as-review-surface.md`
- `docs/430-diff-surface-registry.md`
- `docs/395-drift-bundles-and-review-summaries.md`
- `spec/intent.role.binding.schema.json`
- `spec/intent.role.binding.diff.schema.json`
