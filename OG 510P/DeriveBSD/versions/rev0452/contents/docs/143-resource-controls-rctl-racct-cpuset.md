# Resource controls as a blast-radius boundary (rctl/racct/cpuset)

“Treat builders hostile” includes **resource exhaustion** (CPU/memory/process/thread/IO) as an attack class.
DeriveBSD should derive and enforce resource budgets as part of policy, not as ad-hoc tuning.

Primary references:
- FreeBSD Handbook (resource limits; rctl supports processes and jails): https://docs.freebsd.org/en/books/handbook/security/
- rctl(8): https://man.freebsd.org/rctl
- cpuset(1): https://man.freebsd.org/cpuset

## Lesson to steal

- make resource limits **reviewable and reproducible** (same Plan → same limits)
- apply limits at the boundary we already trust least:
  - builder jails
  - fetcher compartments
  - bhyve microVM runner processes
  - service jails

## DeriveBSD mapping

### Derived object

- `resource.plan.json` (content-addressed):
  - `targets[]`: `{kind: jail|process|service|microvm, id, limits{...}, cpuset{...}}`
  - `rctl_rules[]`: canonical `subject:resource:action=amount` strings
  - `evidence_requirements`: what to snapshot and attach

### Enforcement points

- activation applies:
  - `rctl` rules for each compartment
  - `cpuset` assignments for CPU/mem-domain isolation (where used)

### Evidence

- `resource.applied.json`:
  - effective rctl rules as read-back
  - cpuset membership and affinity for key processes
  - any kernel toggles needed (e.g., racct enabled) as explicit facts

Candidate RFC: *Policy-derived budgets for jails, builders, and microVMs*.

Optional extension:
- treat budgets as delegable capability-like grants (reviewable, leasable): `docs/193-resource-budget-capabilities.md` (RFC-0128)

Last updated: 2026-02-24
