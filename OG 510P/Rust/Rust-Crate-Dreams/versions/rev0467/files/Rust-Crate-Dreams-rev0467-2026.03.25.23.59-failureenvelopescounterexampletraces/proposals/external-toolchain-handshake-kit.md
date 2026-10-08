---
id: P-0457
title: External Toolchain Handshake Kit — dep-info normalization, injected-attribute receipts, and source-pure no_std manifests for non-Cargo orchestrators
status: idea
domains: [cargo, compiler, no_std, build-systems, tooling, integration, rustdoc]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#binary-dep-depinfo
  - https://doc.rust-lang.org/beta/unstable-book/compiler-flags/crate-attr.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html#rustdoc-depinfo
---

# Problem

The Rust toolchain already exposes several pieces that external orchestrators badly need:

- dep-info files for rebuild detection,
- `-Z binary-dep-depinfo` for tracking binary dependencies such as the standard library,
- `-Z crate-attr` for injecting crate-root attributes without editing source,
- and `-Z rustdoc-depinfo` for documentation rebuild detection.

The Rust-for-Linux tooling goal makes this even more explicit: Rust needs a way to extract dependency info and configure `no_std` externally, because some major consumers do not want source files cluttered with orchestrator-specific attributes.

But today the workflow is still scattered:

- dep-info and binary-dep-info are separate and awkward to normalize,
- injected attributes are powerful but easy to lose track of in review,
- rustdoc dep-info is yet another surface,
- and external build systems still lack one compact, boring **handshake artifact** saying “here is what Rust expects, what we injected, and what files actually matter for rebuilds.”

The missing crate is not a replacement for Cargo or Bazel or Kbuild.

The missing crate is a **handshake kit** that defines a reviewable contract between Rust’s toolchain surfaces and external orchestrators.

# What it provides

- `handshake-profile.toml` — pins targets, injected attributes, dep-info policy, path-base rules, and doc-build policy.
- `rust.handshake.json` — normalized manifest of compile units, dep-info sources, binary dependency tracking, and rustdoc dependency behavior.
- `injected-attrs.receipt.json` — exact `-Z crate-attr` injections, where they applied, and why.
- `rebuild-surface.json` — consolidated rebuild inputs across rustc dep-info, binary dep-info, and optional rustdoc dep-info.
- `source-purity.report.json` — records which source assumptions were moved out of source files and into external profiles.
- `cargo external-handshake snapshot` — collect the current toolchain-facing handshake for one workspace.
- `cargo external-handshake diff` — compare handshake artifacts across toolchains or build policies.
- `cargo external-handshake doctor` — surface suspicious path-style, missing binary-dep tracking, or undocumented injected-attribute usage.
- `*.handshakebundle.zip` — shareable artifact for external build-system maintainers, CI, or upstream issue filing.

# What the crate should provide other people

1. **A boring contract artifact** between Rust and external build systems.
2. **A receipt for injected attributes** so source-pure workflows remain reviewable.
3. **A normalized rebuild-surface manifest** that includes binary dependencies when relevant.
4. **A way to keep `no_std` and similar orchestration assumptions out of source files without making them invisible.**
5. **A bridge** between compiler/Cargo/rustdoc metadata and non-Cargo orchestrators.

# Persona / who it’s for

- Rust-for-Linux and kernel build maintainers
- Bazel/Buck/Kbuild/Ninja/Make integrators
- embedded and `no_std` platform teams
- distro/toolchain packagers
- docs build engineers with custom orchestration

# Users & user stories

- **Kernel integrator**: “Record the `no_std`-style injected attributes and binary dependency tracking we needed without patching source files.”
- **External build-system author**: “Ingest one normalized manifest instead of reverse-engineering multiple tool outputs.”
- **Docs build engineer**: “See whether our documentation rebuild logic is using rustdoc dep-info or a weaker fallback.”
- **Auditor / reviewer**: “Review every injected crate attribute and rebuild surface in one bundle.”

# Prior art (and why it’s insufficient)

- Cargo dep-info files are intended for external build systems.
- `-Z binary-dep-depinfo` solves a real rebuild-tracking hole.
- `-Z crate-attr` allows attribute injection at the crate root.
- `-Z rustdoc-depinfo` improves documentation rebuild detection.

What remains missing is a **single handshake artifact** that combines these surfaces into a stable-on-top integration story.

# Design goals

1. **Handshake-first** — external tools should consume one reviewable manifest, not chase many ad hoc files.
2. **Source-purity-explicit** — moved-out-of-source assumptions must still be visible.
3. **Rebuild-surface-aware** — binary and documentation dependencies should not disappear.
4. **Path-conscious** — normalize path-base and absolute/relative-path behavior clearly.
5. **Conservative** — unknown or unsupported rebuild edges must remain visible.

# MVP surface

- Minimal types: `HandshakeProfile`, `InjectedAttrReceipt`, `RebuildSurface`, `HandshakeSnapshot`, `HandshakeDiff`, `DoctorFinding`
- Minimal functions:
  - `collect_handshake()`
  - `normalize_dep_info()`
  - `record_injected_attrs()`
  - `diff_handshakes()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `rustdoc`
  - `binary-dep-depinfo`
  - `crate-attr`

# Compatibility story

- Works with current unstable surfaces by recording them explicitly, not hiding them.
- Should remain useful after stabilization because the artifact value is the normalization and review layer.
- Must stay distinct from generic build-input manifests by focusing on **external orchestration contract surfaces**.
- Can degrade to rustc/Cargo dep-info only when richer signals are unavailable.

# Conformance & fixtures

- Fixtures for one source-pure `no_std` workspace, one binary-dep-tracked build, one rustdoc-depinfo-aware docs build, and one path-normalization case.
- Goldens for “binary deps missing”, “injected attrs undocumented”, “docs rebuild surface missing”, and “normalized handshake clean”.
- Example bundles for a kernel-like external build and a simpler embedded build.
- A small doctor corpus for path and dep-info footguns.

# Path to boring stability

- Stabilize the snapshot schema before adding many orchestrator adapters.
- Start with observation and reporting, not build-system mutation.
- Keep injected attributes and path rewrites impossible to hide.
- Add richer external-tool exports only after the core schema is trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that collect dep-info, binary-dep tracking, injected crate attributes, and optional rustdoc dep-info into one normalized handshake bundle for review by an external orchestrator.

# De-risk plan

1. Start with snapshot/diff/doctor workflows, not deep build-system plugins.
2. Focus first on one motivating case: source-pure `no_std` plus binary dependency tracking.
3. Normalize only a few path styles and make unknowns explicit.
4. Validate on one external-orchestrator integration before widening scope.

# Non-goals

- Not a new build system.
- Not a replacement for Cargo.
- Not a universal manifest for every possible external tool.
- Not a hidden mechanism for mutating source or compiler behavior without receipts.

# Architecture & API sketch

```rust
pub struct InjectedAttrReceipt {
    pub target: String,
    pub attrs: Vec<String>,
    pub reason: String,
}

pub fn collect_handshake(profile: &HandshakeProfile, root: &Path) -> Result<HandshakeSnapshot>;
pub fn normalize_dep_info(snapshot: &HandshakeSnapshot) -> Result<RebuildSurface>;
pub fn diff_handshakes(old: &HandshakeSnapshot, new: &HandshakeSnapshot) -> HandshakeDiff;
pub fn write_bundle(bundle: &HandshakeBundle, out: &Path) -> Result<()>;
```

Bundle draft: `handshake-profile.toml`, `rust.handshake.json`, `injected-attrs.receipt.json`, `rebuild-surface.json`, `source-purity.report.json`, `notes.md`.

# Security / safety model

- Record every injected attribute and its rationale.
- Support redaction of proprietary paths and target names.
- Preserve exact toolchain versions and feature-gate assumptions.
- Never claim the rebuild surface is complete when signals were missing.

# Maintenance & governance plan

- Track stabilization or redesign of dep-info and injected-attribute surfaces closely.
- Keep the core schema orchestrator-neutral.
- Maintain fixtures for external-build-system use cases rather than Cargo-only flows.
- Publish guidance on what “source-pure” means and does not mean.

# Milestones

## 0.1
- snapshot schema
- dep-info normalization
- injected-attribute receipts

## 0.2
- rustdoc dep-info support
- doctor mode
- bundle export

## 1.0
- stable handshake schema
- external-tool adapters
- public fixture corpus

# Open questions

- What is the smallest useful handshake schema for external orchestrators?
- How should rustdoc rebuild surfaces and compile rebuild surfaces relate in one bundle?
- Which path-normalization policies are worth standardizing first?

# Sources

- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Cargo build-cache dep-info docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo unstable `binary-dep-depinfo`: https://doc.rust-lang.org/cargo/reference/unstable.html#binary-dep-depinfo
- Unstable `crate-attr`: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/crate-attr.html
- Cargo unstable `rustdoc-depinfo`: https://doc.rust-lang.org/cargo/reference/unstable.html#rustdoc-depinfo
