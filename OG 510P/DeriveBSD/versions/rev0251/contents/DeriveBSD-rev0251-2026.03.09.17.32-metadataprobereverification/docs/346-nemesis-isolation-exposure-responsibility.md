# Nemesis lesson: isolation + exposure + responsibility (resource use as policy input)

Many systems can *limit* resource use.
Far fewer systems make resource use:
- **isolated** (one component can’t silently steal from another)
- **exposed** (usage is visible and attributable)
- **responsible** (someone is charged; budgets are enforceable)

Nemesis is a research OS built around this discipline for QoS.
The details aren’t what we want to copy; the *triad* is.

## The triad

### 1) Isolation

A component should not be able to degrade unrelated components through shared-kernel contention.
Isolation can be implemented via:
- hard caps
- reservations
- dedicated workers / compartments

DeriveBSD already has strong primitives here (jails, microVMs, rctl/racct, cpusets).

### 2) Exposure

If a component is using a resource, we should be able to answer:
- how much?
- over what window?
- correlated with what events?

This turns “mysterious slowdown” into queryable evidence.

### 3) Responsibility

A component’s resource consumption must be chargeable to a declared intent:
- a budget capability
- a lease
- a policy decision record

If a resource use cannot be attributed, it’s a design smell.

## DeriveBSD translation

### Budgets as capabilities

Prefer making “permission to spend” an explicit object:
- `resource.budget.grant`
- per-unit budget plans
- receipts tying observed usage to the budget

See: `docs/193-resource-budget-capabilities.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`.

### Contention is part of the threat model

When we isolate privileged subsystems (fetch, update, attestation, crypto), we should also isolate *their resource failure modes*:
- runaway CPU/memory
- stuck IO
- pathological retry loops

Then record violations as evidence, not folklore.

See: `docs/214-service-supervision-health-as-evidence.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`.

### Consider “energy” and “bandwidth” as first-class budgets

Nemesis explicitly treated non-traditional resources as schedulable/accountable.
DeriveBSD’s evidence spine makes this tractable:
- energy and network can be measured and receipted
- policy can constrain “who may spend”

This is especially relevant for laptop/edge deployments.

## References

- Nemesis project archive (overview): https://www.cl.cam.ac.uk/research/srg/netos/projects/archive/nemesis/
- “Self-Paging in the Nemesis Operating System” (Hand et al., OSDI 1999): https://www.usenix.org/events/osdi99/full_papers/hand/hand.pdf

Last updated: 2026-02-27
