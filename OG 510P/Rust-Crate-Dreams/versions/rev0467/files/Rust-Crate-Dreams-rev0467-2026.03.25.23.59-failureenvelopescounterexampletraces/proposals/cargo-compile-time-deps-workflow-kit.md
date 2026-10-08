---
id: P-0494
title: Cargo Compile-Time-Deps Workflow Kit — tool-surface parity receipts, root-lane evidence, and fallback-to-full-build diagnosis
status: idea
domains: [cargo, ide, build, devtools, workspace]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
  - https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
  - https://rust-analyzer.github.io/book/configuration
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/cargo/commands/cargo-build.html
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
  - https://doc.rust-lang.org/cargo/commands/cargo-check.html
  - https://github.com/rust-lang/rust-analyzer/issues/18528
  - https://github.com/rust-lang/rust-analyzer/issues/17126
---

# Problem

Rust now has a more explicit **tool-only compile surface** than it used to, but the receiver-facing artifact is still missing.

Official Cargo docs now describe `--compile-time-deps` as a permanently unstable mode that builds only proc-macros, build scripts, and their required dependencies, then runs the build scripts. The docs explicitly say it is intended for tools like rust-analyzer and will never be stabilized as an ordinary end-user workflow.

At the same time, RFC 3477 makes the policy boundary explicit: Rust’s standard stability guarantee is tied to `cargo build`, while `cargo check` is intentionally a faster, less complete answer. And rust-analyzer’s current configuration surface exposes `targetDir`, `target`, `sysrootSrc`, `check.overrideCommand`, `cargo.buildScripts.overrideCommand`, and related knobs because ordinary teams keep needing a workable editor/build split.

That means the missing crate is **not** a new checker, not a rust-analyzer fork, and not an attempt to claim that tool-only builds are equivalent to real builds.

The missing crate is a **Cargo compile-time-deps workflow kit**: a crate and cargo-adjacent tool that turns “our IDE or wrapper is using a tool-only or check-like compile surface” into a portable **receipt, parity diagnosis, and fallback recommendation bundle**.

# Sharper reading after the latest Cargo / rust-analyzer docs

The archive should now treat this proposal as a **tool workflow contract**, not as a generic performance tool.

The important observation is that three pieces of substrate are now explicit enough to build on:

1. Cargo has a documented tool-only compile mode.
2. rust-analyzer documents the exact command/custom-command/config surface it uses for build scripts and checks.
3. Cargo’s build-dir-layout goal explicitly names Cargo↔rust-analyzer lock contention and shared-cache pain as first-class upstream motivation.

So the value of this crate is no longer “discover that editors are different.”
It is to hand another person a stable, reviewable answer to:

- what command really ran,
- what compile surface it covered,
- what assumptions were in play,
- what comparison baseline is being claimed,
- what risks that creates,
- and whether a full build fallback is required.

# 2026-03-08 implementation refresh — comparison baselines and override provenance

This proposal is now more implementation-ready than before because the official rust-analyzer docs expose more of the exact workflow seam than many teams realize.

Five details especially matter:

1. `check.overrideCommand` and `cargo.buildScripts.overrideCommand` are explicit first-class configuration surfaces, and both require JSON-producing commands.
2. `check.overrideCommand` supports `{label}` and rust-analyzer documents that using it behaves much like `check.workspace = false`, which means package-selection drift is not incidental noise but a real comparison-boundary fact.
3. rust-analyzer documents `cargo.targetDir` as a deliberate trade-off: less lock contention in exchange for duplicate build artifacts.
4. rust-analyzer documents `cargo.buildScripts.useRustcWrapper = true` by default, which means build-script/proc-macro workflow provenance can differ from a plain terminal build even when the user did not set a custom wrapper manually.
5. Issue reports show custom or relative override commands are still easy to misdiagnose, while toolchain-specific paired build-script overrides can fix real workflows.

That means the crate should now freeze two extra artifact lanes instead of treating them as incidental log details:

- one **comparison-baseline lock** that says what this tool-facing run is being compared *against*,
- and one **override-command receipt** that says how rust-analyzer or a wrapper actually invoked Cargo-like commands.

# 2026-03-08 implementation refresh — selection coverage and workspace invocation truth

This proposal is more implementation-ready again because current rust-analyzer docs and issue reports make one more boundary explicit: **tool-workflow support truth is also a coverage problem**.

Five additional details matter now:

1. rust-analyzer documents `cargo.allTargets = true` by default and says `check.allTargets` inherits that unless set explicitly.
2. Cargo documents that `--all-targets` expands to `--lib --bins --tests --benches --examples`, which means target-class coverage is a real, nameable boundary instead of vague “editor completeness.”
3. rust-analyzer documents `check.workspace = true` by default, and says `{label}` behaves much like `check.workspace = false`.
4. rust-analyzer documents separate `per_workspace` / `once` invocation strategies for both build-script and check override commands, with different working-directory expectations.
5. Issue reports show concrete support incidents where `allTargets = false` leaves a proc-macro missing and where `check.workspace = false` still leaks broader diagnostics on first start.

That means the crate should now freeze two more artifact lanes instead of burying them in ad hoc notes:

- one **selection-coverage report** that says which package/target classes/dev-dependency surfaces were actually covered,
- and one **workspace-invocation receipt** that says how linked projects, invocation strategy, and working-directory rules shaped the observed run.


# 2026-03-16 implementation refresh — root-lane truth and optional session imports

This proposal is more buildable again because the official Cargo story around **root layout** and **persisted build-analysis sessions** is now sharper than when the archive last touched it.

Five current facts matter:

1. the March 13, 2026 call-for-testing says teams should run tests, release processes, and anything else that touches build-dir / target-dir under `-Zbuild-dir-new-layout`, because many projects still rely on unspecified internal details,
2. that same post says Cargo 1.91 already lets users separate intermediate build artifacts (`build-dir`) from final artifacts (still in `target-dir`),
3. Cargo’s unstable docs explicitly say the new build-dir layout exists to unblock caching and locking improvements,
4. Cargo’s unstable docs also say `[build.analysis] enabled = true` is safe to leave in config even on stable because it only emits an unknown-config warning there,
5. and the same docs expose persisted session IDs plus `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.

That means **P-0494** should stop acting as though “rust-analyzer targetDir policy” is the whole root story.
A tool-facing workflow can now differ along at least four lanes:

- shared vs isolated `target-dir`,
- shared vs isolated `build-dir`,
- tool-only vs fuller-build compile surface,
- and optional imported Cargo build-analysis sessions.

So a worthy crate here should now freeze three more receiver-facing artifacts:

- one **root-lane receipt** that records how target-dir and build-dir were actually arranged for the observed tool run,
- one **evidence-source receipt** that says which facts came from rust-analyzer config, observed argv/env, Cargo config, or imported sessions,
- and one **tool-session link** that can optionally tie a tool-facing run to a Cargo build-analysis session without pretending that linkage is always available or exact.

# What it provides

- `tool-build-policy.toml` — declares which workflows are allowed to use compile-time-only or check-like builds (`ide`, `macro-index`, `buildscript-discovery`, `ci_preflight`, `manual_diagnosis`), what parity level is expected, and when full-build fallback is mandatory.
- `tool-build.receipt.json` — records one observed tool-facing invocation: command, scope, workspace/package selection, targets, target-dir/build-dir facts, sysroot/source facts, wrapper/override facts, and whether unstable Cargo modes were involved.
- `compile-surface.manifest.json` — normalized view of what was and was not built: proc-macros, build scripts, host units, target units, tests/examples, skipped codegen-bearing units, and feature/target assumptions.
- `parity-check.report.json` — classifies whether a workflow is `acceptable_tool_surface`, `missing_runtime_surface`, `target_mismatch`, `sysroot_source_missing`, `build_script_cfg_risk`, `full_build_required`, or `manual_review_required`.
- `fallback.plan.json` — suggests concrete next steps such as `run_full_build`, `align_target_dir_policy`, `install_rust_src`, `pin_override_command`, `narrow_workspace_scope`, `align_targets`, `freeze_comparison_baseline`, or `accept_tool_only_mode`.
- `comparison-baseline.lock` — freezes the claim being made (`tool_vs_tool`, `tool_vs_full_build`, `tool_vs_terminal_build`, or `tool_vs_policy`), plus selection scope, target scope, and exactness.
- `override-command.receipt.json` — records effective check/build-script override commands, placeholder use (`{label}`, `{saved_file}`), command-path resolution style, JSON-output expectations, wrapper hints, and pairing status.
- `selection-coverage.report.json` — records package scope, target-class coverage, dev-dependency visibility, known omissions, proc-macro availability risk, and exact/manual-review boundaries.
- `workspace-invocation.receipt.json` — records linked-project count, invocation strategy (`per_workspace` or `once`), working-directory mode, observed-vs-expected run count, and whether startup leakage or root ambiguity requires conservative reading.
- `root-lane.receipt.json` — records how `target-dir`, `build-dir`, and final-artifact assumptions were arranged for the observed tool run, whether rust-analyzer isolation only changed one lane, and whether duplicate-artifact trade-offs remained in play.
- `evidence-source.receipt.json` — records which facts were observed directly from rust-analyzer config, argv/env, Cargo metadata/config, imported build-analysis sessions, or manual annotations.
- `tool-session.link.json` — optional link to one or more Cargo build-analysis session IDs when the tool-facing run can be conservatively associated with persisted Cargo session data.
- `tool-build.diff.json` — compares two tool receipts or compares a tool receipt against a fuller-build witness.
- `cargo tool-surface snapshot` — capture one workflow receipt and bundle.
- `cargo tool-surface doctor` — explain whether the current IDE/wrapper/tool-only setup is likely to mislead or requires a full-build fallback.
- `cargo tool-surface diff <old> <new>` — compare receipts across toolchains, editor settings, targets, or workspace selections.
- `cargo tool-surface import-session` — attach optional Cargo build-analysis session IDs and imported report provenance when they are available.
- `*.toolbuild.zip` — portable support artifact for IDE setup docs, CI preflight discussion, and support debugging.

# What the crate should provide other people

1. **An honest answer to “what exactly did this tool-facing run build?”** instead of vague references to “cargo check”.
2. **A boring artifact** that can travel between IDE users, maintainers, CI, and support engineers.
3. **A parity vocabulary** that distinguishes “good enough for editor intelligence” from “must fall back to a real build”.
4. **A frozen comparison baseline** so “editor run succeeded” is not silently treated as “workspace build proved the same thing.”
5. **Coverage truth** about which workspace members, target classes, dev-dependencies, and proc-macro-bearing lanes were actually present.
6. **A compact diagnosis of target-dir, build-dir, target, sysroot, build-script, wrapper, override-command, and invocation-strategy assumptions** without scraping ad hoc logs.
7. **Evidence provenance** so another person can tell which claims came from config, observed commands, imported Cargo sessions, or manual annotation.
8. **A clean boundary** between tool-facing compile surfaces and the stronger guarantees tied to `cargo build`.

# Persona / who it’s for

- rust-analyzer-heavy workspace maintainers
- IDE/plugin authors and custom wrapper authors
- CI engineers designing preflight versus release pipelines
- teams with many build scripts, proc-macros, generated cfgs, or unusual targets

# Users & user stories

- **Workspace maintainer**: “Show me whether our editor workflow is only compiling build-time crates, and whether that is acceptable for this workspace.”
- **IDE integrator**: “Give me one stable artifact describing what my wrapper built and why it fell back to a full build.”
- **Support engineer**: “Tell me whether this missing symbol or missing cfg came from a tool-only compile surface, missing sysroot sources, target mismatch, or a custom override command.”
- **Developer**: “Explain whether I should trust this editor result or rerun a real build.”

# Prior art (and why it’s insufficient)

- Cargo’s `--compile-time-deps` docs explain the mechanism, but not the maintainer workflow above it.
- rust-analyzer exposes many relevant configuration knobs, but teams still have to stitch together expectations by hand.
- `cargo metadata --format-version` is a stable, versioned graph/context substrate, but it does not tell another person what tool-facing command actually ran or whether a full build fallback is warranted.
- The archive already has **P-0490 Cargo Lock Contention Witness Kit**. That proposal is about **who blocked whom**.
- The archive already has **P-0489 Cargo Build-Dir Consumer Transition Kit**. That proposal is about **migrating tools off internal layout assumptions**.
- The archive already has **P-0469 Cargo Rebuild Explanation Kit**. That proposal is about **why work recompiled**.

What remains missing is the **tool-only / check-like compile receipt** that answers: “what built, what did not, what assumptions were made, and when should we fall back?”

# Design goals

1. **Honest about guarantees** — never imply tool-only or `check`-like workflows are equivalent to `cargo build`.
2. **Workflow-first** — support IDEs, wrappers, and preflight pipelines rather than trying to stabilize Cargo internals.
3. **Parity-aware** — make fallback decisions explicit and reviewable.
4. **Source-aware** — record sysroot/source and target-dir assumptions when they matter.
5. **Portable** — useful across local editor sessions, CI preflight, and support handoff.

# MVP surface

- Minimal types: `ToolBuildPolicy`, `ToolBuildReceipt`, `CompileSurfaceManifest`, `ParityCheckReport`, `FallbackPlan`, `ComparisonBaselineLock`, `OverrideCommandReceipt`, `SelectionCoverageReport`, `WorkspaceInvocationReceipt`, `ToolBuildDiff`, `ToolBuildBundle`
- Minimal functions:
  - `capture_tool_build_receipt()`
  - `classify_compile_surface()`
  - `capture_override_command_receipt()`
  - `freeze_comparison_baseline()`
  - `capture_selection_coverage()`
  - `capture_workspace_invocation_receipt()`
  - `diagnose_parity_risk()`
  - `suggest_fallback_plan()`
  - `diff_tool_build_receipts()`
- Feature flags:
  - `cargo`
  - `rust-analyzer`
  - `serde`
  - `markdown`

# 0.1 contract

## Promise

For one observed IDE/wrapper/tool-facing run, export one bundle that another person can review without reproducing the machine state live.

## Minimal artifact set

- `tool-build-policy.toml`
- `tool-build.receipt.json`
- `compile-surface.manifest.json`
- `parity-check.report.json`
- `fallback.plan.json`
- `comparison-baseline.lock`
- `override-command.receipt.json`
- `selection-coverage.report.json`
- `workspace-invocation.receipt.json`
- `notes.md`

## Minimal observed facts

- full argv / override-command provenance
- working directory / workspace scope
- target(s) and target-dir/build-dir facts
- sysroot / `sysrootSrc` facts when available
- whether build scripts and proc-macros were enabled
- whether unstable `--compile-time-deps` was in play
- whether `{label}` / `{saved_file}` interpolation changed selection scope
- whether build-script overrides were paired with check overrides or left asymmetric
- whether the effective command path was plain-name, absolute, relative, or wrapper-provided
- whether package scope was workspace-wide, package-only, label-scoped, saved-file-scoped, or ambiguous at startup
- whether `--all-targets` / tests / benches / examples / dev-dependency-bearing lanes were actually covered
- whether multi-workspace invocation ran `per_workspace` or `once`, and with which working-directory rule
- whether the workflow looked closer to editor indexing, editor diagnostics, CI preflight, or manual diagnosis

## First verdict classes

- `acceptable_tool_surface`
- `missing_runtime_surface`
- `target_mismatch`
- `sysroot_source_missing`
- `build_script_cfg_risk`
- `full_build_required`
- `manual_review_required`

# Compatibility story

- Must stay useful even when the actual tool invocation is plain `cargo check`, a rust-analyzer-generated cargo command, `cargo +nightly check --compile-time-deps`, or a wrapper command.
- Must record when a workflow depends on unstable Cargo behavior rather than pretending it is a stable guarantee.
- Must understand target-dir separation and sysroot-source configuration as best-effort facts.
- Must keep `target-dir` and `build-dir` as separate review lanes, because modern Cargo can separate intermediate build artifacts from final artifacts and build-dir layout is still changing.
- Must freeze the comparison baseline when a tool run is contrasted with a workspace build, a package-only build, or policy expectations.
- Must remain honest when target-class coverage changes because `--all-targets`, `check.workspace`, or override-command placeholders changed.
- Must stay usable when rust-analyzer invokes one command per workspace or once per opened project, because both shapes are documented substrate.
- Should remain useful even if rust-analyzer or Cargo changes its default strategy, because the receipt is about observed workflow facts.
- Should be able to compare a tool-only receipt to a fuller build witness without claiming exhaustive semantic equivalence.
- Should be able to import Cargo build-analysis session IDs when available, while remaining useful when no session link exists.

# Conformance & fixtures

- one fixture with rust-analyzer-style separate target dir and acceptable editor-only parity
- one fixture with missing `rust-src` / `sysrootSrc` leading to degraded capability
- one fixture with target mismatch between editor config and terminal build
- one fixture where `{label}`-scoped override commands make the comparison baseline narrower than a workspace build
- one fixture where relative/custom override commands force manual-review receipts
- one fixture where paired build-script override commands preserve a toolchain-specific tool surface
- one fixture where `allTargets = false` leaves a dev-dependency proc-macro unavailable
- one fixture where `check.workspace = false` still leaks broader diagnostics during startup and must remain conservative
- one fixture where linked-project invocation runs `once` and the opened-project root is narrower than per-workspace expectations
- one fixture where a rust-analyzer-specific target dir exists but `build-dir` still remains shared or ambiguous
- one fixture where `-Zbuild-dir-new-layout` compatibility is uncertain and the right answer stays `manual_review_required`
- one fixture where Cargo build-analysis session IDs can be imported as optional supporting evidence
- one fixture where policy requires a full build despite a successful tool-facing run
- goldens for `acceptable_tool_surface`, `sysroot_source_missing`, `target_mismatch`, `build_script_cfg_risk`, `full_build_required`, and `manual_review_required`

# Path to boring stability

- Freeze the parity vocabulary before adding deeper environment inference.
- Keep fallback guidance short and explicit.
- Treat unknown or mixed cases as first-class output.
- Prefer artifact capture and diff over any attempt to drive IDE behavior directly.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one tool-facing compile receipt, classify what was actually built, record target/sysroot/target-dir/override-command assumptions, and emit a fallback recommendation that tells teams when a real `cargo build` is required.

# De-risk plan

1. Start with one narrow workflow: rust-analyzer or a wrapper that mimics it.
2. Keep the parity verdict taxonomy small and conservative.
3. Validate the output against one macro-heavy workspace, one cross-target workspace, and one missing-source case.
4. Avoid claiming language-stability implications beyond what RFC 3477 actually says.

# Non-goals

- Not a replacement for rust-analyzer.
- Not a promise that `cargo check` and `cargo build` are equivalent.
- Not an attempt to stabilize `--compile-time-deps`.
- Not a general Cargo profiler or scheduler.
- Not a lock-contention or cache-layout migration tool.

# Architecture & API sketch

```rust
pub enum WorkflowRole {
    IdeIndex,
    IdeDiagnostics,
    BuildScriptDiscovery,
    CiPreflight,
    ManualDiagnosis,
    Unknown,
}

pub enum ParityClass {
    AcceptableToolSurface,
    MissingRuntimeSurface,
    TargetMismatch,
    SysrootSourceMissing,
    BuildScriptCfgRisk,
    FullBuildRequired,
    ManualReviewRequired,
}

pub fn capture_tool_build_receipt(root: &Path, policy: &ToolBuildPolicy) -> Result<ToolBuildReceipt>;
pub fn classify_compile_surface(receipt: &ToolBuildReceipt) -> CompileSurfaceManifest;
pub fn capture_override_command_receipt(receipt: &ToolBuildReceipt) -> OverrideCommandReceipt;
pub fn freeze_comparison_baseline(receipt: &ToolBuildReceipt) -> ComparisonBaselineLock;
pub fn capture_selection_coverage(receipt: &ToolBuildReceipt) -> SelectionCoverageReport;
pub fn capture_workspace_invocation_receipt(receipt: &ToolBuildReceipt) -> WorkspaceInvocationReceipt;
pub fn diagnose_parity_risk(receipt: &ToolBuildReceipt, manifest: &CompileSurfaceManifest) -> ParityCheckReport;
pub fn suggest_fallback_plan(report: &ParityCheckReport) -> FallbackPlan;
```

Bundle draft: `tool-build-policy.toml`, `tool-build.receipt.json`, `compile-surface.manifest.json`, `parity-check.report.json`, `fallback.plan.json`, `comparison-baseline.lock`, `override-command.receipt.json`, `tool-build.diff.json`, `notes.md`.

# Security / safety model

- Record only the minimum process/environment details needed to explain the compile surface.
- Support redaction for workspace paths and user-specific directories.
- Do not claim a successful tool-only run proves release/build correctness.
- Prefer offline/exportable receipts over live IDE integration complexity in the MVP.

# Maintenance & governance plan

- Track Cargo’s `--compile-time-deps` documentation and behavior changes.
- Track rust-analyzer configuration and any shifts in target-dir/sysroot/override-command expectations.
- Keep the parity/fallback vocabulary stable and modest.
- Maintain fixtures covering separate-target-dir, missing-source, target-mismatch, label-scoped selection drift, override-command provenance, and forced-fallback cases.

# Milestones

## 0.1
- tool-build receipt
- compile-surface manifest
- parity classification
- fallback plan export
- comparison-baseline lock
- override-command receipt
- selection-coverage report
- workspace-invocation receipt

## 0.2
- diff support
- rust-analyzer-specific heuristics
- sysroot-source diagnosis fixtures
- label-scoped selection drift fixtures
- target-class / dev-dependency coverage fixtures

## 0.3
- richer wrapper guidance
- policy presets for IDE versus CI preflight
- comparison against fuller build witnesses

# Open questions

- What is the smallest stable vocabulary that explains tool-facing compile surfaces without overfitting rust-analyzer?
- How should the crate compare a tool receipt with a full build without making unsound equivalence claims?
- How small can `comparison-baseline.lock` stay while still capturing package-selection and target-selection truth?
- Should build-script-generated cfg expectations be first-class in the MVP or only advisory hints?
- How much wrapper-specific command introspection is useful before the crate becomes too environment-specific?
- What is the smallest stable vocabulary for startup leakage, partial workspace coverage, and proc-macro availability holes without overfitting rust-analyzer bugs?

# Sources

- Cargo unstable docs (`compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- RFC 3477 (`cargo check` language policy): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo metadata docs: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo build command docs: https://doc.rust-lang.org/cargo/commands/cargo-build.html
- rust-analyzer issue #18528: https://github.com/rust-lang/rust-analyzer/issues/18528
- rust-analyzer issue #17126: https://github.com/rust-lang/rust-analyzer/issues/17126
