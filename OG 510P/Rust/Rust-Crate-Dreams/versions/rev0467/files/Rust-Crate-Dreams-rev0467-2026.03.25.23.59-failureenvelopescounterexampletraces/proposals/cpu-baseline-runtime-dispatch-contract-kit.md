---
id: P-0497
title: CPU Baseline & Runtime Dispatch Contract Kit — target-cpu receipts, feature-gate support promises, and illegal-instruction risk bundles
status: idea
domains: [compiler, performance, release, portability, cargo, ffi, runtime]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu
  - https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature
  - https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature
  - https://doc.rust-lang.org/std/macro.is_x86_feature_detected.html
---

# Problem

Rust already has real substrate for **CPU-feature-sensitive builds**.

`rustc` exposes `target-cpu` and `target-feature` codegen options. The language/reference surface exposes `cfg(target_feature)`. The standard library exposes runtime feature-detection macros like `is_x86_feature_detected!`. That means Rust is no longer missing the raw ability to tune for a CPU baseline, gate optimized paths, or dispatch at runtime.

But ordinary teams still do not have one boring artifact that answers the maintainer and downstream questions:

- what CPU baseline this binary or library actually promises,
- whether the build accidentally drifted toward host-specific tuning,
- which optimized paths require runtime detection and which are assumed unconditionally,
- whether a fallback implementation exists for each feature-gated path,
- and how likely a given release is to surprise users with an `illegal instruction` failure on older machines.

The missing crate is **not** another SIMD abstraction, compiler wrapper, or benchmark harness.

The missing crate is a **CPU baseline & runtime dispatch contract kit**: a crate and cargo-adjacent tool that turns “this release depends on certain CPU features” into a portable **baseline receipt, dispatch manifest, and support-risk bundle**.

# What it provides

- `cpu-contract.toml` — declares supported target triples, intended CPU baseline, allowed compile-time `target-feature` assumptions, runtime-detection policy, required fallback posture, and explicit “no fallback” exceptions.
- `cpu-baseline.receipt.json` — normalized record of observed `target-cpu`, explicit `target-feature` settings, relevant `cfg(target_feature)` facts, and produced artifacts.
- `runtime-dispatch.manifest.json` — lists optimized paths guarded by runtime detection, the fallback path expected for each one, and whether the fallback is present, partial, or intentionally absent.
- `cpu-support.report.json` — classifies the release as `portable_baseline_ok`, `runtime_dispatch_guarded`, `baseline_too_aggressive`, `feature_requires_fallback`, `host_tuned_release_risk`, `artifact_target_unknown`, or `manual_review_required`.
- `illegal-instruction.risk.json` — compact summary of where a downstream `SIGILL`-style failure is plausible and what support promise was made instead.
- `cargo cpu-contract snapshot` — capture one CPU baseline and dispatch bundle for a build.
- `cargo cpu-contract doctor` — explain whether the current build matches the declared hardware support policy.
- `cargo cpu-contract diff <old> <new>` — compare CPU support promises across releases, targets, or CI environments.
- `*.cpubundle.zip` — portable artifact for release notes, support tickets, downstream SDK consumers, and performance-portability review.

# What the crate should provide other people

1. **A boring answer to “what hardware baseline does this release actually support?”** instead of folklore or build-script tribal knowledge.
2. **A runtime-dispatch manifest** that says which optimized paths are guarded and whether each one has a fallback.
3. **A release-review artifact** that catches accidental host tuning before it becomes a downstream crash.
4. **A shared vocabulary** for CPU support promises across native binaries, Python extensions, Apple frameworks, and other Rust-built artifacts.
5. **A bridge** between low-level codegen knobs and honest downstream support contracts.

# Persona / who it’s for

- maintainers shipping native binaries to broad hardware fleets
- performance-sensitive crate authors using runtime dispatch or per-feature fast paths
- teams shipping Rust-built Python extensions or mobile/desktop SDKs
- support engineers triaging illegal-instruction or “works on one machine only” reports
- CI/release engineers reviewing cross-target portability promises

# Users & user stories

- **Release engineer**: “Show me whether this release accidentally picked a host-specific CPU baseline.”
- **Performance maintainer**: “Give me one artifact that proves every optimized path has a fallback or an explicit support exception.”
- **Support engineer**: “Tell me whether this customer crash is plausibly a CPU-feature mismatch rather than a general runtime bug.”
- **SDK consumer**: “Tell me what hardware assumptions this Rust-built native artifact actually makes.”

# Prior art (and why it’s insufficient)

- `rustc` codegen options expose the knobs, but not a boring support contract above them.
- `cfg(target_feature)` and runtime detection macros expose the mechanisms, but not a reviewable release artifact.
- The archive already has **P-0454 ABI Coherence Profile Kit**. That proposal is about **whole-program coherence of ABI-affecting flags**.
- The archive already has **P-0484 Toolchain & Target Support Contract Kit**. That proposal is about **toolchain/component/target support policy**.
- The archive already has **P-0482 SDK Release Promise Drift Kit**. That proposal is about **cross-language release promises once the artifact is already being shipped**.

What remains missing is the **CPU support contract** that answers: “what baseline, what dispatch guards, what fallback story, and what downstream crash risk?”

# Design goals

1. **Support-promise first** — center the downstream hardware promise, not just the compiler knobs.
2. **Dispatch-aware** — runtime-gated optimized paths and fallbacks must be visible.
3. **Accident-resistant** — catch host tuning and feature creep before release.
4. **Portable** — useful across binaries, native libraries, and Rust-built foreign artifacts.
5. **Conservative** — unknown CPU posture must stay visible.

# MVP surface

- Minimal types: `CpuContract`, `CpuBaselineReceipt`, `RuntimeDispatchManifest`, `CpuSupportReport`, `IllegalInstructionRiskReport`, `CpuContractDiff`, `CpuSupportBundle`
- Minimal functions:
  - `capture_cpu_baseline_receipt()`
  - `collect_runtime_dispatch_manifest()`
  - `classify_cpu_support()`
  - `evaluate_illegal_instruction_risk()`
  - `diff_cpu_support_bundles()`
- Feature flags:
  - `cargo`
  - `serde`
  - `x86`
  - `aarch64`
  - `markdown`

# Compatibility story

- Must remain useful whether projects use `target-cpu`, explicit `target-feature` flags, `cfg(target_feature)`, runtime detection macros, or a mixture.
- Must treat “compiled for the current machine” posture as reviewable risk for redistributable artifacts.
- Should work even when runtime dispatch is implemented in library code rather than build scripts.
- Must not assume every architecture exposes the same runtime-detection ergonomics.
- Should remain useful for foreign-language packaging workflows that need a hardware support promise without understanding all Rust internals.

# Conformance & fixtures

- one fixture with a conservative portable baseline and no runtime dispatch
- one fixture with guarded SIMD fast paths plus an explicit fallback implementation
- one fixture with accidental host-tuned release posture
- one fixture with a compile-time feature assumption but no fallback path
- goldens for `portable_baseline_ok`, `runtime_dispatch_guarded`, `baseline_too_aggressive`, `feature_requires_fallback`, and `host_tuned_release_risk`

# Path to boring stability

- Freeze the support and verdict vocabulary before architecture-specific expansion.
- Treat missing fallback paths as explicit output, not hidden technical debt.
- Start with baseline/dispatch artifacts before trying to infer performance value.
- Prefer release-review receipts over any attempt to auto-tune builds.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that read one CPU support contract, record the build’s actual baseline and feature assumptions, list runtime-dispatched fast paths and fallbacks, and emit a support-risk bundle warning when a release has drifted toward hardware-specific assumptions.

# De-risk plan

1. Start with x86/x86_64 because runtime feature detection and downstream expectations are clearest there.
2. Keep the verdict taxonomy small and conservative.
3. Validate one portable build, one runtime-dispatched build, and one intentionally host-tuned build.
4. Avoid becoming a benchmark framework or performance auto-tuner.

# Non-goals

- Not a new SIMD abstraction layer.
- Not a replacement for compiler codegen options.
- Not a performance benchmarking harness.
- Not a promise that the crate can infer every possible architecture-specific hazard.

# Architecture & API sketch

```rust
pub enum CpuSupportClass {
    PortableBaselineOk,
    RuntimeDispatchGuarded,
    BaselineTooAggressive,
    FeatureRequiresFallback,
    HostTunedReleaseRisk,
    ArtifactTargetUnknown,
    ManualReviewRequired,
}

pub fn capture_cpu_baseline_receipt(root: &Path, contract: &CpuContract) -> Result<CpuBaselineReceipt>;
pub fn collect_runtime_dispatch_manifest(root: &Path) -> Result<RuntimeDispatchManifest>;
pub fn classify_cpu_support(receipt: &CpuBaselineReceipt, manifest: &RuntimeDispatchManifest) -> CpuSupportReport;
pub fn evaluate_illegal_instruction_risk(report: &CpuSupportReport) -> IllegalInstructionRiskReport;
```

Bundle draft: `cpu-contract.toml`, `cpu-baseline.receipt.json`, `runtime-dispatch.manifest.json`, `cpu-support.report.json`, `illegal-instruction.risk.json`, `notes.md`.

# Security / safety model

- Treat environment- and artifact-path details as redactable support data.
- Do not claim portability that was not actually observed or declared.
- Make “host tuned” and “no fallback” postures impossible to hide.
- Prefer explicit support contracts over speculative inference.

# Maintenance & governance plan

- Track `rustc` codegen option docs and language/reference feature-detection surfaces closely.
- Keep the support vocabulary small and release-review oriented.
- Maintain fixtures for portable, guarded, and risky CPU-support postures.
- Add architecture-specific detail only when it sharpens downstream support review.

# Milestones

## 0.1
- CPU contract format
- baseline receipt capture
- runtime-dispatch manifest export
- support classification

## 0.2
- diff support
- redaction controls
- better release-note/support-bundle templates

## 0.3
- foreign-artifact adapters for wheel/framework release review
- architecture-family expansion
- richer support-policy presets

# Open questions

- What is the smallest support vocabulary that stays useful across binaries, libraries, and foreign-language native artifacts?
- How much of runtime dispatch can the crate infer mechanically versus requiring explicit annotations in the contract?
- Which architecture families should follow x86 first without overfitting the MVP to one platform?

# Sources

- `rustc` codegen `target-cpu`: https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu
- `rustc` codegen `target-feature`: https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature
- Rust reference `cfg(target_feature)`: https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature
- `is_x86_feature_detected!`: https://doc.rust-lang.org/std/macro.is_x86_feature_detected.html
