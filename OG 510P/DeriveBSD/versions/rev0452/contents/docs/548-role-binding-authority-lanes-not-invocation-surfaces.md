# Role-binding authority lanes are not invocation surfaces

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain  
**Patterns:** Registry→Diff→Gate, Broker→Lease→Receipt  

`docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md` fixed the interactive authority lane for remembered-role changes.
`docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` fixed `policy_decision_digest` as the non-interactive authority join.
`docs/547-role-binding-support-import-join-via-content-import-receipt.md` fixed import provenance through `import_receipt_digest`.

This doc makes the next small but high-leverage cut:

> `intent.role.binding.event.trigger` names the authority/apply lane that governed the mutation, not the tool or transport that invoked it.

See also:
- ADR: `adrs/ADR-0138-role-binding-authority-lanes-not-invocation-surfaces.md`
- interactive lane: `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- non-interactive policy lane: `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- support/import provenance lane: `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- policy decisions: `docs/93-policy-decision-records.md`

## Why this needs a hard decision

The archive already had the right evidence objects:

- `consent.receipt` for interactive workstation approval
- `policy.decision` for non-interactive reconcile/apply
- `content.import.receipt` for support/import/recovery provenance

But the role-binding event vocabulary still leaked one transport-shaped term:

- `admin-cli`

That is not actually an authority lane.
It only says *how a write was invoked*.
A local admin command can still be policy-governed.
A remote admin wrapper can still be policy-governed.
A daemon can still be policy-governed.
If the archive keeps a transport-shaped trigger, implementations will drift into separate shell, daemon, and remote-admin codepaths even when they all rely on the same `policy.decision` boundary.

That is expensive entropy.
It makes support bundles harder to read, complicates schemas for no product gain, and invites arguments about whether one invocation path is “special.”

## Accepted boundary

The v0 `intent.role.binding.event.trigger` vocabulary is now exactly:

- `trusted-settings-ui`
- `policy-reconcile`
- `support-import`

### What moved where

- authority/apply lane stays in `trigger`
- caller identity stays in `source.name` / `source.service_id`
- interactive approval stays in `consent_receipt_digest`
- non-interactive approval stays in `policy_decision_digest`
- import/recovery provenance stays in `import_receipt_digest`

So a remembered-role mutation can now answer two different questions cleanly:

1. **Who invoked it?** → `source.*`
2. **What lane authorized/applied it?** → `trigger` + joined evidence digests

## Practical implementation target

This gives implementation a much tighter path:

1. read the current `intent.role.binding`
2. construct `intent.role.binding.diff`
3. evaluate the appropriate authority lane
4. compare `diff.from_binding.digest` against current state
5. apply only on match
6. emit `intent.role.binding.event` with the lane-shaped trigger and caller-shaped source metadata

### Example: local admin on profile C

A general-purpose system can still support an explicit local command such as a trusted `derive role-binding set ...` flow.
That command does **not** need a special trigger.
It can compile to:

- `source.name = derive-rolebind-cli`
- `trigger = policy-reconcile`
- joined `policy_decision_digest`

That preserves local-admin viability without inventing a new authority family or requiring a central controller.
The `policy.decision` can be host-local.

## Product-shape fit without forks

- **A / secure fleet host:** reconcile daemons and management wrappers keep one non-interactive authority lane instead of daemon-vs-shell folklore.
- **B / secure workstation:** ordinary user-facing changes still stay on `trusted-settings-ui`; background admin or org policy can use `policy-reconcile` without pretending a prompt happened.
- **C / general-purpose OS:** explicit local admin remains viable, but the command compiles to the same policy lane instead of becoming a new product-shaped trigger.
- **D / appliance factory / regulatory:** factory tooling, staging scripts, and maintenance workflows stay on typed policy/import lanes rather than growing a special manufacturing CLI dialect.

## Why this is worth taking now

This is a small schema change with outsized implementation value:

- one less trigger to explain
- one less drift path for code and docs
- one cleaner query model for support bundles
- and one firmer answer to the “all product shapes without forks” requirement

It is also a better fit for the rest of the archive.
Windows enterprise default associations are administered through policy/configuration files rather than a special “CLI authority” concept, Android managed configurations let IT admins remotely specify app settings, and Kubernetes admission keeps the requesting client distinct from the mutating/validating policy that actually permits or defaults the object. DeriveBSD should keep the same separation between invoker identity and authority lane.  

## What this does **not** decide

This doc does **not** decide:

- exact `policy.decision` language for role-binding reconcile
- transport/auth details for admin tooling
- richer actor/quorum graphs beyond the current joins
- or a general settings/admin transaction platform

Those remain later bounded choices.

## References

- DeriveBSD policy decision records: `docs/93-policy-decision-records.md`
- Android Enterprise managed configurations (IT admins remotely specify app settings): https://developer.android.com/work/managed-configurations
- Android RoleManager API reference: https://developer.android.com/reference/android/app/role/RoleManager
- Microsoft ApplicationDefaults policy CSP (admins set default file type/protocol associations through policy): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-applicationdefaults
- Kubernetes admission controllers (mutating/validating policy is distinct from the requesting client): https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
- Kubernetes Validating Admission Policy (declarative in-process validation rules): https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/

## Related docs

- `docs/93-policy-decision-records.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/229-evidence-spine-overview.md`
- `docs/543-role-binding-event-as-durable-mutation-evidence.md`
- `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`
- `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`
- `docs/547-role-binding-support-import-join-via-content-import-receipt.md`
- `spec/intent.role.binding.event.schema.json`

Last updated: 2026-03-18r278
