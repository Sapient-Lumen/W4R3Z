# ADR-0138: Role-binding authority lanes are not invocation surfaces

Date: 2026-03-18
Status: Accepted

## Context

`adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive workstation authority lane by joining remembered-role changes to constrained `consent.request` / `consent.receipt` profiles.
`adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed `policy_decision_digest` as the non-interactive authority join.
`adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md` fixed compare-and-swap apply semantics.
`adrs/ADR-0137-role-binding-support-import-join-via-content-import-receipt.md` fixed import provenance for support/import paths.

That work left one expensive ambiguity in the event vocabulary:

- `intent.role.binding.event.trigger` still allowed `admin-cli`
- but `admin-cli` is not an authority lane; it is only one way to invoke a write
- the actual authority still comes from either interactive consent, non-interactive policy, or typed import/recovery evidence

Keeping `admin-cli` in the trigger vocabulary mixes *who invoked the write* with *what authorized the write*.
That would push implementations toward extra ad-hoc paths:

- daemon writes with one trigger
- shell writes with another
- remote-admin wrappers with a third
- and endless debates over whether a local command "counts" as policy or not

The archive already has the right split elsewhere: authority is a typed artifact (`consent.receipt`, `policy.decision`, `content.import.receipt`), while the caller identity belongs in bounded source metadata.
The role-binding event family should follow the same rule.

## Decision

1. `intent.role.binding.event.trigger` names the authority/apply lane, not the transport or invocation surface.
2. `admin-cli` is removed from the trigger vocabulary.
3. The v0 trigger vocabulary is now:
   - `trusted-settings-ui`
   - `policy-reconcile`
   - `support-import`
4. Any non-import remembered-role mutation that is not on the interactive consent lane must compile to `trigger = policy-reconcile` and carry `policy_decision_digest`.
5. Local admin commands, remote orchestration, MDM-style management agents, and reconcile daemons identify themselves in `source.name` / `source.service_id`; they do not get separate authority triggers.
6. `support-import` remains distinct because it carries import provenance through `import_receipt_digest`; it may still also carry `policy_decision_digest` when replay/import policy governed the mutation.
7. This ADR does **not** invent a separate admin receipt family and does **not** require a central controller. A host-local command on profile C may still produce a host-local `policy.decision`.

## Consequences

- The event family becomes smaller and more implementable: there is one interactive lane, one non-interactive policy lane, and one import/recovery lane.
- Profile **C** keeps local-admin viability without forking the evidence model; a CLI can still be explicit while compiling to the same `policy.decision` lane as other non-interactive writers.
- A / B / C / D stay coherent because the authority vocabulary now matches the already-accepted evidence joins.
- Support bundles can answer both *which tool invoked the write* (`source.*`) and *which lane authorized it* (`trigger` + joined digests) without inventing extra folklore.
- Future implementation work gets a crisp target: build diff → evaluate policy/consent/import → compare-and-swap apply → emit event with lane-shaped trigger and caller-shaped source metadata.

## Follow-up intentionally left open

This ADR still does **not** decide:

- exact role-binding reconcile policy language
- richer actor/quorum attribution beyond `source.*` plus existing joined evidence
- remote transport/auth details for admin tools
- or a full replayable settings/admin transaction family

Those remain later bounded choices.

## Related

- `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md`
- `adrs/ADR-0137-role-binding-support-import-join-via-content-import-receipt.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`
- `spec/intent.role.binding.event.schema.json`
