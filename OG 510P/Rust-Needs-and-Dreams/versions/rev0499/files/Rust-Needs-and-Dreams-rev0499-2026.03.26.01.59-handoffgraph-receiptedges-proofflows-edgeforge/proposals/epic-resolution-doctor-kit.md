# Epic Proposal: Resolution Doctor Kit (`cargo resolve`)

## One-sentence pitch
Turn Cargo’s dependency and feature resolution into a first-class evidence surface: explain version choices, trace feature activation, minimize confusing cases, and export portable reports that other Rust tools can build on.

## Deliverables
- `cargo-resolve` reference implementation
- Schemas:
  - `resolve-report/v0`
  - `feature-trace/v0`
  - `conflict-report/v0`
  - `resolve-repro/v0`
  - `resolve-pack/v0`
- Adapters/integrations:
  - `cargo tree`
  - `cargo metadata` / `--unit-graph`-style sources where applicable
  - future PubGrub-based resolver libraries
  - Feature Kit, Public API Kit, Policy Kit, Workspace Governance Kit
- Docs:
  - issue-reporting workflow
  - CI diff workflow
  - redaction guidance for private registries and paths

## Why now (signals)
- Cargo’s plumbing effort explicitly says the existing machine-facing surface is too thin and that `cargo metadata` excludes feature resolution.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The PubGrub effort aims for better Cargo error messages, better MSRV support, CVE-aware resolution, and a richer ecosystem of cargo extensions.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- `cargo-semver-checks` progress shows that accurate recursive dependency-feature information and cross-crate provenance are still missing pieces for ecosystem-critical tooling.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  https://blog.rust-lang.org/2025/12/16/Project-Goals-2025-November-Update.md/
- Cargo is already standardizing report-oriented UX (`cargo report timings`, `cargo report rebuild`, `cargo report sessions`), making a resolution report family much more plausible than it was a year ago.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Non-goals
- Replacing Cargo’s resolver in v0
- Exhaustively enumerating every hypothetical feature matrix
- Perfect remediation suggestions for every conflict
- Forcing immediate upstream stabilization

## Strategic value
This kit is high leverage because it addresses an ecosystem-wide substrate problem instead of one symptom:
- maintainers get issue-attachable, reviewable explanations,
- semver and public-API tooling get the resolution facts they lack,
- policy and security tooling gain source/version provenance with stable schemas,
- future resolver and plumbing work gets a concrete consumer and artifact contract.

## Milestones
1. **v0 plugin + reports**
   - produce `resolve-report/v0` and `feature-trace/v0`
   - basic explain and diff commands
2. **v0.2 conflict + repro workflows**
   - `conflict-report/v0`
   - reduced reproducer export
   - redaction support
3. **v1 ecosystem convergence**
   - deeper integration with Cargo report/plumbing work
   - stronger feature-source fidelity
   - shared consumption by semver/policy/workspace tools


## Stack posture
Treat this proposal as one half of the shared **Dependency Control Stack** with the companion kit. The synthesis and rollout layer lives in [`design/dependency-control-stack.md`](../design/dependency-control-stack.md) and [`design/dependency-control-pilot-program.md`](../design/dependency-control-pilot-program.md). The stack must keep chosen-graph truth, feature/unification truth, and downstream API/policy handoffs distinct instead of flattening them into one dependency-health verdict.
