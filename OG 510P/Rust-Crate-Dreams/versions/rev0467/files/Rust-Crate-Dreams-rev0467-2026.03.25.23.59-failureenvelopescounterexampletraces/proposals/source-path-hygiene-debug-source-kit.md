---
id: P-0493
title: Source Path Hygiene & Debug Source Kit — trim-path receipts, virtual-source manifests, and rust-src/rustc-dev diagnosis bundles
status: idea
domains: [debugging, rustc, cargo, toolchains, reproducibility, privacy, support, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/rustc/remap-source-paths.html
  - https://doc.rust-lang.org/rustc/command-line-arguments.html
  - https://rust-lang.github.io/rfcs/3127-trim-paths.html
  - https://rust-lang.github.io/rustup/concepts/components.html
  - https://doc.rust-lang.org/beta/releases.html
---

# Problem

Rust now has meaningful substrate for **sanitizing** and **reconstructing** source paths, but ordinary teams still do not have a boring workflow above it.

The substrate is already richer than it first appears:

- `rustc` supports `--remap-path-prefix` across compiler output, diagnostics, macro expansions, and debug information.
- Cargo’s `trim-paths` work is turning path sanitization into a more explicit profile/release surface.
- The trim-paths RFC documents the special `/rustc/<commit-hash>/...` virtual-path behavior and how it interacts with sysroot sources.
- rustup documents installable `rust-src` and `rustc-dev` components, which influence whether source lookup can resolve std/compiler paths locally.
- Rust release notes keep landing fixes in this area because source-path un-remapping and debugger-source lookup are subtle in practice.

That is progress, but it leaves maintainers with a stubborn support gap.

Ordinary teams still lack a boring answer to questions like:

- which source paths were embedded or sanitized in this build,
- whether the build favors **privacy/reproducibility** or **easy interactive source lookup**,
- which paths now point at virtual `/rustc/<hash>/...` locations,
- whether a downstream debugger session requires `rust-src`, `rustc-dev`, or neither,
- whether path trimming changed only local workspace paths or also sysroot/compiler-source paths,
- and how the source-lookup story drifted between two profiles, toolchains, or releases.

Today the workflow is still improvised:

- inspect build flags and hope `trim-paths` or remaps behaved as intended,
- discover in the debugger that source locations are virtual or missing,
- guess whether installing `rust-src` or `rustc-dev` will fix it,
- and manually compare one build’s path posture against another.

The missing crate is **not** another debugger and **not** a source-distribution service.

The missing crate is a **Source Path Hygiene & Debug Source Kit**: a crate and cargo-adjacent tool that capture path-sanitization policy, virtual-source mapping, and debugger-source availability into a durable **support and reproducibility receipt**.

# What it provides

- `source-hygiene-policy.toml` — declares intended posture per profile/target (`developer_friendly`, `privacy_trimmed`, `release_redacted`, `manual_review_required`), plus which source classes may remain discoverable.
- `remap.manifest.json` — normalized list of remap rules, trim-path posture, scope expectations, and observed source classes (`workspace`, `path_dependency`, `sysroot`, `compiler_source`, `generated`, `manual_review_required`).
- `virtual-source.manifest.json` — records observed virtual path prefixes such as `/rustc/<hash>/...`, what they correspond to, and which local components could satisfy them.
- `source-availability.report.json` — verdicts like `workspace_sources_ok`, `sysroot_sources_missing`, `compiler_sources_missing`, `overtrimmed_for_debugging`, `privacy_goal_met`, `manual_review_required`.
- `debug-source.receipt.json` — one compact artifact describing toolchain, profile, target, path-sanitization posture, and expected source-lookup story.
- `source-hygiene.diff.json` — compares two builds and classifies `workspace_paths_trimmed`, `sysroot_paths_virtualized`, `compiler_paths_now_resolvable`, `privacy_posture_changed`, `debug_support_degraded`, and `manual_review_required`.
- `cargo source-hygiene capture` — inspect one build/artifact set and emit manifests plus a receipt.
- `cargo source-hygiene doctor` — explain what source components or mappings are needed for successful interactive debugging.
- `cargo source-hygiene diff <old> <new>` — compare two builds or profile/toolchain variants.
- `*.sourcehygiene.zip` — portable release/support bundle for CI, support, reproducibility review, or downstream debugger setup.

# What the crate should provide other people

1. **A boring path-hygiene receipt** that explains what source-path posture a build actually shipped.
2. **A debugger-source diagnosis bundle** that says whether `rust-src`, `rustc-dev`, or neither is needed.
3. **A privacy-versus-support contract** instead of vague “we turned on trim-paths” claims.
4. **A diff artifact** for catching accidental loss of source lookup between releases.
5. **A bridge** between remap/trim-path substrate and real-world support/debugging workflows.

# Persona / who it’s for

- maintainers shipping binaries or SDKs who care about both privacy and supportability
- release engineers controlling `trim-paths` and remap policies
- support/debug engineers diagnosing “debugger can’t find sources” problems
- toolchain and reproducibility engineers reviewing path hygiene
- teams using build-std, `rust-src`, or compiler-linked tooling that need clear source lookup expectations

# Users & user stories

- **Release engineer**: “Show me whether this build still lets downstream users step into std or whether we intentionally redacted that path story.”
- **Support engineer**: “Tell me whether the fix is ‘install `rust-src`’, ‘install `rustc-dev`’, or ‘this build intentionally trimmed too much for source lookup’.”
- **Maintainer**: “Diff our debug profile and release profile and show how source visibility changed.”
- **Reproducibility reviewer**: “Prove that local absolute paths were sanitized without guessing from binary strings.”

# Prior art (and why it’s insufficient)

- `rustc` already documents `--remap-path-prefix`.
- Cargo/trim-paths work already provides a simpler source-path sanitization model.
- rustup already documents `rust-src` and `rustc-dev` components.
- Release notes already show that correct un-remapping of compiler sources is subtle enough to need ongoing fixes.
- The archive already has **P-0486 Debuggability Support Contract Kit**, which is about the broader debuginfo/symbol/visualizer posture.
- The archive already has **P-0430 Build-Std Workbench Kit**, which is about sysroot rebuild recipes and evidence.

What remains missing is the narrower **source-path hygiene and lookup artifact** that tells another human what paths were trimmed, what became virtual, what local source components can satisfy those paths, and how that changed.

# Design goals

1. **Path-hygiene-first** — make remapping and sanitization visible as first-class release/support facts.
2. **Source-class-aware** — workspace, path-dependency, sysroot, and compiler-source paths must remain distinct.
3. **Privacy-versus-debugging-honest** — do not pretend one setting optimizes both perfectly.
4. **Virtual-path-aware** — `/rustc/<hash>/...` and similar source resolution cases must be explicit.
5. **Diffable** — support regressions caused by path hygiene should be reviewable in CI and release review.

# MVP surface

- Minimal types: `SourceHygienePolicy`, `RemapManifest`, `VirtualSourceManifest`, `SourceAvailabilityReport`, `DebugSourceReceipt`, `SourceHygieneDiff`, `SourceHygieneBundle`
- Minimal functions:
  - `capture_remap_manifest()`
  - `capture_virtual_source_manifest()`
  - `classify_source_availability()`
  - `diff_source_hygiene_receipts()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `zip`
  - `markdown`
  - `rustup-components`
  - `debug-support`

# Compatibility story

- Must work whether the build used explicit remap flags, `trim-paths`, both, or neither.
- Must distinguish path sanitization of local workspace paths from virtualization of sysroot/compiler-source paths.
- Must remain useful even if the consumer machine differs from the build machine.
- Should stay compatible with future stabilization or expansion of trim-paths-related Cargo surfaces.
- Should avoid assuming every debugger family consumes source paths identically; focus first on source-availability facts rather than launcher-specific behavior.

# Conformance & fixtures

- one developer-friendly fixture with no remap/trim and easy workspace/source lookup.
- one release fixture with `trim-paths`/remap enabled and workspace paths redacted.
- one fixture where std sources resolve with `rust-src` installed.
- one fixture where compiler-source lookup requires `rustc-dev` and fails without it.
- one diff fixture showing privacy gain but debugger-source regression.

# Path to boring stability

- Freeze the source-class and verdict vocabulary before broad debugger integration.
- Start with observation/capture and diagnosis, not source download/orchestration.
- Prefer conservative verdicts when source lookup is ambiguous.
- Keep the first artifact format intentionally small and support-oriented.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A cargo subcommand that inspects one build or artifact set, emits a remap/virtual-source manifest, and tells a maintainer whether downstream source lookup is preserved, requires extra components, or has been intentionally trimmed away.

# De-risk plan

1. Start with static capture of remap rules and source-availability classification.
2. Limit early verdicts to a few source classes and component hints.
3. Pilot on one developer profile and one release-trimmed profile before widening platform scope.
4. Keep debugger-launcher specifics out of the first version.

# Non-goals

- Not a full debugger launcher or symbolication system.
- Not a source-code mirror or package manager.
- Not a replacement for rustup.
- Not a promise that all privacy/reproducibility goals can coexist with every debugging workflow.

# Architecture & API sketch

```rust
pub enum SourceClass {
    Workspace,
    PathDependency,
    Sysroot,
    CompilerSource,
}

pub fn capture_virtual_source_manifest(cx: &Context) -> Result<VirtualSourceManifest>;
pub fn classify_source_availability(manifest: &VirtualSourceManifest) -> SourceAvailabilityReport;
pub fn diff_source_hygiene_receipts(a: &DebugSourceReceipt, b: &DebugSourceReceipt) -> SourceHygieneDiff;
```

# Why now / why this is newly possible

Rust crossed the threshold where path hygiene is no longer a hidden compiler trick. Remap-paths are documented, trim-paths is becoming more explicit, and rustup components already shape what source lookup can succeed.

That makes the next missing layer a small, honest support artifact — not another low-level mechanism.
