# Design: Resolution Doctor Kit (`cargo resolve`, `resolve-pack/v0`)

## Goal
Make Cargo dependency and feature resolution **explainable, portable, and composable** by defining:
- a reference CLI (`cargo resolve`),
- stable machine-readable reports (`resolve-report/v0`, `feature-trace/v0`, `conflict-report/v0`),
- a minimized reproducer format (`resolve-repro/v0`),
- and a bundle format (`resolve-pack/v0`).

This is not just “prettier `cargo tree` output.” The point is to create a common evidence layer for resolution-sensitive tooling.

## References (signals)
- Cargo plumbing goal: `cargo metadata` excludes feature resolution; feature resolution is its own build phase; `--unit-graph` is one experiment.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- PubGrub goal: better error messages, better MSRV support, CVE-aware resolution, richer cargo extensions.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- cargo-semver-checks 2025H2 goal: witness programs, implied-bounds precision, cross-crate linting, and the need to uniquely determine where foreign items came from.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- July 2025 goals update: docs.rs hosting rustdoc JSON helps, but determining active dependency features recursively is still missing from lockfile/Cargo interfaces.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- November 2025 goals update: rustdoc JSON now includes rlib information for cross-crate work, but Cargo-side blockers remain and dependency-feature correctness still needs more work.
  https://blog.rust-lang.org/2025/12/16/Project-Goals-2025-November-Update.md/
- Cargo 1.94 development cycle: `cargo report timings`, `cargo report rebuild`, `cargo report sessions`.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Core UX: `cargo resolve`
- `cargo resolve doctor`
  - run resolution with structured tracing
  - emit `resolve-pack/v0`
- `cargo resolve explain <crate>`
  - show selected version, competing constraints, and why this package is present
- `cargo resolve features <crate>`
  - show which features are active, by whom, and in which scope (normal/dev/build/proc-macro/target)
- `cargo resolve diff --against <lockfile|ref|report>`
  - compare two resolution states and classify changes
- `cargo resolve minimize [--preserve <symptom>]`
  - emit a reduced reproducer preserving a duplicate, conflict, feature activation, or resolution failure
- `cargo resolve verify-pack <path>`
  - validate schema versions, checksums, and redaction state

## Artifact set
### `resolve-report/v0`
A complete snapshot of the chosen graph:
- workspace identity and member selection
- resolver version / Cargo version / rustc version
- chosen packages, versions, sources, and dependency kinds
- target and host partitions
- duplicate-package records and reason codes
- relevant overrides: patch, replace, source replacement, precise update pins, yanked avoidance
- deterministic IDs for diffing

### `feature-trace/v0`
Not just “features enabled,” but *why*:
- per package: active features
- activation sources:
  - dependency edge
  - default feature
  - target condition
  - build-dependency or proc-macro context
  - workspace/root selection
- host/target separation
- stable reason codes such as:
  - `FEATURE:DEFAULT`
  - `FEATURE:EDGE-REQUESTED`
  - `FEATURE:BUILD-CONTEXT`
  - `FEATURE:TARGET-SPECIFIC`
  - `FEATURE:WORKSPACE-UNIFIED`

### `conflict-report/v0`
For failures or surprising duplicates:
- incompatibility chain / conflict core
- packages and constraints involved
- candidate relaxations when they can be described safely
- human summary plus stable machine codes

### `resolve-repro/v0`
A minimized issue attachment:
- reduced `Cargo.toml` / `Cargo.lock`
- workspace slice and target selection
- preservation claim (`duplicate`, `failure`, `unexpected-feature`, `unexpected-version`)
- reduction log for transparency

### `resolve-pack/v0`
A portable bundle:
- `manifest.json`
- `resolve-report.json`
- `feature-trace.json`
- `conflict-report.json` (optional)
- `resolve-repro/` (optional)
- checksums, redaction markers, provenance pointers

## Design principles
- **Explain decisions, not just results.** Users need “why,” not only the final lockfile.
- **One evidence layer, many consumers.** Public API analysis, policy, CI bots, and IDEs should not each reinvent resolution tracing.
- **Reason codes over brittle prose.** Automation should survive wording changes.
- **Respect Cargo boundaries.** Start as a plugin and artifact adapter over existing interfaces and experiments; upstream later if it proves out.
- **Redaction is first-class.** Private registries, paths, and mirrors must be redactable without invalidating the report structure.

## Shared stack note
Treat this kit plus [`design/feature-kit.md`](./feature-kit.md) as the shared **Dependency Control Stack**, with [`design/dependency-control-stack.md`](./dependency-control-stack.md) and [`design/dependency-control-pilot-program.md`](./dependency-control-pilot-program.md) as the synthesis / rollout layer above them.

Design rule: **Resolution Doctor owns chosen-graph truth; Feature Kit owns activated-capability and minimization truth; public/private dependency policy remains a downstream handoff, not something this kit silently absorbs.**

Additional boundary: [`design/resolution-strategy-kit.md`](./resolution-strategy-kit.md) owns **objective-profile / alternative-candidate / accepted-tradeoff truth above the chosen graph**. Resolution Doctor should feed that layer, not absorb it.

## Integration points
- **Feature Kit** consumes `feature-trace/v0` for policy and minimization.
- **Public API Kit** uses resolution evidence to know which foreign items and dependency features matter.
- **Policy Kit** uses selected-version and source evidence for compliance gates.
- **Workspace Governance Kit** uses it to explain inheritance and cross-member resolution differences.
- **Cargo Report Kit** aligns conventions and report ergonomics with existing `cargo report *` work.

## Hard problems (explicitly scoped)
1. **Cargo interface gaps**
   - v0 should record provenance and confidence levels when some information must be inferred.
2. **Feature matrix explosion**
   - v0 should report the selected build context, not every hypothetical graph.
3. **Cross-crate analysis requirements**
   - this kit does not itself solve rustdoc JSON completeness, but it should export the inputs other tools need.
4. **Resolver performance overhead**
   - detailed traces should be optional or sampled, with a smaller always-on baseline report.
5. **Alternative registries and mirrors**
   - support source redaction and stable source IDs.

## Evaluation plan
Use the ranked rollout in [`design/dependency-control-pilot-program.md`](./dependency-control-pilot-program.md).

Pilot on five classes of lanes:
1. a single-crate graph + feature-why lane,
2. a workspace unification / split-selection lane,
3. a public/private boundary handoff lane,
4. an MSRV / publish-time / upgrade lane,
5. a consumer-import lane.

Within those lanes, prove the stack on concrete repos such as:
1. a workspace with duplicate versions and target-specific deps,
2. a library whose semver checks depend on foreign-item and feature accuracy,
3. an enterprise monorepo needing CI-readable diffs and private-registry redaction.

Success bar:
- a maintainer can attach one `resolve-pack/v0` to a bug or PR,
- CI can diff resolution changes without scraping human output,
- other kits can consume the pack instead of rebuilding their own ad hoc explainers.
