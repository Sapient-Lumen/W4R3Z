# Public Dependency Boundary Kit fixtures

This fixture pack models the review artifacts for **P-0431 Public Dependency Boundary Kit**.

## Core artifact families

- `manifest-intent.receipt` — what Cargo declarations said, including unsupported inheritance facts.
- `boundary-verdict.report` — what dependencies are effectively public today.
- `exposure-route.report` — how each dependency crossed the public boundary.
- `evidence-provenance.receipt` — which findings came from Cargo/rustc versus rustdoc-based tooling.
- `workspace-gap.receipt` — where current workspace/scope limitations block a cleaner declaration.
- `boundary-migration.plan` — safest next moves.
- `public-dependency-drift.diff` — how the boundary changed over time.
- `public-dependency-support-bundle.manifest` — compact handoff bundle.

## Scenario families

1. accidental exposure through a reexport or visible signature,
2. workspace inheritance gaps that prevent `public` from being declared where intent lives,
3. hidden shim / allowlisted cases that still need explicit provenance,
4. wrapper migrations that remove effective publicness without pretending the old publicness never existed,
5. drift between declared and effective boundary across releases.
