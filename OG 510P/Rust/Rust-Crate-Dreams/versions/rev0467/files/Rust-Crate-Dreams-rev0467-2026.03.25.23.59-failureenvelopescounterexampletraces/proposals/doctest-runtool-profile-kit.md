---
id: P-0481
title: Doctest Runtool Profile Kit — target-aware runner profiles, route receipts, execution-basis audits, and emulator/VM handoff bundles
status: idea
domains: [rustdoc, cargo, testing, docs, cross-compilation, ci]
last_reviewed: 2026-03-22
evidence:
  - https://doc.rust-lang.org/rustdoc/command-line-arguments.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#doctest-xcompile
  - https://doc.rust-lang.org/beta/releases.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/commands/cargo-test.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  - https://doc.rust-lang.org/rustdoc/unstable-features.html#--persist-doctests-persist-doctest-executables-after-running
---

# Problem

Rust documentation tests are no longer just “host-only examples that happen to compile.”

Current upstream progress made them much more operational:

- rustdoc now has stable `--test-runtool` and `--test-runtool-arg` support for running doctests under a wrapper like QEMU or another VM/runtime,
- Cargo now honors `--target` for doctests,
- release notes keep target-specific `ignore-*` attributes official,
- Cargo configuration still supports target-specific runner settings and environment overrides,
- Cargo’s `cargo test` docs still keep the compile-vs-run working-directory split explicit for doctests,
- and Rust-for-Linux still wants stable rustdoc support for special-environment doc tests.

That is real substrate, but maintainers still lack a boring workflow for questions like:

- which route actually selected the effective runner for this target lane,
- whether the current lane came from explicit rustdoc wrapper flags or inherited Cargo target-runner configuration,
- what working-directory assumptions the wrapper actually depended on,
- which examples were intentionally ignored for this target versus accidentally unreviewed,
- and how to hand another maintainer one compact artifact that explains route, basis, results, and imports together.

Today the workflow is still mostly:

- write ad hoc `cargo test --doc --target ...` commands,
- pass runner settings through config, environment, or shell scripts,
- sprinkle `ignore-*` attributes manually,
- and hope the next maintainer can reconstruct what “this docs example is supported on target X” really meant.

The missing crate is not another docs portal and not another generic test runner.

The missing crate is a **Doctest Runtool Profile Kit**: a crate and cargo-adjacent tool that turn cross-target documentation examples into a reviewable **runner profile, route receipt, execution-basis receipt, ignore audit, target matrix, and portable support bundle**.

# What it provides

- `doctest-profile.toml` — declares target triples, runner program/args, env variables, working-directory policy, and supported target categories.
- `runner-route.receipt.json` — explains whether execution came from explicit rustdoc flags, Cargo target-runner config, environment override, direct execution, or manual-review-only reconstruction.
- `execution-basis.receipt.json` — records target, support class, compile/run directory basis, ignore-target policy, and adjacent imported receipts.
- `doctest-target-matrix.json` — item-by-item view of which doctests are expected to `run`, `compile-only`, `ignore`, or `needs-runner` on which targets.
- `doctest-ignore-audit.json` — records all `ignore`, `ignore-*`, and related annotations with reasons, target matches, and stale-policy warnings.
- `doctest.results.json` — normalized results from one run, including runner identity, target, execution status, and captured failure summaries.
- `doctest.receipt.json` — exact rustdoc/Cargo/toolchain/profile context, runner command line, and environment assumptions.
- `doctest.diff.json` — compare two runs or two policies and classify `newly-runnable`, `newly-ignored`, `runner-changed`, `basis-changed`, `result-changed`, and `annotation-drift`.
- `doctest-runtool-support-bundle.manifest.json` — portable handoff manifest that keeps route, basis, results, and imports separate.
- `cargo doctest-profile route` — resolve and emit the effective runner route without executing doctests.
- `cargo doctest-profile basis` — emit execution-basis receipts and target/ignore audits.
- `cargo doctest-profile run` — execute one target profile and emit a shareable route/basis/results bundle.
- `cargo doctest-profile diff <old> <new>` — compare two receipts or matrices.
- `*.doctestrun.zip` — portable artifact for cross-target docs CI, emulator failures, and maintainer handoff.

# What the crate should provide other people

1. **A boring policy file** for cross-target docs-example support.
2. **An explicit route receipt** for how the effective runner was selected.
3. **An explicit execution basis** for target, working-directory, and ignore-policy truth.
4. **A durable runner receipt** for emulators, VMs, or special runtimes.
5. **An ignore-audit workflow** so target-specific annotations stop drifting silently.
6. **A bridge** between new rustdoc/Cargo execution capabilities and ordinary docs maintenance.

# Persona / who it’s for

- embedded and systems maintainers using emulators or custom runners
- docs maintainers who want examples to stay honest across targets
- CI owners wiring rustdoc examples into non-host environments
- teams like Rust-for-Linux, WASI, kernel, or firmware projects with special test environments

# Users & user stories

- **Embedded maintainer**: “Run the same docs examples under QEMU on one target and compile-only on another, with one reviewable profile and one route receipt.”
- **Docs reviewer**: “Show me which examples were skipped by `ignore-*` policy, which route selected the runner, and whether those annotations still match our supported targets.”
- **CI owner**: “Attach one artifact showing runner settings, working-directory basis, target, and doctest results when a docs job fails.”
- **Platform maintainer**: “Compare docs-example support before and after a target/runtime change without flattening route drift into plain pass/fail drift.”

# Prior art (and why it’s insufficient)

- rustdoc’s stable runner flags are powerful, but they are still low-level CLI substrate rather than a reusable policy/route/basis workflow.
- Cargo honoring `--target` for doctests is important, but it does not by itself produce route receipts, execution-basis receipts, or ignore audits.
- Cargo target-runner config is useful, but its presence in config or environment does not explain what a docs CI lane was actually claiming.
- Existing doctest extraction work (including Rust-for-Linux integration) proves the ecosystem needs special-environment docs execution, but that work does not give ordinary teams a compact stable artifact.
- P-0455 Doctest Extraction & Support Contract Kit in this archive addresses the nightly extraction/rewrite/grouping/handoff seam; it is not the same as a stable runner-route and execution-basis layer.

What remains missing is a **profile + route receipt + execution-basis receipt + bundle layer** above rustdoc/Cargo’s doctest execution substrate.

# Design goals

1. **Stable-surface first** — start from stable runner flags, stable docs annotations, and documented Cargo config surfaces.
2. **Target-aware** — treat `ignore-*` and `--target` behavior as first-class policy, not comments.
3. **Runner explicitness** — record exactly which emulator/runtime/VM wrapper executed the test and how it was selected.
4. **Working-directory honesty** — keep compile and run directory basis visible.
5. **Docs-maintainer friendly** — optimize for reviewable matrices and receipts, not only raw execution.
6. **Diffable** — changes in support policy should be obvious across releases.

# MVP surface

- Minimal types: `DoctestProfile`, `RunnerRouteReceipt`, `ExecutionBasisReceipt`, `DoctestTargetMatrix`, `IgnoreAudit`, `DoctestResults`, `DoctestReceipt`, `DoctestDiff`, `DoctestBundle`
- Minimal functions:
  - `resolve_runner_route()`
  - `build_execution_basis_receipt()`
  - `build_doctest_target_matrix()`
  - `audit_ignore_annotations()`
  - `run_doctest_profile()`
  - `diff_doctest_receipts()`
  - `write_doctest_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `emulator`
  - `ci`

# Compatibility story

- Works with stable rustdoc runner flags first.
- Integrates with Cargo doctest cross-compilation behavior as it exists today.
- Must distinguish “supported because it ran via explicit runtool route” from “supported because a Cargo target runner happened to apply” from “supported because policy says compile-only or ignore.”
- Should remain useful even if richer doctest extraction or scheduling surfaces stabilize later, because route and basis receipts still matter.
- May import unstable `--persist-doctests` artifacts as evidence, but must not make them mandatory for the stable contract.

# Conformance & fixtures

- One host-only fixture with no custom runner.
- One fixture where a Cargo target-runner route applies without explicit rustdoc runtool flags.
- One fixture where target-specific ignore annotations are intentional and reviewable.
- One fixture where run-directory assumptions matter for assets or wrapper scripts.
- One fixture where runner arguments changed and results must be classified as `runner-changed` rather than plain pass/fail drift.
- Goldens for `run`, `compile-only`, `ignore`, `needs-runner`, `route-changed`, and `basis-changed` states.

# Path to boring stability

- Stabilize route, basis, and bundle schemas before supporting many adapters.
- Keep the first version focused on audit and receipts, not fancy dashboards.
- Treat missing runner/environment data as explicit gaps.
- Prefer conservative target classification over magical inference.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A crate and cargo subcommand that read one doctest runner profile, resolve the effective runner route, emit an execution-basis receipt, audit `ignore-*` annotations, run one target profile, and emit a diffable receipt bundle.

# De-risk plan

1. Start with a tiny vocabulary: `run`, `compile-only`, `ignore`, `needs-runner`.
2. Support one simple runner profile plus host-only mode first.
3. Resolve and emit route receipts before trying to infer too much from execution.
4. Validate on one emulator-backed project and one ordinary library with target-specific ignores.
5. Keep ignore-audit and working-directory output prominent so policy drift is visible early.

# Non-goals

- Not a replacement for rustdoc or Cargo.
- Not a generic emulator-management framework.
- Not a docs quality dashboard.
- Not a nightly-only doctest extraction system; that is a distinct seam.
- Not a substitute for extraction-basis/grouping work in P-0455.

# Architecture & API sketch

```rust
pub struct RunnerRouteReceipt {
    pub target: String,
    pub route_kind: RouteKind,
    pub wrapper: Option<RunnerSpec>,
    pub declaration_sources: Vec<DeclarationSource>,
}

pub struct ExecutionBasisReceipt {
    pub target: String,
    pub support_class: SupportClass,
    pub compile_directory_basis: DirectoryBasis,
    pub run_directory_basis: DirectoryBasis,
}

pub fn resolve_runner_route(root: &std::path::Path, profile: &DoctestProfile) -> Result<RunnerRouteReceipt>;
pub fn build_execution_basis_receipt(root: &std::path::Path, profile: &DoctestProfile) -> Result<ExecutionBasisReceipt>;
pub fn run_doctest_profile(root: &std::path::Path, profile: &DoctestProfile) -> Result<DoctestReceipt>;
```

Bundle draft: `doctest-profile.toml`, `runner-route.receipt.json`, `execution-basis.receipt.json`, `doctest-target-matrix.json`, `doctest-ignore-audit.json`, `doctest.results.json`, `doctest.receipt.json`, `doctest.diff.json`, `notes.md`.

# Security / safety model

- Treat runner programs and runner arguments as code-execution surfaces.
- Never hide that a result depended on an emulator, VM, Cargo config, or environment override.
- Permit redaction of local paths and environment variables in exported bundles.
- Keep annotation audits explicit so ignored doctests do not masquerade as passed support.
- Treat unstable `--persist-doctests` artifacts as optional evidence only.

# Maintenance & governance plan

- Track rustdoc doctest flags, Cargo target-runner behavior, working-directory rules, and target-annotation behavior.
- Keep schemas compact and versioned.
- Maintain fixtures for host-only, emulator-backed, route-drift, and ignore-policy cases.
- Coordinate carefully with any future rustdoc extraction or special-environment work so the stable runner-route layer stays narrow.

# Milestones

## 0.1
- profile parser
- runner-route receipt
- execution-basis receipt
- target matrix builder
- ignore audit

## 0.2
- runner receipt export
- diffing
- CI bundle output

## 1.0
- stable bundle schema
- curated emulator/host fixtures
- policy guidance for common target classes

# Open questions

- What is the smallest route vocabulary that still helps maintainers?
- How much runner/environment detail should be mandatory in exported receipts?
- Should compile-only expectations be modeled separately from `ignore-*` annotations in the first stable schema?
- How should local config/env routes be redacted without losing review value?

# Sources

- rustdoc command-line arguments (`--test-runtool`, `--test-runtool-arg`): https://doc.rust-lang.org/rustdoc/command-line-arguments.html
- Cargo unstable docs (`doctest-xcompile` honoring `--target`): https://doc.rust-lang.org/cargo/reference/unstable.html#doctest-xcompile
- Rust release notes (cross-target doctests, `ignore-*`, stable runtool flags): https://doc.rust-lang.org/beta/releases.html
- Cargo configuration (`target.<triple>.runner`, `target.<cfg>.runner`, env override): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo test docs (execution model caveat, compile/run directories): https://doc.rust-lang.org/cargo/commands/cargo-test.html
- Rust for Linux tooling goal (special-environment doc tests): https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- rustdoc unstable features (`--persist-doctests`): https://doc.rust-lang.org/rustdoc/unstable-features.html#--persist-doctests-persist-doctest-executables-after-running
