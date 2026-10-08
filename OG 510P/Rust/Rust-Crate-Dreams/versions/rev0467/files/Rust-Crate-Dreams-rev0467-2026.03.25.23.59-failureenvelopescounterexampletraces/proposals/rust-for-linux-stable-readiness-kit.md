---
id: P-0444
title: Rust-for-Linux Stable Readiness Kit — kernel toolchain profiles, rustavailable receipts, and subsystem-ready evidence bundles for stable-Rust adoption
status: idea
domains: [linux, kernel, compiler, tooling, build, no_std, ci, safety]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-compiler.html
  - https://docs.kernel.org/rust/quick-start.html
  - https://rust-for-linux.com/rust-version-policy
  - https://rust-for-linux.com/unstable-features
---

# Problem

Rust-for-Linux is no longer just “someday.” The Rust project has spent multiple goal periods pushing Linux toward building on stable Rust, and the 2025H2 goals split the remaining work into language and compiler/tooling tracks.

But the day-to-day maintainer problem is still messy:

- kernel and distro builders need to know which toolchain/profile assumptions are actually in force,
- subsystem teams need a compact answer to “are we ready for stable Rust here yet?”
- unstable feature usage, version policy, quick-start requirements, `rustavailable`, Kconfig state, and CI results all live in different places,
- and many review conversations still rely on folklore instead of a portable readiness artifact.

The missing crate is not a kernel build system replacement.

The missing crate is a **stable-readiness kit** that turns scattered kernel/Rust constraints into a reviewable profile and evidence bundle.

# What it provides

- `kernel-rust-profile.toml` — pins kernel tree assumptions, rustc/LLVM expectations, required components, unstable-feature policy, and subsystem-specific rules.
- `rustavailable.receipt.json` — captures toolchain-detection output and normalized blocker categories.
- `kernel-rust-readiness.json` — records readiness claims by subsystem, target, and policy profile.
- `feature-waiver.toml` — explicit waivers for still-unstable or non-portable edges.
- `rfl-ready check` — gathers local environment, policy, and kernel-state information.
- `rfl-ready explain` — tells humans why a profile is or is not “stable-ready”.
- `rfl-ready bundle` — emits `*.rflbundle.zip` for CI, distro review, or upstream discussion.
- adapters for Kconfig snippets, `make rustavailable`, and selected kernel docs outputs.

# What the crate should provide other people

1. **A shared readiness language** for Rust-for-Linux adoption conversations.
2. **A compact profile** that separates hard blockers from local policy choices.
3. **A reviewable bundle** for distro builders, subsystem maintainers, and CI.
4. **A bridge** between Rust project goals and the day-to-day kernel workflow.
5. **An honest artifact** that records waivers and caveats instead of pretending everything is stable already.

# Persona / who it’s for

- kernel subsystem maintainers
- distro / platform engineers building kernels
- Rust-for-Linux contributors tracking stabilization progress
- CI maintainers validating toolchain readiness over time

# Users & user stories

- **Kernel maintainer**: “Explain why this subsystem still needs unstable features or special toolchain assumptions.”
- **Distro builder**: “Produce one artifact showing whether our packaging environment satisfies Rust-for-Linux requirements.”
- **Contributor**: “Attach a stable-readiness bundle to a discussion about moving a feature out of experimental use.”
- **CI engineer**: “Track readiness drift across toolchain updates and kernel branches.”

# Prior art (and why it’s insufficient)

- Rust project goals document the remaining language/compiler/tooling work.
- Kernel quick-start docs explain how to get started and mention `rustavailable`.
- Rust-for-Linux publishes version-policy and unstable-feature guidance.

What remains missing is a **portable readiness receipt** that combines those threads for ordinary maintainers.

# Design goals

1. **Profile before policy magic** — record assumptions explicitly.
2. **Kernel-native** — meet maintainers where they already work (`make`, Kconfig, docs, CI).
3. **Waiver-aware** — unstable edges should be recorded, not hidden.
4. **Conservative** — never present “stable-ready” as a stronger claim than the evidence supports.
5. **Long-horizon useful** — remain helpful even while upstream stabilization work continues.

# MVP surface

- Minimal types: `KernelRustProfile`, `ReadinessCheck`, `ReadinessStatus`, `Waiver`, `RustavailableReceipt`, `RflBundle`
- Minimal functions:
  - `collect_environment()`
  - `capture_rustavailable()`
  - `evaluate_readiness()`
  - `explain_blockers()`
  - `write_bundle()`
- Feature flags:
  - `serde`
  - `kconfig`
  - `docs`
  - `ci`

# Compatibility story

- Works alongside existing kernel build flows; it does not replace them.
- Can operate on stable toolchains while still recording unstable-feature dependencies.
- Treats official kernel docs and local command outputs as inputs, not assumptions.
- Supports policy profiles for distro packaging, subsystem experimentation, and upstream tracking.

# Conformance & fixtures

- Fixture profiles for “stable-ready”, “needs unstable flags”, “missing component”, and “version-policy mismatch” cases.
- Goldens for normalized blocker categories from `rustavailable` output.
- Example subsystem profiles with waivers.
- CI drift fixtures showing readiness changes across toolchain updates.

# Path to boring stability

- Stabilize blocker categories and receipt schema first.
- Keep the first profiles intentionally small and explicit.
- Treat policy overlays as data, not hard-coded logic.
- Add more kernel-surface adapters only after the core readiness bundle proves useful.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and CLI that capture `rustavailable`, compare the result against a declared kernel/Rust profile, and emit a readiness receipt plus an explainable bundle of blockers and waivers.

# De-risk plan

1. Start with environment capture and normalized blocker categories.
2. Keep subsystem-level readiness as explicit profile data, not inference.
3. Validate on one or two kernel workflows first (local dev and distro-like packaging).
4. Add richer Kconfig / CI integration only after the receipt format is trusted.

# Non-goals

- Not a replacement for kernel `make` logic.
- Not a promise that Linux is fully stable-Rust-ready today.
- Not a general Linux package manager or toolchain installer.
- Not a substitute for upstream stabilization work.

# Architecture & API sketch

```rust
pub struct ReadinessReport {
    pub status: ReadinessStatus,
    pub blockers: Vec<Blocker>,
    pub waivers: Vec<Waiver>,
    pub toolchain: ToolchainFingerprint,
}

pub fn capture_rustavailable(tree: &Path) -> Result<RustavailableReceipt>;
pub fn evaluate_readiness(profile: &KernelRustProfile, inputs: &CollectedInputs) -> ReadinessReport;
pub fn explain_blockers(report: &ReadinessReport) -> Vec<String>;
pub fn write_bundle(bundle: &RflBundle, out: &Path) -> Result<()>;
```

Bundle draft: `kernel-rust-profile.toml`, `rustavailable.receipt.json`, `kernel-rust-readiness.json`, `feature-waiver.toml`, `notes.md`.

# Security / safety model

- Make all unstable-feature dependencies explicit.
- Support redaction of local paths and private CI details.
- Never silently convert waivers into “ready”.
- Keep command capture deterministic and clearly versioned.

# Maintenance & governance plan

- Track Rust-for-Linux language/compiler goal progress and version-policy changes.
- Maintain a compact blocker taxonomy aligned with kernel docs and real workflows.
- Keep subsystem profiles data-driven and community-reviewable.
- Publish example profiles for distro, subsystem, and experimentation scenarios.

# Milestones

## 0.1
- profile schema
- `rustavailable` receipt
- readiness explanation

## 0.2
- waiver support
- bundle export
- CI drift reporting

## 1.0
- stable receipt schema
- subsystem profile library
- report adapters

# Open questions

- What is the smallest blocker taxonomy that still helps real maintainers?
- Which parts of readiness are objective versus local policy?
- How should readiness reports encode “good enough for this subsystem but not globally stable-ready”?

# Sources

- Stabilize tooling needed by Rust for Linux: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Rust-for-Linux stable: language features: https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html
- Rust-for-Linux stable: compiler features: https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-compiler.html
- Kernel Rust quick start: https://docs.kernel.org/rust/quick-start.html
- Rust-for-Linux version policy: https://rust-for-linux.com/rust-version-policy
- Rust-for-Linux unstable features: https://rust-for-linux.com/unstable-features
