# RFC-0179: Resource budgets as evidence

Status: Draft

## Problem

Resource limits today are usually configured through:

- ad-hoc rc scripts
- per-user `ulimit`
- opaque supervisor flags

This breaks DeriveBSD’s goal that operational behavior is explainable and replayable.
We want resource governance to be **reviewable**, **composable**, and **auditable**.

## Goals

- Define a typed budget/profile format that can compile to multiple backends.
- Make budget application produce receipts.
- Make budget violations produce structured events.
- Integrate budgets into `svcdb` so authority changes appear in diffs.

Non-goals:

- Replacing all backend mechanisms. We *compile to* them.

## Proposal

1) Introduce `resource.profile` (artifact) with `budgets[]`.
2) Extend `svcdb.services[].resources` with optional `budgets[]`.
3) Add apply-engine op `apply-resource-budgets`.
4) Emit `resource.budget.receipt` on apply.
5) Emit `resource.violation.event` on exceedance.

## Backends

- FreeBSD: `rctl(8)` + `racct(8)` + `cpuset(1)`.
- Jails/microVMs: enforce via jail parameters and hypervisor config.

## Evidence + causality

- Receipt digests and violation event ids are candidates for `causality.graph` nodes.
- Incident bundles gain explicit `resource_budget_*` include lists.

## Rollback

Budgets are part of generation switching:

- “active generation” defines the service graph and budgets.
- switching generations applies budgets as part of activation.

## Open questions

- Standard resource enum and unit normalization.
- How to express multi-dimensional budgets (e.g., CPU+IO) portably.

References:
- `docs/247-resource-budgets-and-limits-as-evidence.md`
