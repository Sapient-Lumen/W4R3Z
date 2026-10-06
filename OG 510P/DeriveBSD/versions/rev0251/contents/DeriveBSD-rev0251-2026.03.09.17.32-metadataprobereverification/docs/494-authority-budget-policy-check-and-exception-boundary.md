# Authority budget / check / exception boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had the right instinct on authority budgets, but one boundary was still too fuzzy:

> is the generic budget lane a small runtime least-authority contract, or a giant umbrella for every privileged operation in the system?

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **authority-budget policy**, **authority-budget evidence**, and **authority-budget waivers** distinct.

The authoritative objects are:

- `authority.budget`
- `authority.exception`

The evidence-only object is:

- `authority.budget.check`

That means:

- `authority.budget` is the reviewed least-authority budget for a component runtime
- `authority.budget.check` records the comparison between compiled runtime posture and that budget
- `authority.exception` is the narrow authoritative waiver when a specific field must temporarily exceed budget

## The generic budget lane is intentionally narrow

In v0, the generic authority-budget lane covers only component-runtime surfaces that compile naturally from descriptor intent and compiled runtime IR:

- filesystem
- network
- devices
- trust
- observability

These map cleanly to artifacts DeriveBSD already wants to compile and receipt, such as `caproute.json`, `preopen.map`, `mount.view`, `devfs.view.plan`, `pki.profile.json`, and `diagnostics.profile.json`.

This is the right scope for a generic least-authority budget because it is:

- reviewable at plan time,
- comparable at drift-check time,
- and portable across A/B/C/D product shapes.

## `authority.budget.check` stays evidence-only

`spec/authority.budget.check.schema.json` carries `authority_semantics = authority-budget-check-evidence-only`.

The check records things like:

- which budget digest was evaluated
- which compiled runtime inputs were used
- which dimension/field broadened or violated policy
- whether the result passed or failed
- which specific fields are candidates for a scoped exception

This gives reviewers and incident tooling the explanation surface they need without letting a check object silently become policy.

## `authority.exception` is field-scoped and timeboxed

`authority.exception` is the authoritative waiver object.
It is deliberately narrow:

- it binds one `authority.budget` digest
- it binds one `authority.budget.check` digest
- it waives one dimension/field at a time
- it expires
- it carries explicit approvals and justification

This keeps “temporary exception” from becoming ambient permanent policy.

## What the generic budget lane does **not** own

The generic authority-budget lane does **not** replace already-accepted higher-authority contracts.

These lanes keep their own authoritative objects and profile-shaped defaults:

- kernel mutation (`docs/475-kernel-mutation-posture-by-profile.md`)
- host network-topology mutation (`docs/477-network-topology-posture-by-profile.md`)
- firmware / UEFI mutation (`docs/471-firmware-update-posture-by-profile.md`)
- destructive reprovision / reset (`docs/483-destructive-reprovisioning-and-reset-authority.md`)
- workload identity issuance (`docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`)
- operator sessions (`docs/467-operator-access-posture-by-profile.md`)

Authority budgets may eventually summarize those lanes in a review UI, but they are not the source of truth for them.

## Why this is the right small hard decision

Making `authority.budget` universal would feel flexible at first, but it would duplicate accepted lane boundaries and make implementation harder.

Keeping it narrow gives DeriveBSD something much more valuable:

- one compilable least-authority object for common runtime surfaces,
- one evidence object for review/explanation,
- and one precise waiver object when reality must temporarily differ.

That is enough to start implementing without pretending every hard authority question is already solved.

## Product-shape fit (A–D without forks)

- **A / fleet host:** budgets stay strict and reviewable for service/runtime authority, while higher-risk host mutation still goes through existing maintenance-leased lanes.
- **B / workstation:** apps and AppVMs can use the same generic budget lane, but trusted-UI-visible consent and session posture remain separate where they should.
- **C / general-purpose OS:** the budget lane stays useful even when broader compatibility adapters exist, because the budget is about compiled runtime posture rather than purity fantasies.
- **D / appliance factory / regulatory:** narrow budgets and narrow exceptions fit audit-heavy environments better than giant catch-all permission objects.

## Related docs

- `adrs/ADR-0084-authority-budgets-and-exception-boundary.md`
- `docs/298-authority-budgets-and-permission-drift-alarms.md`
- `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- `docs/229-evidence-spine-overview.md`
- `docs/374-authority-diff-schema-and-review-workflows.md`
- `spec/authority.budget.schema.json`
- `spec/authority.budget.check.schema.json`
- `spec/authority.exception.schema.json`

Last updated: 2026-03-07r223
