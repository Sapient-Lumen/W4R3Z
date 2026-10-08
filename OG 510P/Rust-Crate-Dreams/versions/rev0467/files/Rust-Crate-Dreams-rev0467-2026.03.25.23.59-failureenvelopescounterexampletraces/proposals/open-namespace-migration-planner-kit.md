---
id: P-0443
title: Open Namespace Migration Planner Kit — RFC-3243 adoption plans, alias receipts, and import-migration bundles for namespaced crates
status: idea
domains: [cargo, crates-io, packaging, migration, naming, registry, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
  - https://github.com/rust-lang/cargo/issues/13576
  - https://github.com/rust-lang/crates.io/issues/8292
  - https://blog.rust-lang.org/inside-rust/2024/03/26/this-development-cycle-in-cargo-1.78/
---

# Problem

Optional package namespaces are now real Rust project policy and active implementation work. Cargo support is partially implemented, compiler support is partially implemented, and crates.io work is explicitly in scope.

That means a new ecosystem seam is opening up:

- projects with flat crate families may want to migrate to namespaced layouts,
- organizations will need to decide which existing crates become parents, shims, or deprecated aliases,
- documentation, import paths, package IDs, workspace naming, and release flows may all need coordinated updates,
- and teams will need to explain ownership and migration plans to downstream users without causing chaos.

The missing crate is not the namespace feature itself.

The missing crate is a **planner and receipt layer** that helps crate families adopt namespaces deliberately and reversibly.

# What it provides

- `namespace-plan.toml` — declares parent crates, child crates, alias/shim strategy, edition/toolchain assumptions, and rollout phases.
- `namespace-map.json` — records current flat names, future namespaced names, docs aliases, and package-ID implications.
- `namespace.receipt.json` — records the migration decision, ownership assumptions, generated shims, and caveats.
- `import-diff.md` — human-readable examples of `Cargo.toml`, `use`, and package-name changes.
- `cargo namespace-plan doctor` — checks a workspace or crate family for migration blockers.
- `cargo namespace-plan export` — emits a machine-readable migration bundle.
- `cargo namespace-plan scaffold` — generates shim crates, deprecation notices, or import examples from a plan.
- `*.namespacebundle.zip` — shareable artifact for organizational review, release planning, and downstream guidance.

# What the crate should provide other people

1. **A calm migration story** for organizations adopting namespaced crate families.
2. **A shared receipt format** for rename/alias/shim decisions.
3. **A documentation handoff artifact** that downstream users can actually follow.
4. **A conservative doctor** that highlights likely surprises before a publish attempt.
5. **A bridge** between RFC-level policy and ordinary crate-family maintenance.

# Persona / who it’s for

- maintainers of crate families with many related packages
- organizations that own umbrella crates and plugin ecosystems
- release engineers coordinating rename/deprecation plans
- docs / developer-relations maintainers preparing migration guides

# Users & user stories

- **Crate-family maintainer**: “Show me how our existing flat package family could map into an RFC-3243 namespace.”
- **Org maintainer**: “Generate a plan that distinguishes parent, child, shim, and deprecated crates.”
- **Release engineer**: “Export a migration bundle reviewers can read before we start publishing namespaced crates.”
- **Downstream maintainer**: “Tell me exactly which `Cargo.toml` and import-path edits this migration implies.”

# Prior art (and why it’s insufficient)

- RFC 3243 defines the feature direction.
- Cargo and crates.io tracking issues capture implementation progress.
- The Inside Rust cargo update explains the broad intended UX.

What remains missing is an **ecosystem migration kit** for ordinary maintainers: not a feature prototype, but a plan/receipt layer above it.

# Design goals

1. **Migration-first** — optimize for rename, alias, and rollout planning.
2. **Ownership-explicit** — record parent/child publication assumptions clearly.
3. **Downstream-legible** — generate artifacts people can actually act on.
4. **Conservative** — surface uncertain behavior instead of inventing guaranteed future UX.
5. **Workspace-aware** — support crate families, examples, docs, CI, and publishing checklists.

# MVP surface

- Minimal types: `NamespacePlan`, `NamespaceNode`, `AliasStrategy`, `MigrationPhase`, `NamespaceReceipt`, `NamespaceBundle`
- Minimal functions:
  - `analyze_workspace()`
  - `build_namespace_map()`
  - `render_import_diff()`
  - `write_receipt()`
  - `scaffold_shims()`
- Feature flags:
  - `cargo`
  - `serde`
  - `templates`
  - `git`

# Compatibility story

- Does not require namespaces to be fully stable before being useful.
- Can operate in “planning only” mode on stable toolchains.
- Should be able to emit bundles even when some namespace behavior is still experimental.
- Keeps exact publish/install semantics as explicit assumptions, not hidden defaults.

# Conformance & fixtures

- Fixture families with one parent crate, many sibling crates, plugin ecosystems, and mixed binaries/libraries.
- Goldens for “parent kept flat”, “child renamed”, “shim required”, and “docs alias only” cases.
- Example downstream diffs for `Cargo.toml` dependencies and `use` statements.
- Receipts for dry-run organizational review.

# Path to boring stability

- Stabilize the plan and receipt schema before automating lots of rewrites.
- Keep the first doctor focused on obvious blockers and ambiguity.
- Treat generated shims as optional outputs, not the core value.
- Separate planning semantics from exact crates.io/Cargo implementation details.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that read a crate family, produce a namespace migration plan plus import diff examples, and emit a `namespace.receipt.json` describing the rollout assumptions.

# De-risk plan

1. Start with analysis and export only; avoid publish automation.
2. Support one common migration story first: flat family → parent plus children.
3. Keep ownership and registry assumptions explicit in the receipt.
4. Add shim generation only after the plan format proves useful.

# Non-goals

- Not crates.io namespace implementation.
- Not a guarantee that final namespace UX matches today’s assumptions.
- Not a full code-rewrite engine for downstream dependents.
- Not organizational identity / access-control infrastructure.

# Architecture & API sketch

```rust
pub struct NamespacePlan {
    pub parent: String,
    pub children: Vec<NamespaceNode>,
    pub aliases: Vec<AliasStrategy>,
    pub phases: Vec<MigrationPhase>,
}

pub fn analyze_workspace(root: &Path) -> Result<WorkspaceInventory>;
pub fn build_namespace_map(inv: &WorkspaceInventory, plan: &NamespacePlan) -> NamespaceMap;
pub fn render_import_diff(map: &NamespaceMap) -> String;
pub fn write_receipt(plan: &NamespacePlan, map: &NamespaceMap) -> NamespaceReceipt;
```

Bundle draft: `namespace-plan.toml`, `namespace-map.json`, `namespace.receipt.json`, `import-diff.md`, `notes.md`.

# Security / safety model

- No hidden registry writes or publish actions in the MVP.
- Make all assumptions about ownership and registry support explicit.
- Support redaction of private workspace paths in shared bundles.
- Keep generated migration guidance deterministic and versioned.

# Maintenance & governance plan

- Track Cargo/crates.io namespace progress and version compatibility carefully.
- Keep the schema general enough for multiple rollout strategies.
- Maintain example migration templates for plugin families, SDK families, and multi-crate libraries.
- Document where human review is still required.

# Milestones

## 0.1
- workspace analysis
- migration-plan schema
- import diff rendering

## 0.2
- shim/deprecation templates
- doctor mode
- bundle export

## 1.0
- stable plan/receipt schema
- CI/release guidance adapters
- richer rollout templates

# Open questions

- Which migration assumptions are stable enough to encode today?
- How should package-name changes versus import-path changes be presented to downstream users?
- What is the smallest useful ownership model for namespaced crate families?

# Sources

- RFC 3243 packages as optional namespaces: https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
- Open namespaces project goal: https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- Cargo tracking issue: https://github.com/rust-lang/cargo/issues/13576
- crates.io tracking issue: https://github.com/rust-lang/crates.io/issues/8292
- Cargo 1.78 development-cycle notes: https://blog.rust-lang.org/inside-rust/2024/03/26/this-development-cycle-in-cargo-1.78/
