---
id: P-0506
title: Cargo Workspace Boundary Doctor Kit — ancestor-discovery receipts, config-layering reports, and invocation-mode bundles
status: idea
domains: [cargo, workspace, config, devtools, ci, editors]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/workspaces.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#script
  - https://github.com/rust-lang/cargo/issues/12738
  - https://github.com/rust-lang/cargo/issues/15320
  - https://github.com/rust-lang/cargo/issues/16562
  - https://github.com/rust-lang/cargo/issues/16563
  - https://github.com/rust-lang/cargo/issues/8643
---

# Problem

Cargo’s workspace and config discovery behavior is powerful, but a surprising amount of real pain lives at its **boundaries**:

- a parent `Cargo.toml` or `.cargo/config.toml` can poison a subproject unexpectedly,
- `--manifest-path` can make the current working directory’s config matter more than the target project’s config,
- include chains and config-relative paths can make the effective config differ from what a user sees in one file,
- auto-membership and workspace discovery can make a package “believe it is in a workspace” when that is not what the maintainer wanted,
- and single-file package / manifest-command lanes change discovery posture in ways that ordinary users rarely model explicitly.

Cargo’s February 2026 development update makes workspace/config discovery an explicit design topic instead of folklore.
The Cargo Book now also documents hierarchical probing, include merging, config-relative path rules, environment / CLI precedence, and single-file package discovery differences.
Those are good substrate docs, but they still do not hand maintainers or tool authors one small artifact answering:

- which ancestors were candidates,
- which boundary or stop condition was observed,
- which config files, includes, env variables, and CLI overrides materially affected the run,
- which path basis each config route used,
- whether the invocation used cwd auto-discovery, `--manifest-path`, manifest-command mode, or a single-file package lane,
- and what the least invasive next action is.

The missing crate is not “replace Cargo discovery.”
It is a **boundary diagnosis and receipt kit** for Cargo workspace and config surprises.

# Why this moved now

The current signals line up unusually well:

1. Cargo’s 1.94 update calls out **workspace and configuration discovery** as an active design topic, including accidental parent manifests, home-directory surprises, and possible `package.workspace = false` style escape hatches.
2. Cargo’s config docs make hierarchical probing, include merging, config-relative path rules, and environment / CLI precedence explicit enough that a diagnosis crate can be honest instead of relying on rumor.
3. Cargo’s single-file package docs now make it explicit that `.rs` packages cannot be auto-discovered like `Cargo.toml` manifests and that manifest-command mode shifts config-root expectations.
4. The project-specific-config tracking issue confirms that some settings are really package concerns, but the migration from config to manifest is incomplete and not one-to-one.

So the missing value is no longer “some docs page.”
It is the **portable context / discovery / layering / invocation / diagnosis bundle** another maintainer can inspect.

# Main judgment

A worthy crate in this lane should let another person answer all of these cleanly:

1. **Which ancestor manifests and config files were candidates, and where did probing stop?**
2. **Which workspace root Cargo appeared to select, and why was that root even eligible?**
3. **Which config layers mattered, in what precedence order, and which path basis did each one use?**
4. **Which invocation mode was used, and did that mode permit workspace auto-discovery at all?**
5. **Which diagnosis family applies: parent poisoning, config-layer mismatch, cwd/subject split, single-file posture, or manual review?**
6. **What is the smallest honest workaround or next step?**

If a candidate crate cannot answer those questions, it is still mostly docs, editor glue, or incident folklore.

# What it provides

- `boundary-context.toml` — declares the intended invocation root, selected manifest, expected workspace behavior, and whether local config should matter.
- `discovery-trace.receipt.json` — records probed parents, candidate manifests/config files, current working directory, manifest path, and observed winner(s).
- `workspace-membership.report.json` — classifies whether the package was a root package, virtual-workspace member, auto-member, excluded package, or ambiguous case.
- `config-probe.report.json` — records which config files and environment/config overrides materially affected the run.
- `ancestor-discovery.receipt.json` — receiver-facing receipt for ancestor candidates, stop conditions, workspace-boundary basis, and whether auto-discovery was enabled or intentionally absent.
- `config-layering.report.json` — receiver-facing report for file layers, include edges, env/CLI override routes, precedence, and config-relative path basis.
- `invocation-mode.report.json` — distinguishes cwd auto-discovery, `--manifest-path`, manifest-command mode, single-file package lanes, and whether workspace auto-discovery was disabled.
- `boundary-diagnosis.report.json` — emits verdicts such as `parent_manifest_poisoning`, `cwd_config_split`, `config_include_layer_surprise`, `manifest_command_root_shift`, `single_file_workspace_autodiscovery_disabled`, `package_workspace_optout_candidate`, and `manual_review_required`.
- `boundary-diff.report.json` — compares two runs and classifies whether the boundary moved because of cwd, manifest path, parent files, config layering, or invocation mode.
- `boundary-support-bundle.manifest.json` — top-level manifest tying context, discovery, layering, invocation, membership, and diagnosis artifacts together.
- `invocation-advice.md` — the shortest honest guidance: add empty `[workspace]`, move/rename the parent manifest, run from project root, split config, remove a surprising include, or wait for upstream support.
- `cargo boundary-doctor capture` — emit one bundle for the current invocation.
- `cargo boundary-doctor doctor` — print the shortest diagnosis for the current surprise.
- `cargo boundary-doctor diff <old> <new>` — compare two invocation shapes.
- `*.boundarybundle.zip` — portable artifact for CI failures, editor integrations, and “Cargo is seeing the wrong project” bug reports.

# What the crate should provide other people

1. **A reproducible boundary bug bundle** instead of screenshots and shell-history archaeology.
2. **A shared vocabulary** for workspace/config discovery failures.
3. **A tool-author-friendly schema** for editors, wrappers, and CI launchers that need to explain why Cargo saw a different project than the user expected.
4. **An ancestor-discovery answer** that separates observed candidates from inferred influence.
5. **A config-layering answer** that keeps file layers, include chains, env overrides, and CLI overrides visibly distinct.
6. **An invocation-mode answer** so users stop treating cwd auto-discovery, `--manifest-path`, manifest commands, and single-file package lanes as the same route.
7. **A conservative advice layer** that distinguishes fix-now workarounds from upstream design gaps.
8. **A review artifact** when a repo intentionally changes workspace boundaries or config layering.

# Persona / who it’s for

- maintainers of nested repos and monorepos
- editor / IDE / wrapper authors invoking Cargo on behalf of users
- CI engineers using `--manifest-path`, manifest commands, or non-root working directories
- contributors confused by accidental workspace membership or parent config bleed

# Users & user stories

- **Maintainer**: “Explain why a crate under this directory suddenly thinks it belongs to a parent workspace.”
- **Tool author**: “I run Cargo with `--manifest-path`; tell me whether cwd config changed the outcome.”
- **CI engineer**: “Capture one artifact that proves whether the job used repo config or runner-local config.”
- **Reviewer**: “Show me whether this refactor changed workspace boundaries or only moved files around.”
- **Script author**: “Tell me whether this `.rs` single-file invocation even had workspace auto-discovery available.”
- **New contributor**: “Give me the shortest possible explanation instead of a scary Cargo error.”

# Prior art (and why it’s insufficient)

- Cargo’s docs explain config and workspace rules, but they are not a support-grade receipt.
- Existing issues and design threads document specific surprises, but not a reusable diagnostic artifact.
- `--manifest-path`, manifest-command mode, and local config workarounds exist, but without a bundle they are hard to review and compare.
- The project-specific-config work is important, but it does not solve today’s “why did Cargo discover *that*?” incident by itself.

What remains missing is the **boundary context + ancestor discovery + config layering + invocation mode + diagnosis + advice** layer.

# Design goals

1. **Boundary-explicit** — always separate workspace membership, ancestor discovery, config layering, invocation mode, and caller-intent mismatch.
2. **Observed-facts first** — preserve what Cargo could see without overclaiming the final internal decision process.
3. **Invocation-aware** — current working directory, `--manifest-path`, manifest commands, and single-file package posture belong in the artifact.
4. **Precedence-visible** — file layers, include edges, env overrides, and CLI overrides must stay reviewable.
5. **Diff-friendly** — boundary changes must be reviewable across two invocations or revisions.
6. **Low-intrusion** — diagnosis and receipts first; mutation or automatic fixing later, if ever.

# MVP surface

- Minimal types: `BoundaryContext`, `DiscoveryTraceReceipt`, `WorkspaceMembershipReport`, `ConfigProbeReport`, `AncestorDiscoveryReceipt`, `ConfigLayeringReport`, `InvocationModeReport`, `BoundaryDiagnosisReport`, `BoundaryDiff`, `BoundarySupportBundleManifest`
- Minimal functions:
  - `capture_context()`
  - `trace_discovery()`
  - `capture_ancestor_discovery()`
  - `classify_membership()`
  - `classify_config_probe()`
  - `capture_config_layering()`
  - `capture_invocation_mode()`
  - `diagnose_boundary()`
  - `diff_boundaries()`
- Feature flags:
  - `serde`
  - `env-snapshot`
  - `ci`
  - `editor`
  - `path-redaction`

# Compatibility story

- Works with current Cargo workspace/config rules instead of trying to replace them.
- Records current-working-directory, manifest-path, manifest-command, include layering, and path-basis effects explicitly.
- Can stay useful even if Cargo later grows `package.workspace = false`, project-config-in-manifest support, or isolated-invocation flags.
- Must remain honest when a case is only partially observable from stable surfaces.

# Conformance & fixtures

- one `parent_home_manifest_poisoning` fixture showing accidental parent discovery
- one `manifest_path_local_config_split` fixture showing cwd config overriding the target project’s expectations
- one `parent_config_include_chain_and_cli_override_need_distinct_layer_receipts` fixture showing include/override precedence and path-basis separation
- one `manifest_command_and_manifest_path_have_different_config_roots` fixture showing invocation-mode drift
- one `single_file_package_disables_workspace_autodiscovery_but_not_config_discovery` fixture showing single-file posture
- one `portable_bundle_keeps_ancestor_layering_and_invocation_mode_separate` fixture showing the receiver-facing bundle shape
- goldens for `parent_manifest_poisoning`, `cwd_config_split`, `config_include_layer_surprise`, `manifest_command_root_shift`, and `single_file_workspace_autodiscovery_disabled`

# Path to boring stability

- Freeze the diagnosis vocabulary early.
- Keep the crate read-mostly and advice-oriented.
- Record path redaction posture explicitly.
- Prefer one portable bundle over a large interactive UI.
- Keep the invocation-mode vocabulary small and stable enough for editors and CI wrappers to reuse.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 5/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that capture the invocation context, trace the relevant parent manifests and config files, explain config layering and invocation mode, classify the workspace/config boundary problem, and emit one small advice bundle another maintainer can review.

# De-risk plan

1. Start with capture and diagnosis, not automatic repair.
2. Keep the first version focused on a handful of concrete failure families.
3. Treat upstream design gaps as explicit findings instead of burying them in generic errors.
4. Validate against editor/CI/script invocation shapes early.

# Non-goals

- Not a replacement for Cargo’s workspace discovery.
- Not a general config unification mechanism.
- Not a promise to emulate Cargo’s internal parser perfectly.
- Not an always-on daemon watching the filesystem.
- Not a silent fixer that rewrites manifests or config includes automatically.

# Architecture & API sketch

```rust
pub struct AncestorDiscoveryReceipt {
    pub cwd: std::path::PathBuf,
    pub subject_manifest: std::path::PathBuf,
    pub invocation_mode: InvocationMode,
    pub candidates: Vec<AncestorCandidate>,
    pub workspace_boundary_basis: Option<WorkspaceBoundaryBasis>,
}

pub fn capture_context(request: &CaptureRequest) -> Result<BoundaryContext>;
pub fn trace_discovery(context: &BoundaryContext) -> Result<DiscoveryTraceReceipt>;
pub fn capture_ancestor_discovery(context: &BoundaryContext) -> Result<AncestorDiscoveryReceipt>;
pub fn capture_config_layering(context: &BoundaryContext) -> Result<ConfigLayeringReport>;
pub fn capture_invocation_mode(context: &BoundaryContext) -> Result<InvocationModeReport>;
pub fn diagnose_boundary(bundle: &BoundaryBundle) -> Result<BoundaryDiagnosisReport>;
pub fn diff_boundaries(old: &BoundaryBundle, new: &BoundaryBundle) -> Result<BoundaryDiff>;
```

Bundle draft: `boundary-context.toml`, `discovery-trace.receipt.json`, `workspace-membership.report.json`, `config-probe.report.json`, `ancestor-discovery.receipt.json`, `config-layering.report.json`, `invocation-mode.report.json`, `boundary-diagnosis.report.json`, `boundary-diff.report.json`, `boundary-support-bundle.manifest.json`, `invocation-advice.md`.

# Security / safety model

- Support path redaction for private home-directory and CI runner paths.
- Distinguish observed files from inferred influence.
- Treat environment snapshots as sensitive and opt-in where appropriate.
- Avoid mutating manifests or config files automatically.
- Preserve exactness classes so suspected influence is not mislabeled as proven precedence.

# Maintenance & governance plan

- Keep schemas small and versioned.
- Track upstream discovery/config design issues explicitly.
- Maintain a compact fixture pack for common surprise families.
- Prefer stable docs/issues as evidence instead of folklore.
- Add new diagnosis families only when the archive can name a distinct review object they need.

# Milestones

## 0.1
- context capture
- discovery trace receipt
- first diagnosis report
- portable boundary bundle

## 0.2
- ancestor-discovery receipt
- config-layering report
- invocation-mode report
- editor / CI invocation presets

## 1.0
- stable schemas
- richer path-basis / include-edge reporting
- stronger advice generation
- documented compatibility table for newer Cargo boundary features

# Open questions

- How much of Cargo’s internal discovery sequence can be exposed conservatively on stable inputs alone?
- Should env snapshots be part of the default bundle, or only on explicit request?
- What is the smallest advice taxonomy that still helps maintainers act?
- Which invocation-mode labels will stay stable enough across future Cargo design changes?

# Sources

- Cargo 1.94 development cycle: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo configuration docs: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace docs: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo unstable single-file package docs: https://doc.rust-lang.org/cargo/reference/unstable.html#script
- Project-specific config tracking: https://github.com/rust-lang/cargo/issues/12738
- Workspace discovery failure example: https://github.com/rust-lang/cargo/issues/15320
- `cargo init` home-directory confusion: https://github.com/rust-lang/cargo/issues/16562
- workspace opt-out discussion: https://github.com/rust-lang/cargo/issues/16563
- ignore-local-config request: https://github.com/rust-lang/cargo/issues/8643
