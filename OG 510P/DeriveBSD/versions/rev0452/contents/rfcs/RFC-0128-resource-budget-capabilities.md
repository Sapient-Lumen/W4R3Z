# RFC-0128: Resource budget capabilities (delegable envelopes + usage receipts)

Status: **draft**

## Motivation

DeriveBSD already uses OS primitives (rctl/racct, cpuset, ZFS) to enforce limits.
But ecosystems often lack a clean way to express:

- who is allowed to *spend* budgets
- how a parent can subdivide a budget among children
- how budget changes become reviewable and auditable

Treating budgets as capability-like grants makes “resource authority” explicit.

## Goals

- Define a standard signed budget grant object.
- Support delegation/subdivision while maintaining a bounded envelope.
- Keep enforcement mapped to FreeBSD primitives.
- Optionally emit small usage receipts for explainability.

## Non-goals

- Replacing a full scheduler / cluster resource manager.
- Perfectly representing every resource type on day 1.
- Moving enforcement out of the kernel/host primitives.

## Proposal

### 1) Evidence object: `resource.budget.grant`

Schema: `spec/resource.budget.grant.schema.json`

Fields (v0.1):

- `kind`, `grant_version`
- `lease_id` (optional)
- `subject`:
  - `{target_kind: process|jail|service|microvm, id: ...}`
- `budgets[]`:
  - `{resource, limit, period_seconds?, burst?}`
- `context`:
  - `plan_digest`, `policy_snapshot_digest`, `policy_decision_digest`
- `issued_at`, `expires_at`
- `signature`

### 2) Delegation / subdivision

Policy MAY allow:

- parent to request sub-grants where sum(child) <= parent envelope
- automatic subdivision templates per workload class

Sub-grants SHOULD bind to the parent grant digest in `context.parent_grant_digest`.

### 3) Enforcement mapping

- rctl/racct for CPU, memory, processes, IO counters
- cpuset for core pinning / isolation
- ZFS dataset quotas/reservations where budgets include storage
- optional network shaping via pf+dummynet when needed

### 4) Evidence object: `resource.budget.usage` (optional)

Schema: `spec/resource.budget.usage.schema.json`

Summarizes observed usage for a window:

- binds to grant digest
- includes usage counters
- records whether a limit was hit

### 5) Policy integration

Add optional policy knobs:

- `resource.requiredBudgets` per target kind
- `resource.maxEnvelope` per class
- `resource.allowDelegation` rules

## References

- FreeBSD rctl(8): https://man.freebsd.org/rctl
- Linux cgroup v2 delegation model (mindset reference): https://docs.kernel.org/admin-guide/cgroup-v2.html
