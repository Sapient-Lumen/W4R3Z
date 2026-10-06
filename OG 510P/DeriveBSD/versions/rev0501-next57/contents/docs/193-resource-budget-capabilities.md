# Resource budget capabilities (delegable, reviewable, enforceable)

DeriveBSD already maps resource ceilings to OS primitives (rctl/racct, cpuset, ZFS quotas).
What most OSes miss is **delegation**:

- who is allowed to *spend* resource budgets
- how budgets can be subdivided safely
- how to make “budget changes” reviewable like other authority changes

This doc proposes an optional lane: **resource budgets as capabilities**.

## Why this is greenfield-worthy

As systems scale, “set some limits” turns into:

- per-service SLO budgets
- dynamic job schedulers
- plugins/workers spawned by a parent that must not exceed a shared envelope

If budgets are not delegable objects, the ecosystem falls back to ambient authority (“just run it and hope limits exist”).

Linux cgroup v2 explicitly documents a model of *delegation* as a first-class concept.
DeriveBSD can steal that mindset while mapping enforcement to FreeBSD primitives.

References:
- cgroup v2 delegation model: https://docs.kernel.org/admin-guide/cgroup-v2.html
- FreeBSD rctl(8): https://man.freebsd.org/rctl

## Model

### Budget grants

`resource.budget.grant` is a signed, digestable authorization:

- **subject**: process/jail/service/microVM runner
- **resources**: cpu-time, memory, processes, IO, dataset bytes, network egress (as supported)
- **bounds**: limit + optional period/burst
- **lease**: time-bounded by default; revocable when mediated
- **context**: plan/policy decision digests

Schema:
- `spec/resource.budget.grant.schema.json`

### Delegation / subdivision

Budgets may be subdivided:

- parent receives a budget grant
- parent requests sub-budgets for children
- policy may allow automatic subdivision within a max envelope

Operationally, this is the resource analogue of portals + leases:
explicit grants, explicit revocation, explicit receipts.

### Enforcement mapping

- CPU/memory/process ceilings: rctl/racct + cpuset
- dataset quotas/reservations: ZFS dataset properties
- network caps (optional): pf + dummynet shaping, or per-interface limits when available

The key is that **policy derives budgets**, and activation enforces them.

### Usage evidence (optional)

For explainability and SLO debugging, a small `resource.budget.usage` receipt can summarize:

- grant digest
- window
- observed usage + whether any limit was hit

Schema:
- `spec/resource.budget.usage.schema.json`

## Integration points

- Capability graph linting: budgets are “authority edges” (ability to consume resources)
- Rollouts: staged deployments can gate on “budget conformance”
- Scenario tests: assert budgets are actually enforced under load

See:
- `docs/143-resource-controls-rctl-racct-cpuset.md`
- `docs/189-capability-graph-lint-and-viz.md`
- `docs/188-scenario-tests-multimachine.md`

Last updated: 2026-02-24
