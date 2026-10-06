# Diagnostics query plane (Archivist-style): selectors, snapshots, and least-authority access

`docs/302-structured-diagnostics-inspect-trees.md` covers the core idea: **Inspect-style trees** as structured state, and an **archivist** service that ingests and serves diagnostics.

This doc tightens the *ecosystem* side of that idea: the query API, the snapshot artifact shape, and the permission/contract integration that keeps diagnostics from turning into ambient surveillance.

Prior art worth stealing:
- Fuchsia diagnostics overview (logs + Inspect + Archivist): https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics
- Fuchsia Inspect overview: https://fuchsia.dev/fuchsia-src/development/diagnostics/inspect
- Fuchsia diagnostics protocols (`fuchsia.diagnostics`): https://fuchsia.dev/reference/fidl/fuchsia.diagnostics
- Inspect tree hosting/discovery notes: https://fuchsia.dev/fuchsia-src/reference/diagnostics/inspect/tree
- RFC-0168 (Inspect exposure via InspectSink): https://fuchsia.dev/fuchsia-src/contribute/governance/rfcs/0168_exposing_inspect_through_inspectsink

## DeriveBSD direction

### 1) A single, capability-gated query surface
Introduce a brokered query contract (conceptually like Fuchsia’s ArchiveAccessor):

- `diag.query` — select and fetch diagnostics data
  - supports *selectors* (component id + subtree path)
  - supports time windows (for logs/traces) and point-in-time reads (for inspect trees)
  - supports streaming for large datasets (with budgets)

Key property: access is mediated through capabilities and leases.

See:
- observability as capability: `docs/192-observability-as-capability.md`
- permission center: `docs/371-permission-center-and-authority-introspection.md`

### 2) Snapshots are first-class artifacts
Add a “diagnostics snapshot” concept as a normal derived output (not a bespoke tarball):

- a snapshot is a *plan* (what to include + redaction rules) and a *receipt* (what was captured)
- snapshots are content-addressed and can be referenced from incident bundles

This aligns with:
- incident snapshots + support bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

### 3) Diagnostics schema drift is reviewable
If tooling depends on diagnostic paths, changes must be reviewable like other surfaces:
- new stable Inspect subtrees can appear in `contract.diff` (or a dedicated diagnostics-contract registry)
- “new diagnostic sink exposure” should appear as an authority edge in `authority.diff`

See:
- contract diffs: `docs/370-contract-registries-and-api-diff-gates.md`
- authority diffs: `docs/374-authority-diff-schema-and-review-workflows.md`

## Permissions and privacy budgets

Diagnostics are inherently sensitive.
Bake in the following invariants:

- **Access requires a lease** by default (timeboxed; receipted).
- **Selectors are the unit of review** (don’t grant “all diagnostics”, grant “this component subtree”).
- **Export is always mediated** (ticketing uploads, support bundles) and emits receipts.
- **Budgets exist** (rate/size limits) to prevent diagnostics from becoming a covert channel.

## Why this is a groundfloor feature

If the platform doesn’t ship a uniform diagnostics plane, ecosystems reinvent it:
- ad-hoc scrape endpoints
- “run this script with sudo”
- permanent debug backdoors

An Archivist-style query plane turns diagnostics into:
- a consistent developer experience
- a consistent operator experience
- a consistent policy + evidence surface
