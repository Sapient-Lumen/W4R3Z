---
id: P-0428
title: Cargo Impact Planner Kit — explainable affected-package/test plans and workspace blast-radius receipts
status: idea
domains: [cargo, build-performance, ci, workspaces, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://docs.rs/guppy
  - https://docs.rs/guppy-summaries
  - https://crates.io/crates/determinator
---

# Problem

Large Rust workspaces still suffer from a very practical question that is only partially answered by existing tools:

**Given this diff, what really needs to be rebuilt, retested, re-documented, or re-benchmarked — and why?**

Rust already has strong package-graph substrate (`guppy`), build-summary substrate (`guppy-summaries`), and a change-determination crate (`determinator`). Cargo itself is also actively working on smaller cacheable units and less painful build-directory locking.

But teams still repeatedly reinvent the same higher-level logic:

- classify which changed files matter,
- map those changes onto affected packages and targets,
- decide whether doc tests, benches, examples, or integration suites should run,
- explain the “blast radius” to humans,
- and package the result so CI systems and reviewers can trust it.

The missing crate is an **impact planner** that gives workspaces a boring, explainable, conservative default for change planning.

# What it provides

- `impact-policy.toml` — declares taint rules, package criticality, public-API boundaries, proc-macro/build.rs escalation, and CI tiers.
- `impact.inputs.json` — records git diff, changed paths, package metadata snapshot, and feature/build summary data.
- `impact.plan.json` — minimal affected packages, targets, test suites, docs, benches, and confidence/explanation data.
- `impact.receipt.json` — records the planner version, reasoning chain, and why each package/target was included.
- `cargo impact plan` — generates a plan for a diff or working tree.
- `cargo impact explain <package>` — tells a human why a package is in the plan.
- `*.impactbundle.zip` — shareable artifact for CI, code review, or “why did this rebuild so much?” debugging.

# What the crate should provide other people

1. **Smaller default CI/test plans** without forcing each company to build its own planner.
2. **Explainable blast-radius analysis** instead of opaque target lists.
3. **A reusable policy surface** for workspaces with different risk tolerances.
4. **A shareable artifact** that lets CI, local dev tooling, and reviewers agree on what changed.
5. **A practical bridge** between Cargo graph substrate and organization-specific workflows.

# Persona / who it’s for

- maintainers of medium and large Rust workspaces
- CI/platform engineers
- monorepo owners
- release managers and reviewers who need to understand rebuild/test scope

# Users & user stories

- **Workspace maintainer**: “I changed docs and one internal crate; tell me the smallest credible test plan.”
- **CI engineer**: “Emit a machine-readable affected-target plan I can shard and cache.”
- **Reviewer**: “Explain why this apparently unrelated package ended up in scope.”
- **Tool author**: “Reuse one impact schema instead of inventing a bespoke affected-crates format.”

# Prior art (and why it’s insufficient)

- `guppy` models Cargo dependency graphs well.
- `guppy-summaries` records what got built and can be compared over time.
- `determinator` shows that package-change determination is useful in practice.
- Cargo is actively pursuing better build-cache structure and locking.

What remains missing is a **human-explainable planning layer** that turns diff + graph + policy into a reviewable affected-work plan, rather than merely exposing raw graph primitives.

# Design goals

1. **Conservative by default** — better to slightly over-include than to miss risky work.
2. **Explainable** — every included package or target needs a reason.
3. **Workspace-native** — supports features, proc-macros, build scripts, examples, benches, docs, and host/target splits.
4. **CI-friendly** — produce stable machine-readable plans and bundles.
5. **Composable** — can sit above `guppy`, `guppy-summaries`, and existing git metadata.

# MVP surface

- Minimal types: `ImpactPolicy`, `ChangeSet`, `ImpactPlan`, `ImpactReason`, `ImpactReceipt`, `ImpactBundle`
- Minimal functions:
  - `collect_changes()`
  - `plan_impact()`
  - `explain_package()`
  - `write_plan()`
  - `write_bundle()`
- Feature flags:
  - `git`
  - `guppy`
  - `summaries`
  - `serde`
  - `html-report`

# Compatibility story

- Reuses `cargo metadata`/`guppy` for graph understanding.
- Accepts `guppy-summaries` when available, but does not require them for the MVP.
- Can ingest git diffs from local repos or CI-provided changed-file lists.
- Avoids changing Cargo internals; this is a planner above existing substrate.

# Conformance & fixtures

- Fixture workspaces with internal-only changes, public-API changes, feature-flag changes, proc-macro changes, and `build.rs` changes.
- Goldens for “docs-only”, “tests-only”, “workspace-wide taint”, and “safe narrow diff” scenarios.
- Comparison corpus showing how different policies affect affected-target breadth.
- Replay bundles for CI disagreements.

# Path to boring stability

- Stabilize `impact.plan.json` and `ImpactReason` categories early.
- Keep the first policy language intentionally small and explicit.
- Start with package/target/test planning before adding remote-cache optimization logic.
- Prefer conservative reasoning rules over hard-to-explain heuristics.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 5/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that take a git diff plus workspace metadata and emit an explainable affected-package/test/doc plan with machine-readable reasons.

# De-risk plan

1. Start with path-to-package and package-graph propagation only.
2. Add a few conservative escalation rules (`build.rs`, proc-macros, workspace manifests).
3. Validate on open-source workspaces with golden expected plans.
4. Add feature/build-summary overlays only after the core explanations are trusted.

# Non-goals

- Not an exact predictor of rustc incremental compilation internals.
- Not a replacement for Cargo.
- Not an opaque ML ranking engine.
- Not a global remote-cache system.

# Architecture & API sketch

```rust
pub struct ImpactPlan {
    pub packages: Vec<PlannedPackage>,
    pub targets: Vec<PlannedTarget>,
    pub reasons: Vec<ImpactReason>,
    pub confidence: Confidence,
}

pub fn collect_changes(repo: &RepoState) -> Result<ChangeSet>;
pub fn plan_impact(policy: &ImpactPolicy, changes: &ChangeSet, graph: &PackageGraph) -> ImpactPlan;
pub fn explain_package(plan: &ImpactPlan, package: &str) -> Vec<ImpactReason>;
pub fn write_bundle(bundle: &ImpactBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `impact-policy.toml`, `changes.json`, `graph.snapshot.json`, `impact.plan.json`, `impact.receipt.json`, `notes.md`.

# Security / safety model

- Support redaction of repo paths and private crate names in shared bundles.
- Never present low-confidence narrow plans as certainty.
- Keep policy evaluation deterministic and inspectable.
- Make “manual override” visible in the receipt.

# Maintenance & governance plan

- Track planner rules as named, versioned reason categories.
- Maintain a small public fixture workspace suite.
- Keep ecosystem-specific adapters optional.
- Publish example policies for OSS, medium monorepos, and high-assurance repos.

# Milestones

## 0.1
- diff ingestion
- package-graph propagation
- `cargo impact plan`

## 0.2
- `cargo impact explain`
- stable `impact.plan.json`
- fixture workspace corpus

## 1.0
- `*.impactbundle.zip`
- policy tiers
- CI/report adapters

# Open questions

- What is the smallest useful reason taxonomy that still explains real workspace behavior?
- How should feature changes and public-API drift interact in conservative planning?
- Which target kinds deserve separate planning semantics in the MVP?

# Sources

- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Rework Cargo Build Dir Layout: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- `guppy`: https://docs.rs/guppy
- `guppy-summaries`: https://docs.rs/guppy-summaries
- `determinator`: https://crates.io/crates/determinator
