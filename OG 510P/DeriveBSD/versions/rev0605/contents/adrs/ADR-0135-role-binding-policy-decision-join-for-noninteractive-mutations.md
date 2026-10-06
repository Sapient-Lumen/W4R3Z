# ADR-0135: Role-binding policy-decision join for non-interactive mutations

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md` fixed remembered browser/mail ownership as typed `intent.role.binding` state.
`adrs/ADR-0132-role-binding-diff-as-review-surface.md` fixed `intent.role.binding.diff` as the compact review surface.
`adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md` fixed `intent.role.binding.event` as the durable mutation trail.
`adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive workstation approval lane by reusing constrained `consent.request` / `consent.receipt` profiles.

That leaves one narrow but important cross-profile gap:

- what proves why a non-interactive `policy-reconcile` change rewrote remembered browser/mail ownership?
- how do A / C / D avoid inheriting workstation prompts for fleet, maintenance, dedicated-device, or regulated images?
- how do we answer that without inventing a new role-binding approval subsystem?

The archive already has a generic artifact for machine-enforced authority:

- `policy.decision`

DeriveBSD already uses `policy_decision_digest` as the standard evidence join across grants, receipts, launch plans, and event artifacts.
That means the smallest coherent move is to bind non-interactive role-binding mutations back to the existing policy-decision lane instead of letting reconcile daemons or admin wrappers become the real source of truth.

Android Enterprise reinforces the distinction: ordinary role ownership is an explicit role flow, while managed devices and managed configurations give IT/admin authority explicit policy control over app settings for work profiles and dedicated devices.

## Decision

For non-interactive role/default mutations, DeriveBSD now standardizes a policy-decision join on the existing event artifact instead of adding a new approval family.

The boundary is:

1. `intent.role.binding.event` is extended with optional `policy_decision_digest`.
2. For `trigger = policy-reconcile`, `policy_decision_digest` is required.
3. The required digest points at the existing `policy.decision` record that authorized the resulting remembered role/default state.
4. `admin-cli` may also attach `policy_decision_digest` when the mutation ran under an explicit policy apply/reconcile plan, but v0 does not require it for every local-admin path.
5. The interactive workstation lane remains what ADR-0134 decided: `consent.request` / `consent.receipt` profiles plus `consent_receipt_digest`.
6. The durable event is now the narrow authority join surface:
   - interactive workstation mutation → `consent_receipt_digest`
   - non-interactive policy mutation → `policy_decision_digest`
7. This is still not a universal actor/approval graph. If later work needs richer multi-party or replayable settings-operation receipts, it should arrive as a separate bounded family.

## Consequences

- A / C / D now have a clean non-interactive authority story for remembered role/default changes without pretending every image has a workstation prompt.
- Fleet, maintenance, reconcile, and dedicated-device role-binding changes can point to the same authority artifact DeriveBSD already uses elsewhere.
- Support bundles and event-journal queries can answer not only *what changed* and *when*, but also *which policy decision authorized the non-interactive change*.
- The archive stays small: it reuses `policy.decision` instead of inventing `intent.role.binding.policy.receipt` or a workstation-shaped admin lane.

## What this ADR does **not** decide

This ADR does **not** yet decide:

- a replayable trusted-settings/admin transaction log,
- exact policy language for role-binding reconcile,
- whether every `admin-cli` role-binding change must always compile through an explicit policy plan,
- or richer actor/quorum receipts for organization-shared mutations.

Those remain later bounded decisions.

## Related

- `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`
- `adrs/ADR-0132-role-binding-diff-as-review-surface.md`
- `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`
- `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/93-policy-decision-records.md`
- `docs/474-high-risk-approval-posture-by-profile.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `spec/intent.role.binding.event.schema.json`
