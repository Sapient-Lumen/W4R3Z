# Invariant registry and design invariants (Registry → Diff → Gate)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Registry→Diff→Gate  

DeriveBSD is only coherent if a small set of statements stays true **forever**, even as features and profiles evolve.
Those statements are *invariants*: they define what “DeriveBSD-ness” means and prevent slow drift into an ad-hoc distro.

This doc introduces a single stable diff surface for invariants:

- `invariant.registry` — a typed registry of invariants (`spec/invariant.registry.schema.json`).

This is intentionally **small and boring**: a registry you can diff in code review, gate in CI, and cite from other docs.

## Why a registry (not prose)

Prose rots. A registry is:

- **diffable:** changes are obvious and reviewable
- **gateable:** CI can prevent accidental weakening
- **citable:** other docs can reference invariant ids instead of rephrasing them

Pattern mapping (`docs/397-pattern-catalog.md`):
- **Registry → Diff → Gate:** invariants live in a registry, are reviewed as diffs, and can be gated by policy/CI.

## What belongs here

Invariants are high-level “must never break” statements. They should:

- be **testable** (or at least checkable) eventually
- cite the **evidence surface** that proves compliance (receipt/event/report)
- name the **scope** (build, activation, runtime, promotion)

Examples:
- “No implicit inputs reach a build without a policy-controlled impurity receipt.”
- “Every activation switch emits a typed receipt bound to the generation digest.”
- “Interop adapters must be killable by policy.”

## How to use invariants

### 1) Reference invariant ids in design docs
Instead of restating the same rule in 10 places, cite the invariant id:

- `inv.repro.explicit-inputs`
- `inv.isolation.leased-authority`
- `inv.supply.promote-gated`
- `inv.ops.receipts-everywhere`

### 2) Treat invariant changes as high-cost
Changing invariants is allowed, but should feel like changing a constitution:

- **RFC first**, then an ADR on acceptance.
- Require a clear *entropy budget* justification: what gets simpler / more coherent?
- Update any downstream evidence surfaces and tooling checks.

### 3) Wire invariants into review rubrics
The design review rubric should eventually include:

- “Which invariants does this proposal rely on?”
- “Does it weaken any invariant?”

(Keep this doc small; add rubric wiring only when it becomes concrete.)

## Related prior art (formal-ish thinking without requiring formal methods)

The intent is “invariants-first thinking”, not mandatory theorem proving.
If/when the project benefits from deeper modeling, these are good entry points:

- TLA+ (temporal logic specs): https://lamport.azurewebsites.net/tla/tla.html
- TLA+ toolbox / reference impl: https://github.com/tlaplus/tlaplus
- Alloy (lightweight relational modeling): https://alloytools.org/

## Files

- Registry schema: `spec/invariant.registry.schema.json`
- Registry example: `spec/examples/invariant.registry.json`

