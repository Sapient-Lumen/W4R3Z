# Genode init and capability-routing lessons (nested policy, explicit resources)

Genode is a capability-based component framework that has accumulated years of pragmatic routing/policy experience.
Two things are especially relevant to DeriveBSD’s “unit manifests + cap routing” direction:

1) **Init is policy-driven**: a data file declares children, relationships, and resource assignments.
2) **Nested init**: the system can be a tree of “subsystems”, each with scoped authority.

References:
- Genode “init component” documentation: https://genode.org/documentation/genode-foundations/21.05/system_configuration/The_init_component.html
- Genode capability-based security overview: https://genode.org/documentation/genode-foundations/20.05/architecture/Capability-based_security.html

## What to steal

### 1) A single place to read “how the system runs”
Genode’s init config serves as an operator’s map of:
- what runs
- who depends on what
- who gets what resources

DeriveBSD should keep pushing toward the same property via:
- `derive.unit` as the declaration surface
- compiled runtime manifests as the truth

See:
- unit manifests + routing: `docs/344-derive-unit-manifests-and-capability-routing.md`
- component descriptors → runtime manifests: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`

### 2) Hierarchical subsystems with scoped authority
Nested init is a practical way to avoid a flat, global capability soup.
DeriveBSD can express this with:
- hierarchical unit groups (sub-plans)
- microVM/jail boundaries as first-class nodes
- authority graphs that preserve parent/child scope

See:
- authority graphs: `docs/366-capability-graphs-and-authority-diff-surfaces.md`
- microVM targets: `docs/24-microvm-artifact-target.md`

### 3) Resource assignment is part of policy
Genode treats resource assignment as part of the config, not an afterthought.
This aligns with DeriveBSD’s “budgets are authority” idea:
- CPU/mem/IO budgets are explicit and reviewable
- changes show up as diffs and produce receipts

See:
- resource governance as evidence: `docs/222-resource-governance-as-evidence.md`
- budget capabilities: `docs/193-resource-budget-capabilities.md`

## What not to copy

- The exact XML format is not the point.
- The point is the *shape*: policy-as-data, routing-as-declaration, nested scope, and explicit resources.
